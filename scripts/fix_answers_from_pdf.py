"""
从PDF提取红色正确答案，替换到output_xigai_v9文件中。
策略简单直接：PDF中红色选项行 = 正确答案，按顺序匹配到每道选择题。
"""
import os, re, fitz
from collections import Counter, defaultdict

PROJECT = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(PROJECT, '..', '习概题库.pdf')
SRC_DIR = os.path.join(PROJECT, '..', 'output_xigai_v9')
OUT_DIR = os.path.join(PROJECT, '..', 'output_xigai_v10')


def extract_red_answers_from_pdf():
    """从PDF提取红色答案，按章节+题号组织"""
    doc = fitz.open(PDF_PATH)
    answers = defaultdict(dict)  # {chapter_idx: {q_number: answer}}

    current_chapter_idx = 0
    current_type = None
    q_counter = defaultdict(int)  # {type: count}

    # 章节切换：遇到 "一、单项选择题" 且是新的章节内容
    # 用单选题题号重置来判断

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text('dict')['blocks']

        for block in blocks:
            if 'lines' not in block:
                continue

            for line in block['lines']:
                # 收集行中的所有span
                black_text = ''
                red_text = ''
                for span in line['spans']:
                    is_red = (span['color'] & 0xFFFFFF) == 0xFF0000
                    if is_red:
                        red_text += span['text']
                    else:
                        black_text += span['text']

                full_text = (black_text + red_text).strip()
                if not full_text:
                    continue
                if full_text.startswith('爬取题库'):
                    continue

                # 检测题型
                if full_text.startswith('一、单项选择题'):
                    current_type = 'single'
                    continue
                elif full_text.startswith('二、多项选择题'):
                    current_type = 'multiple'
                    continue
                elif full_text.startswith('四、判断题'):
                    current_type = 'judge'
                    continue
                elif re.match(r'^[三五]、', full_text):
                    current_type = None  # 填空 or 简答
                    continue

                # 检测题目编号
                qm = re.match(r'^(\d+)\.', full_text)
                if qm:
                    q_num = int(qm.group(1))
                    if current_type:
                        q_counter[current_type] = q_num

                # 检测红色答案
                if red_text and current_type:
                    red_text = red_text.strip()
                    # 选择题答案: （X）xxx
                    opt_m = re.match(r'^（([A-G])）', red_text)
                    if opt_m and current_type in ('single', 'multiple'):
                        letter = opt_m.group(1)
                        key = (current_chapter_idx, current_type, q_counter.get(current_type, 0))
                        if key in answers:
                            # 多选：合并字母
                            old = answers[key]
                            answers[key] = ''.join(sorted(set(old + letter)))
                        else:
                            answers[key] = letter
                    # 判断题
                    elif '√' in red_text and current_type == 'judge':
                        key = (current_chapter_idx, 'judge', q_counter.get('judge', 0))
                        answers[key] = '√'
                    elif '×' in red_text and current_type == 'judge':
                        key = (current_chapter_idx, 'judge', q_counter.get('judge', 0))
                        answers[key] = '×'

    return answers


def main():
    print('📖 从PDF提取红色答案...')
    # 这个简单方法：直接扫描PDF中所有红色文字，找出答案模式

    doc = fitz.open(PDF_PATH)

    # 收集所有红色答案行（简化为：红色文本行中提取答案）
    red_answers_list = []  # [{type, answer, page}]

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text('dict')['blocks']

        for block in blocks:
            if 'lines' not in block:
                continue
            for line in block['lines']:
                red_text = ''
                for span in line['spans']:
                    if (span['color'] & 0xFFFFFF) == 0xFF0000:
                        red_text += span['text']

                red_text = red_text.strip()
                if not red_text:
                    continue

                # 选择题红色答案: (X)xxx
                m = re.match(r'^（([A-G])）', red_text)
                if m:
                    red_answers_list.append({
                        'type': 'choice',
                        'letter': m.group(1),
                        'page': page_num,
                    })
                elif '√' in red_text[:2]:
                    red_answers_list.append({
                        'type': 'judge',
                        'letter': '√',
                        'page': page_num,
                    })
                elif '×' in red_text[:2]:
                    red_answers_list.append({
                        'type': 'judge',
                        'letter': '×',
                        'page': page_num,
                    })

    print(f'  找到 {len(red_answers_list)} 个红色答案')

    # 读取V9文件，用红色答案替换
    sys.path.insert(0, os.path.join(PROJECT, '..', 'backend'))
    from routes.import_routes import parse_txt_file

    os.makedirs(OUT_DIR, exist_ok=True)

    # 按V9章节顺序匹配答案
    files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith('.txt') and f not in ('统计.txt', '异常清单.txt')])

    red_idx = 0  # 当前红色答案索引
    total_fixed = 0

    for fname in files:
        ch_name = fname.replace('.txt', '')
        old_qs = parse_txt_file(os.path.join(SRC_DIR, fname))

        # 为每道选择题和判断题匹配红色答案
        for q in old_qs:
            if q['type'] in ('single', 'multiple') and red_idx < len(red_answers_list):
                ra = red_answers_list[red_idx]
                if ra['type'] == 'choice':
                    old_answer = q.get('answer', '')
                    new_answer = ra['letter']
                    if old_answer != new_answer:
                        q['answer'] = new_answer
                        total_fixed += 1
                    red_idx += 1
            elif q['type'] == 'judge' and red_idx < len(red_answers_list):
                ra = red_answers_list[red_idx]
                if ra['type'] == 'judge':
                    old_answer = q.get('answer', '')
                    new_answer = ra['letter']
                    if old_answer != new_answer:
                        q['answer'] = new_answer
                        total_fixed += 1
                    red_idx += 1
            # 填空题暂时保持原答案

        # 写入V10
        filepath = os.path.join(OUT_DIR, fname)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f'{ch_name}\n')
            f.write('=' * 50 + '\n\n')
            for qtype, label in [('single', '单选题'), ('multiple', '多选题'),
                                  ('blank', '填空题'), ('judge', '判断题')]:
                qs = [q for q in old_qs if q['type'] == qtype]
                if not qs:
                    continue
                f.write(f'【{label}】（共{len(qs)}题）\n\n')
                for num, q in enumerate(qs, 1):
                    f.write(f'{num}. {q["content"]}\n')
                    if q.get('options'):
                        for opt in q['options']:
                            f.write(f' （{opt["key"]}）{opt["text"]}\n')
                    ans = q.get('answer', '')
                    if ans:
                        f.write(f' 答案：{ans}\n')
                    else:
                        f.write('\n')
                    f.write('\n')

        tc = dict(Counter(q['type'] for q in old_qs))
        has = sum(1 for q in old_qs if q.get('answer'))
        no = len(old_qs) - has
        status = 'OK' if no == 0 else f'WARN:{no}noans'
        print(f'  {ch_name}: {len(old_qs)}q {tc} -> {has}ans {status}')

    print(f'\n📊 修正了 {total_fixed} 道题的答案')
    print(f'  输出: {OUT_DIR}')


if __name__ == '__main__':
    import sys
    main()
