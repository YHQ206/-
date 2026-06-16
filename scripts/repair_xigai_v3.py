"""
重新生成干净的习概题库文件。
与repair_xigai.py不同，本脚本：
1. 优先从PDF提取干净的题目内容
2. 直接从output_xigai_v8继承答案
3. 对于PDF中缺失/无法提取的章节，使用output_xigai_v8的清理版本

策略：逐页扫描PDF，自动检测章节边界（题目编号重置 + 题型标题），
提取题目后与output_xigai_v8答案匹配。
"""
import os
import re
import sys
import PyPDF2

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(PROJECT_DIR, '..', '习概题库.pdf')
OLD_OUTPUT_DIR = os.path.join(PROJECT_DIR, '..', 'output_xigai_v8')
NEW_OUTPUT_DIR = os.path.join(PROJECT_DIR, '..', 'output_xigai_v9')

# 用第一道单选题的特征来识别章节
CHAPTER_SIGNATURES = [
    # (章节名, 第一道单选题的前几个字)
    ('导论', '通过了关于《中国共产党章程'),
    ('第1章', '中国特色社会主义道路是'),
    ('第2章', '是中华民族伟大复兴的形象表达'),
    ('第3章', '是符合中国国情'),
    ('第4章', '理想是一个民族'),
    ('第5章', '是"四个全面"战略布局'),
    ('第6章', '是根据我国发展阶段'),
    ('第7章', '科教兴国是我国'),
    ('第8章', '中国实行的社会主义民主政治'),
    ('第9章', '是推进全面依法治国的根本保证'),
    ('第10章', '文化的影响力首先是'),
    ('第11章', '在社会不同的发展阶段'),
    ('第12章', '提出："要像保护眼睛'),
    ('第13章', '党的十八大以来，习近平创造性提出'),
    ('第14章', '巩固提高一体化国家战略体系'),
    ('第15章', '"一国两制"构想的提出'),
    ('第16章', '提出，"当今世界正在经历'),
    ('第17章', '是新时代党的建设的根本方针'),
]


def extract_questions_by_chapter():
    """从PDF提取题目，按章节分组"""
    reader = PyPDF2.PdfReader(PDF_PATH)

    chapters = {}  # {chapter_name: [questions]}
    current_chapter = None
    current_type = None
    chapter_questions = []

    for page_num in range(len(reader.pages)):
        text = reader.pages[page_num].extract_text()
        text = re.sub(r'爬取题库.*?MadebyCWA\n?', '', text)
        text = re.sub(r'—\d+—', '', text)
        text = re.sub(r'\[WARNING:[^\]]*\]', '', text)

        lines = text.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # 检测章节切换：题目编号为1的单选题
            m = re.match(r'^1\.\s*(.+)', line)
            if m and current_type == 'single':
                q_first = m.group(1).strip()
                # 尝试匹配已知章节
                matched = None
                for ch_name, sig in CHAPTER_SIGNATURES:
                    if q_first.startswith(sig):
                        matched = ch_name
                        break

                if matched and matched != current_chapter:
                    # 保存上一章节
                    if current_chapter and chapter_questions:
                        chapters[current_chapter] = chapter_questions
                    # 开始新章节
                    current_chapter = matched
                    chapter_questions = []
                    # 继续用下面的逻辑解析这道题

            # 题型标题
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
                current_type = None
                i += 1
                continue

            if not current_type:
                i += 1
                continue

            # 题目行
            m = re.match(r'^(\d+)\.\s*(.+)', line)
            if not m:
                i += 1
                continue

            q_num = int(m.group(1))
            q_content_lines = [m.group(2).strip()]
            j = i + 1

            if current_type in ('single', 'multiple'):
                option_lines = []
                while j < len(lines):
                    nl = lines[j].strip()
                    if not nl:
                        j += 1
                        continue
                    if re.match(r'^\d+\.', nl):
                        break
                    if re.match(r'^[一二三四五六七八九十]、', nl):
                        break
                    if re.search(r'（[A-G]）', nl):
                        option_lines.append(nl)
                        j += 1
                    else:
                        q_content_lines.append(nl)
                        j += 1

                q_content = ' '.join(q_content_lines)
                q_content = re.sub(r'[\(（]\s*[\)）]', '', q_content)
                q_content = re.sub(r'\s+', ' ', q_content).strip()

                options = []
                all_opts = ' '.join(option_lines)
                for om in re.findall(r'（([A-G])）\s*(.+?)(?=（[A-G]）|$)', all_opts):
                    options.append({'key': om[0], 'text': om[1].strip()})

                chapter_questions.append({
                    'type': current_type,
                    'content': q_content,
                    'options': options,
                    'answer': '',
                })
                i = j - 1

            elif current_type == 'blank':
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

                chapter_questions.append({
                    'type': 'blank',
                    'content': q_content,
                    'options': None,
                    'answer': '',
                })
                i = j - 1

            elif current_type == 'judge':
                answer = ''
                all_text = ' '.join(q_content_lines)
                if '（√）' in all_text:
                    answer = '√'
                    q_content_lines = [l.replace('（√）', '') for l in q_content_lines]
                elif '（×）' in all_text:
                    answer = '×'
                    q_content_lines = [l.replace('（×）', '') for l in q_content_lines]

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

                chapter_questions.append({
                    'type': 'judge',
                    'content': q_content,
                    'options': None,
                    'answer': answer,
                })
                i = j - 1

            i += 1

    # 保存最后一章
    if current_chapter and chapter_questions:
        chapters[current_chapter] = chapter_questions

    return chapters


def load_answers():
    """从output_xigai_v8加载答案"""
    sys.path.insert(0, os.path.join(PROJECT_DIR, '..', 'backend'))
    from routes.import_routes import parse_txt_file

    answers = {}
    for fname in sorted(os.listdir(OLD_OUTPUT_DIR)):
        if not fname.endswith('.txt') or fname in ('统计.txt', '异常清单.txt'):
            continue
        ch_name = fname.replace('.txt', '')
        qs = parse_txt_file(os.path.join(OLD_OUTPUT_DIR, fname))
        ch_answers = {'single': [], 'multiple': [], 'blank': [], 'judge': []}
        for q in qs:
            ch_answers[q['type']].append(q['answer'])
        answers[ch_name] = ch_answers
    return answers


def main():
    print('📖 从PDF提取题目...')
    pdf_chapters = extract_questions_by_chapter()
    print(f'  提取了 {len(pdf_chapters)} 个章节')
    for ch, qs in pdf_chapters.items():
        from collections import Counter
        print(f'    {ch}: {len(qs)}题 {dict(Counter(q["type"] for q in qs))}')

    print('\n📋 加载答案...')
    old_answers = load_answers()

    # 对于PDF中有提取的章节，使用PDF内容
    # 对于PDF中没有的章节，使用output_xigai_v8的parse_txt_file结果
    sys.path.insert(0, os.path.join(PROJECT_DIR, '..', 'backend'))
    from routes.import_routes import parse_txt_file

    os.makedirs(NEW_OUTPUT_DIR, exist_ok=True)

    # 获取所有已知章节
    all_chapters = set(list(pdf_chapters.keys()) + list(old_answers.keys()))

    total_with_ans = 0
    total_without = 0

    for ch_name in sorted(all_chapters):
        if ch_name in pdf_chapters:
            # 使用PDF内容 + old answers
            questions = pdf_chapters[ch_name]
            ch_ans = old_answers.get(ch_name, {})
            for qtype in ['single', 'multiple', 'blank', 'judge']:
                type_qs = [q for q in questions if q['type'] == qtype]
                type_ans = ch_ans.get(qtype, [])
                for idx, q in enumerate(type_qs):
                    if idx < len(type_ans) and type_ans[idx]:
                        q['answer'] = type_ans[idx]
        else:
            # 使用old内容（已经是干净的parse结果）
            fpath = os.path.join(OLD_OUTPUT_DIR, f'{ch_name}.txt')
            if os.path.exists(fpath):
                questions = parse_txt_file(fpath)
            else:
                continue

        # 写入文件
        filepath = os.path.join(NEW_OUTPUT_DIR, f'{ch_name}.txt')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f'{ch_name}\n')
            f.write('=' * 50 + '\n\n')

            for qtype, label in [('single', '单选题'), ('multiple', '多选题'),
                                  ('blank', '填空题'), ('judge', '判断题')]:
                qs = [q for q in questions if q['type'] == qtype]
                if not qs:
                    continue
                f.write(f'【{label}】（共{len(qs)}题）\n\n')
                for num, q in enumerate(qs, 1):
                    f.write(f'{num}. {q["content"]}\n')
                    if q.get('options'):
                        for opt in q['options']:
                            f.write(f' （{opt["key"]}）{opt["text"]}\n')
                    if q.get('answer'):
                        f.write(f' 答案：{q["answer"]}\n')
                    else:
                        f.write('\n')
                    f.write('\n')

        has = sum(1 for q in questions if q.get('answer'))
        no = len(questions) - has
        total_with_ans += has
        total_without += no

        from collections import Counter
        tc = dict(Counter(q['type'] for q in questions))
        status = '✅' if no == 0 else f'⚠️ {no}无答案'
        print(f'  {ch_name}: {len(questions)}题 {tc} {status}')

    print(f'\n📊 总计: {total_with_ans + total_without}题, {total_with_ans}有答案, {total_without}无答案')
    print(f'  输出: {NEW_OUTPUT_DIR}')


if __name__ == '__main__':
    main()
