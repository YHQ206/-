"""
从原始PDF重新提取习概题库 V2。

策略：从PDF解析所有题目（顺序排列），按output_xigai_v8/统计.txt的题目数
分割为章节，再用output_xigai_v8的答案匹配。
"""
import os
import re
import sys
import PyPDF2

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(PROJECT_DIR, '..', '习概题库.pdf')
OLD_OUTPUT_DIR = os.path.join(PROJECT_DIR, '..', 'output_xigai_v8')
NEW_OUTPUT_DIR = os.path.join(PROJECT_DIR, '..', 'output_xigai_v9')

# 从统计.txt读取每章节的期望题目数
EXPECTED_COUNTS = [
    # (章节名, single, multiple, blank, judge) — 不含简答题
    # 从output_xigai_v8/统计.txt
]

def load_expected_counts():
    """从output_xigai_v8/统计.txt读取期望题目数"""
    stat_file = os.path.join(OLD_OUTPUT_DIR, '统计.txt')
    if not os.path.exists(stat_file):
        print('统计.txt not found, using hardcoded counts')
        return [
            ('导论', 63, 2, 2, 2),
            ('第1章', 42, 5, 5, 5),
            ('第2章', 43, 3, 2, 4),
            ('第3章', 40, 0, 0, 0),
            ('第4章', 10, 2, 2, 4),
            ('第5章', 45, 9, 3, 6),
            ('第6章', 52, 12, 6, 11),
            ('第7章', 41, 0, 0, 0),
            ('第8章', 70, 16, 15, 14),
            ('第9章', 29, 3, 0, 0),
            ('第10章', 36, 19, 18, 15),
            ('第11章', 20, 14, 14, 12),
            ('第12章', 25, 14, 13, 11),
            ('第13章', 25, 0, 0, 0),
            ('第14章', 13, 0, 0, 0),
            ('第15章', 71, 14, 14, 11),
        ]

    chapters = []
    with open(stat_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            m = re.match(r'^\s*(导论|第\d+章):\s*(.+)', line)
            if m:
                name = m.group(1)
                rest = m.group(2)
                counts = {'single': 0, 'multiple': 0, 'blank': 0, 'judge': 0}
                for part in rest.split(','):
                    part = part.strip()
                    kv = part.split(':')
                    if len(kv) == 2:
                        key = kv[0].strip()
                        val = int(kv[1].strip())
                        type_map = {'单选题': 'single', '多选题': 'multiple',
                                    '填空题': 'blank', '判断题': 'judge'}
                        if key in type_map:
                            counts[type_map[key]] = val
                chapters.append((name, counts['single'], counts['multiple'],
                                counts['blank'], counts['judge']))
    return chapters


def extract_all_questions():
    """从PDF提取所有题目（按PDF中的出现顺序）"""
    reader = PyPDF2.PdfReader(PDF_PATH)

    all_questions = []  # [{type, content, options, answer}]
    current_type = None

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

                all_questions.append({
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

                all_questions.append({
                    'type': 'blank',
                    'content': q_content,
                    'options': None,
                    'answer': '',
                })
                i = j - 1

            elif current_type == 'judge':
                answer = ''
                if '（√）' in ' '.join(q_content_lines):
                    answer = '√'
                    q_content_lines = [l.replace('（√）', '') for l in q_content_lines]
                elif '（×）' in ' '.join(q_content_lines):
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

                all_questions.append({
                    'type': 'judge',
                    'content': q_content,
                    'options': None,
                    'answer': answer,
                })
                i = j - 1

            i += 1

    return all_questions


def load_answers_from_old():
    """从output_xigai_v8加载答案"""
    sys.path.insert(0, os.path.join(PROJECT_DIR, '..', 'backend'))
    from routes.import_routes import parse_txt_file

    all_answers = {}  # {chapter_name: {type: [answer1, answer2, ...]}}

    for fname in sorted(os.listdir(OLD_OUTPUT_DIR)):
        if not fname.endswith('.txt'):
            continue
        if fname in ('统计.txt', '异常清单.txt'):
            continue

        ch_name = fname.replace('.txt', '')
        filepath = os.path.join(OLD_OUTPUT_DIR, fname)
        questions = parse_txt_file(filepath)

        ch_answers = {'single': [], 'multiple': [], 'blank': [], 'judge': []}
        for q in questions:
            ch_answers[q['type']].append(q['answer'])

        all_answers[ch_name] = ch_answers

    return all_answers


def main():
    print('📖 从PDF提取所有题目...')
    all_qs = extract_all_questions()
    print(f'  共提取 {len(all_qs)} 题')

    # 按类型计数
    from collections import Counter
    print(f'  类型: {Counter(q["type"] for q in all_qs)}')

    print('\n📋 加载答案...')
    old_answers = load_answers_from_old()
    print(f'  加载了 {len(old_answers)} 个章节')

    print('\n📊 加载期望题目数...')
    chapters = load_expected_counts()

    # 按期望题目数分割
    os.makedirs(NEW_OUTPUT_DIR, exist_ok=True)

    q_idx = 0  # 当前在all_qs中的位置
    stats = []

    for ch_name, exp_sc, exp_mc, exp_bl, exp_ju in chapters:
        ch_questions = []

        for qtype, exp_count in [('single', exp_sc), ('multiple', exp_mc),
                                  ('blank', exp_bl), ('judge', exp_ju)]:
            for _ in range(exp_count):
                if q_idx < len(all_qs):
                    q = all_qs[q_idx]
                    # 类型匹配检查
                    if q['type'] == qtype:
                        ch_questions.append(q)
                        q_idx += 1
                    else:
                        # 类型不匹配，尝试在前面或后面找
                        print(f'  ⚠️ {ch_name} [{qtype}]: expected type at pos {q_idx}, got {q["type"]}')
                        # 跳过不匹配的题目
                        found = False
                        for offset in range(1, 20):
                            if q_idx + offset < len(all_qs) and all_qs[q_idx + offset]['type'] == qtype:
                                # 跳过了offset道不同类型的题
                                skipped = all_qs[q_idx:q_idx + offset]
                                print(f'     skipped {len(skipped)} questions of types {[s["type"] for s in skipped]}')
                                q_idx += offset
                                ch_questions.append(all_qs[q_idx])
                                q_idx += 1
                                found = True
                                break
                        if not found:
                            print(f'     ❌ cannot find {qtype} question!')

        # 匹配答案
        ch_answers = old_answers.get(ch_name, {})
        for qtype in ['single', 'multiple', 'blank', 'judge']:
            type_qs = [q for q in ch_questions if q['type'] == qtype]
            type_ans = ch_answers.get(qtype, [])
            for idx, q in enumerate(type_qs):
                if idx < len(type_ans) and type_ans[idx]:
                    q['answer'] = type_ans[idx]

        # 写入文件
        filepath = os.path.join(NEW_OUTPUT_DIR, f'{ch_name}.txt')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f'{ch_name}\n')
            f.write('=' * 50 + '\n\n')

            for qtype, label in [('single', '单选题'), ('multiple', '多选题'),
                                  ('blank', '填空题'), ('judge', '判断题')]:
                qs = [q for q in ch_questions if q['type'] == qtype]
                if not qs:
                    continue
                f.write(f'【{label}】（共{len(qs)}题）\n\n')
                for num, q in enumerate(qs, 1):
                    f.write(f'{num}. {q["content"]}\n')
                    if q['options']:
                        for opt in q['options']:
                            f.write(f' （{opt["key"]}）{opt["text"]}\n')
                    if q['answer']:
                        f.write(f' 答案：{q["answer"]}\n')
                    else:
                        f.write('\n')
                    f.write('\n')

        type_counts = Counter(q['type'] for q in ch_questions)
        has_ans = sum(1 for q in ch_questions if q['answer'])
        no_ans = len(ch_questions) - has_ans
        status = f'✅' if no_ans == 0 else f'⚠️ {no_ans}无答案'
        print(f'  {ch_name}: {len(ch_questions)}题 ({dict(type_counts)}) {status}')

        stats.append({'chapter': ch_name, 'total': len(ch_questions),
                      'has_answer': has_ans, 'no_answer': no_ans})

    # 汇总
    total = sum(s['total'] for s in stats)
    total_ans = sum(s['has_answer'] for s in stats)
    total_no = sum(s['no_answer'] for s in stats)
    print(f'\n{"="*60}')
    print(f'📊 汇总: {total}题, {total_ans}有答案, {total_no}无答案')
    print(f'  剩余未匹配: {len(all_qs) - q_idx}题 (PDF中有但不在统计中)')
    print(f'  输出目录: {NEW_OUTPUT_DIR}')

    # 统计文件
    stat_path = os.path.join(NEW_OUTPUT_DIR, '统计.txt')
    with open(stat_path, 'w', encoding='utf-8') as f:
        f.write('=' * 50 + '\n提取统计\n' + '=' * 50 + '\n\n')
        for s in stats:
            f.write(f' {s["chapter"]}\n')
        f.write(f'\n合计: {total}题\n')


if __name__ == '__main__':
    main()
