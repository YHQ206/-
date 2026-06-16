"""
从原始PDF重新提取习概题库，生成干净的TXT文件。

PDF中的题目文本干净，但没有选择题和填空题的答案。
output_xigai_v8 文件中有答案但内容损坏。
本脚本合并两者：从PDF取干净内容 + 从output_xigai_v8取答案。
"""
import os
import re
import sys
import PyPDF2
from collections import OrderedDict

# 项目路径
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(PROJECT_DIR, '..', '习概题库.pdf')
OLD_OUTPUT_DIR = os.path.join(PROJECT_DIR, '..', 'output_xigai_v8')
NEW_OUTPUT_DIR = os.path.join(PROJECT_DIR, '..', 'output_xigai_v9')

# TOC页码 → 实际PDF页面索引映射（经过扫描验证）
CHAPTERS = [
    ('导论', 1),
    ('第1章', 8),
    ('第2章', 14),
    ('第3章', 19),
    ('第4章', 23),
    ('第5章', 25),
    ('第6章', 30),
    ('第7章', 37),
    ('第8章', 41),
    ('第9章', 52),
    ('第10章', 55),
    ('第11章', 61),
    ('第12章', 66),
    ('第13章', 71),
    ('第14章', 74),
    ('第15章', 75),
    ('第16章', 81),
    ('第17章', 84),
]


def extract_text_from_pdf(pdf_path):
    """从PDF提取纯文本，去掉页眉、页码、水印"""
    reader = PyPDF2.PdfReader(pdf_path)
    all_text = []
    for page in reader.pages:
        text = page.extract_text()
        # 去页眉
        text = re.sub(r'爬取题库.*?MadebyCWA\n?', '', text)
        # 去页码标记 —N—
        text = re.sub(r'—\d+—', '', text)
        # 去水印
        text = re.sub(r'\[WARNING:[^\]]*\]', '', text)
        # 合并多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        all_text.append(text)
    return all_text


def get_page_range_for_chapter(ch_idx, total_pages):
    """根据TOC页码计算一个章节的PDF页面范围（0-indexed）"""
    _, start_page_1based = CHAPTERS[ch_idx]
    # TOC在第1页（index 0），内容从第2页（index 1）开始
    # TOC页码需要 +0 或 +1 偏移（因为TOC占一页）
    start_0based = start_page_1based  # 直接使用TOC页码作为0-index

    if ch_idx + 1 < len(CHAPTERS):
        _, next_start = CHAPTERS[ch_idx + 1]
        end_0based = next_start  # 下一章开始的前一页
    else:
        end_0based = total_pages

    return start_0based, end_0based


def parse_questions_from_text(text):
    """从文本中解析题目列表"""
    questions = []  # [{type, number, content, options, answer}]
    lines = text.split('\n')

    current_type = None
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # 识别题型
        if re.match(r'^一、单项选择题', line):
            current_type = 'single'
            i += 1
            continue
        elif re.match(r'^二、多项选择题', line):
            current_type = 'multiple'
            i += 1
            continue
        elif re.match(r'^三、填空题', line):
            current_type = 'blank'
            i += 1
            continue
        elif re.match(r'^四、判断题', line):
            current_type = 'judge'
            i += 1
            continue
        elif re.match(r'^[五六七八九十]、', line):
            # 简答题/论述题等，停止收集
            current_type = None
            i += 1
            continue

        if not current_type:
            i += 1
            continue

        # 解析题目
        m = re.match(r'^(\d+)\.\s*(.+)', line)
        if not m:
            i += 1
            continue

        q_num = int(m.group(1))
        q_content_lines = [m.group(2).strip()]

        j = i + 1

        if current_type in ('single', 'multiple'):
            # 选择题：收集题目续行 + 选项行
            option_lines = []
            while j < len(lines):
                nl = lines[j].strip()
                if not nl:
                    j += 1
                    continue
                # 下一题
                if re.match(r'^\d+\.', nl):
                    break
                # 新题型
                if re.match(r'^[一二三四五六七八九十]、', nl):
                    break
                # 选项行：包含（A）（B）等
                if re.search(r'（[A-G]）', nl):
                    option_lines.append(nl)
                    j += 1
                else:
                    # 题目续行
                    q_content_lines.append(nl)
                    j += 1

            # 合并题目内容
            q_content = ' '.join(q_content_lines)
            # 移除题干中的空括号
            q_content = re.sub(r'[\(（]\s*[\)）]', '', q_content)
            q_content = re.sub(r'\s+', ' ', q_content).strip()

            # 从选项行提取选项
            options = []
            all_opts_text = ' '.join(option_lines)
            opt_matches = re.findall(r'（([A-G])）\s*(.+?)(?=（[A-G]）|$)', all_opts_text)
            for om in opt_matches:
                opt_text = om[1].strip()
                options.append({'key': om[0], 'text': opt_text})

            questions.append({
                'type': current_type,
                'number': q_num,
                'content': q_content,
                'options': options,
                'answer': ''  # 稍后从output_xigai_v8匹配
            })

            i = j - 1

        elif current_type == 'blank':
            # 填空题：收集题目续行（没有选项）
            while j < len(lines):
                nl = lines[j].strip()
                if not nl:
                    j += 1
                    continue
                if re.match(r'^\d+\.', nl):
                    break
                if re.match(r'^[一二三四五六七八九十]、', nl):
                    break
                q_content_lines.append(nl)
                j += 1

            q_content = ' '.join(q_content_lines)
            q_content = re.sub(r'\s+', ' ', q_content).strip()

            questions.append({
                'type': 'blank',
                'number': q_num,
                'content': q_content,
                'options': None,
                'answer': ''
            })

            i = j - 1

        elif current_type == 'judge':
            # 判断题：可能有内联答案（√）（×）
            answer = ''
            # 检查内联答案
            if '（√）' in ' '.join(q_content_lines):
                answer = '√'
                q_content_lines = [l.replace('（√）', '') for l in q_content_lines]
            elif '（×）' in ' '.join(q_content_lines):
                answer = '×'
                q_content_lines = [l.replace('（×）', '') for l in q_content_lines]

            # 收集题目续行
            while j < len(lines):
                nl = lines[j].strip()
                if not nl:
                    j += 1
                    continue
                if re.match(r'^\d+\.', nl):
                    break
                if re.match(r'^[一二三四五六七八九十]、', nl):
                    break
                if '（√）' in nl:
                    answer = '√'
                    nl = nl.replace('（√）', '')
                if '（×）' in nl:
                    answer = '×'
                    nl = nl.replace('（×）', '')
                q_content_lines.append(nl)
                j += 1

            q_content = ' '.join(q_content_lines)
            q_content = re.sub(r'\s+', ' ', q_content).strip()

            questions.append({
                'type': 'judge',
                'number': q_num,
                'content': q_content,
                'options': None,
                'answer': answer
            })

            i = j - 1

        i += 1

    return questions


def load_answers_from_old(chapter_name):
    """从output_xigai_v8加载答案（按题型和题号组织）"""
    filepath = os.path.join(OLD_OUTPUT_DIR, f'{chapter_name}.txt')
    if not os.path.exists(filepath):
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    answers = {}  # {type: {number: answer}}
    lines = content.split('\n')
    current_type = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if '单选题' in line:
            current_type = 'single'
            continue
        elif '多选题' in line:
            current_type = 'multiple'
            continue
        elif '填空题' in line:
            current_type = 'blank'
            continue
        elif '判断题' in line:
            current_type = 'judge'
            continue
        elif '简答题' in line:
            current_type = None
            continue

        # 解析答案行
        if current_type:
            ans_m = re.search(r'答案[：:]\s*(.+)', line)
            if ans_m:
                # 找到对应的题号
                num_m = re.match(r'^(\d+)\.?\s', line)
                if not num_m:
                    # 答案可能在上一行的题目中，找前面的题号
                    pass
                # 简单方法：顺序解析
                ans_val = ans_m.group(1).strip()
                if current_type not in answers:
                    answers[current_type] = {}
                # 用顺序编号
                idx = len(answers[current_type]) + 1
                answers[current_type][idx] = ans_val

    return answers


def load_all_answers_from_old():
    """从output_xigai_v8全部文件加载答案（按题号在章节内唯一编号）"""
    # 直接解析每个文件的parse_txt_file结果
    sys.path.insert(0, os.path.join(PROJECT_DIR, '..', 'backend'))
    from routes.import_routes import parse_txt_file as old_parse

    all_answers = {}  # {chapter_name: {type: [answer1, answer2, ...]}}

    for fname in sorted(os.listdir(OLD_OUTPUT_DIR)):
        if not fname.endswith('.txt'):
            continue
        if fname in ('统计.txt', '异常清单.txt'):
            continue

        ch_name = fname.replace('.txt', '')
        filepath = os.path.join(OLD_OUTPUT_DIR, fname)
        questions = old_parse(filepath)

        ch_answers = {'single': {}, 'multiple': {}, 'blank': {}, 'judge': {}}
        for q in questions:
            qtype = q['type']
            # 用当前类型的计数作为题号
            count = len(ch_answers[qtype]) + 1
            ch_answers[qtype][count] = q['answer']

        all_answers[ch_name] = ch_answers

    return all_answers


def write_clean_output(chapter_name, questions):
    """将清理后的题目写入输出文件"""
    os.makedirs(NEW_OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(NEW_OUTPUT_DIR, f'{chapter_name}.txt')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f'{chapter_name}\n')
        f.write('=' * 50 + '\n\n')

        for qtype, type_label, type_name in [
            ('single', '单选题', '单项选择题'),
            ('multiple', '多选题', '多项选择题'),
            ('blank', '填空题', '填空题'),
            ('judge', '判断题', '判断题')
        ]:
            qs = [q for q in questions if q['type'] == qtype]
            if not qs:
                continue

            f.write(f'【{type_label}】（共{len(qs)}题）\n\n')

            for q in qs:
                f.write(f'{q["number"]}. {q["content"]}\n')

                if q['options']:
                    for opt in q['options']:
                        f.write(f' （{opt["key"]}）{opt["text"]}\n')

                if q['answer']:
                    f.write(f' 答案：{q["answer"]}\n')
                else:
                    f.write(f'\n')

                f.write('\n')

    return filepath


def main():
    print('📖 读取原始PDF...')
    pages = extract_text_from_pdf(PDF_PATH)
    total_pages = len(pages)
    print(f'  共 {total_pages} 页')

    print('📋 加载答案...')
    old_answers = load_all_answers_from_old()
    print(f'  加载了 {len(old_answers)} 个章节的答案')

    # 需要处理的章节（考试范围 + 所有章节）
    target_chapters = [ch[0] for ch in CHAPTERS]

    stats = []

    for ch_idx, (ch_name, _) in enumerate(CHAPTERS):
        start_pg, end_pg = get_page_range_for_chapter(ch_idx, total_pages)

        # 提取该章节的所有页面文本
        ch_text = ''
        for pg in range(start_pg, min(end_pg, total_pages)):
            ch_text += pages[pg] + '\n'

        if not ch_text.strip():
            print(f'  ⚠️ {ch_name}: 无内容（页码范围 {start_pg+1}-{end_pg}）')
            continue

        # 解析题目
        questions = parse_questions_from_text(ch_text)

        if not questions:
            print(f'  ⚠️ {ch_name}: 解析出0题')
            continue

        # 匹配答案
        ch_answers = old_answers.get(ch_name, {})
        for qtype in ['single', 'multiple', 'blank', 'judge']:
            type_answers = ch_answers.get(qtype, {})
            type_qs = [q for q in questions if q['type'] == qtype]
            for idx, q in enumerate(type_qs):
                ans_key = idx + 1  # 答案按1-based编号
                if ans_key in type_answers and type_answers[ans_key]:
                    q['answer'] = type_answers[ans_key]

        # 写入文件
        filepath = write_clean_output(ch_name, questions)

        type_counts = {}
        has_ans = 0
        no_ans = 0
        for q in questions:
            type_counts[q['type']] = type_counts.get(q['type'], 0) + 1
            if q['answer']:
                has_ans += 1
            else:
                no_ans += 1

        status = f'✅ {has_ans}有答案' if no_ans == 0 else f'⚠️ {no_ans}无答案'
        print(f'  {ch_name}: {len(questions)}题 ({type_counts}) {status}')

        stats.append({
            'chapter': ch_name,
            'total': len(questions),
            'types': type_counts,
            'has_answer': has_ans,
            'no_answer': no_ans
        })

    # 汇总
    print(f'\n{"="*60}')
    print(f'📊 汇总')
    total_q = sum(s['total'] for s in stats)
    total_ans = sum(s['has_answer'] for s in stats)
    total_no = sum(s['no_answer'] for s in stats)
    print(f'  题目总数: {total_q}')
    print(f'  有答案: {total_ans}')
    print(f'  无答案: {total_no}')
    print(f'  输出目录: {NEW_OUTPUT_DIR}')

    # 生成统计文件
    stat_path = os.path.join(NEW_OUTPUT_DIR, '统计.txt')
    with open(stat_path, 'w', encoding='utf-8') as f:
        f.write('=' * 50 + '\n')
        f.write('提取统计\n')
        f.write('=' * 50 + '\n\n')
        for s in stats:
            types_str = ', '.join(f'{k}:{v}' for k, v in s['types'].items())
            f.write(f' {s["chapter"]}: {types_str}\n')
        f.write(f'\n 合计: {total_q}题, 有答案{total_ans}, 无答案{total_no}\n')

    print(f'\n✅ 完成！输出目录: {NEW_OUTPUT_DIR}')


if __name__ == '__main__':
    main()
