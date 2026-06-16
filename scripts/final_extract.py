"""
最终版：get_text('text') 取干净内容 + get_text('dict') 取红色答案。
"""
import os, re, fitz
from collections import Counter

PDF = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '习概题库.pdf')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output_xigai_v10')


def get_clean_text_and_red_answers(doc):
    """逐页提取：clean文本 + 红色答案列表"""
    all_text = ''
    red_answers = []  # [{letter, page, approx_position}]

    for pg in range(len(doc)):
        page = doc[pg]

        # Clean text (no color)
        text = page.get_text('text')
        # Remove header/footer
        text = re.sub(r'爬取题库.*?Made by CWA\n?', '', text)
        text = re.sub(r'^— \d+ —$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\[WARNING:[^\]]*\]\n?', '', text)
        all_text += text + '\n'

        # Red answers from dict extraction
        blocks = page.get_text('dict')['blocks']
        for block in blocks:
            if 'lines' not in block:
                continue
            for line in block['lines']:
                red = ''
                for s in line['spans']:
                    if (s['color'] & 0xFFFFFF) == 0xFF0000:
                        red += s['text']
                red = red.strip()
                if not red:
                    continue
                m = re.match(r'^（([A-G])）', red)
                if m:
                    red_answers.append(m.group(1))
                elif red == '√':
                    red_answers.append('√')
                elif red == '×':
                    red_answers.append('×')

    return all_text, red_answers


def parse_clean_text(text, red_answers):
    """从clean文本解析题目，匹配红色答案"""
    lines = text.split('\n')
    questions = []
    current_type = None
    red_idx = 0
    i = 0

    # 预处理：合并跨行的题目内容
    # 先收集所有有效行
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('—') or 'WARNING' in line:
            continue
        clean_lines.append(line)

    i = 0
    while i < len(clean_lines):
        line = clean_lines[i]

        # 题型标题
        if line.startswith('一、单项选择题'):
            current_type = 'single'
            i += 1
            continue
        elif line.startswith('二、多项选择题'):
            current_type = 'multiple'
            i += 1
            continue
        elif line.startswith('三、填空题'):
            current_type = 'blank'
            i += 1
            continue
        elif line.startswith('四、判断题'):
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

        # 题目行: "N." 或 "N. xxx" 或 "N.__________xxx"
        m = re.match(r'^(\d+)\.\s*(.*)', line)
        if not m:
            i += 1
            continue

        q_num = int(m.group(1))
        q_start = m.group(2)

        # 如果题号后没有内容，从下一行取
        if not q_start and i + 1 < len(clean_lines):
            i += 1
            q_start = clean_lines[i]

        if current_type in ('single', 'multiple'):
            # 收集题目内容和选项
            content_parts = [q_start]
            option_lines = []
            j = i + 1

            while j < len(clean_lines):
                nl = clean_lines[j]
                if re.match(r'^\d+\.\s', nl) or re.match(r'^[一二三四五六七八九十]、', nl):
                    break
                if re.match(r'^（[A-G]）', nl):
                    option_lines.append(nl)
                    j += 1
                else:
                    content_parts.append(nl)
                    j += 1

            # 合并内容
            content = ''.join(content_parts).replace('__________', '____')
            content = re.sub(r'\s+', '', content)

            # 提取选项
            options = []
            for ol in option_lines:
                om = re.match(r'^（([A-G])）\s*(.+)', ol)
                if om:
                    key = om.group(1)
                    if key not in [o['key'] for o in options]:
                        options.append({'key': key, 'text': om.group(2).strip()})

            # 答案：从红字列表取
            answer = ''
            if current_type == 'single' and red_idx < len(red_answers):
                a = red_answers[red_idx]
                if a not in ('√', '×'):
                    answer = a
                    red_idx += 1
            elif current_type == 'multiple' and red_idx < len(red_answers):
                # 多选题可能有多个红字答案
                while red_idx < len(red_answers):
                    a = red_answers[red_idx]
                    if a in ('√', '×'):
                        break
                    answer = ''.join(sorted(set(answer + a)))
                    red_idx += 1
                    # Check if next is for a different question
                    if red_idx < len(red_answers) and red_answers[red_idx] in ('√', '×'):
                        break
                    # Simple heuristic: stop if we have enough letters
                    if len(answer) >= 2:
                        break

            questions.append({
                'type': current_type,
                'content': content,
                'options': options,
                'answer': answer,
            })
            i = j - 1

        elif current_type == 'blank':
            content_parts = [q_start]
            j = i + 1
            while j < len(clean_lines):
                nl = clean_lines[j]
                if re.match(r'^\d+\.\s', nl) or re.match(r'^[一二三四五六七八九十]、', nl):
                    break
                content_parts.append(nl)
                j += 1

            content = ''.join(content_parts)
            content = re.sub(r'\s+', '', content)
            content = content.replace('__________', '____')

            questions.append({
                'type': 'blank',
                'content': content,
                'options': None,
                'answer': '',  # 填空题红字答案需另外处理
            })
            i = j - 1

        elif current_type == 'judge':
            content_parts = [q_start]
            j = i + 1
            answer = ''
            while j < len(clean_lines):
                nl = clean_lines[j]
                if re.match(r'^\d+\.\s', nl) or re.match(r'^[一二三四五六七八九十]、', nl):
                    break
                content_parts.append(nl)
                j += 1

            content = ''.join(content_parts)
            content = re.sub(r'\s+', '', content)
            content = content.replace('（√）', '').replace('（×）', '')

            # 红字答案
            if red_idx < len(red_answers) and red_answers[red_idx] in ('√', '×'):
                answer = red_answers[red_idx]
                red_idx += 1

            questions.append({
                'type': 'judge',
                'content': content,
                'options': None,
                'answer': answer,
            })
            i = j - 1

        i += 1

    return questions


def split_chapters(questions):
    """按预计题目数分章节"""
    spec = [
        ('导论',      63, 2,  2,  2),
        ('第1章',     42, 5,  5,  5),
        ('第2章',     43, 3,  2,  4),
        ('第3章',     40, 0,  0,  0),
        ('第4章',     10, 2,  2,  4),
        ('第5章',     45, 9,  3,  6),
        ('第6章',     52, 12, 6,  11),
        ('第7章',     41, 0,  0,  0),
        ('第8章',     70, 16, 15, 14),
        ('第9章',     29, 3,  0,  0),
        ('第10章',    36, 19, 18, 15),
        ('第11章',    20, 14, 14, 12),
        ('第12章',    25, 14, 13, 11),
        ('第13章',    25, 0,  0,  0),
        ('第14章',    13, 0,  0,  0),
        ('第15章',    71, 14, 14, 11),
    ]
    chapters = {}
    qi = 0
    for ch, sc, mc, bl, ju in spec:
        ch_qs = []
        for qt, cnt in [('single', sc), ('multiple', mc), ('blank', bl), ('judge', ju)]:
            taken = 0
            while taken < cnt and qi < len(questions):
                if questions[qi]['type'] == qt:
                    ch_qs.append(questions[qi])
                    taken += 1
                qi += 1
        chapters[ch] = ch_qs
    return chapters


def main():
    doc = fitz.open(PDF)
    print('Extracting...')
    text, red = get_clean_text_and_red_answers(doc)
    print(f'Text: {len(text)} chars, Red answers: {len(red)}')

    questions = parse_clean_text(text, red)
    print(f'Parsed: {len(questions)} questions')
    tc = dict(Counter(q['type'] for q in questions))
    ans = sum(1 for q in questions if q['answer'])
    print(f'Types: {tc}, with answers: {ans}')

    chapters = split_chapters(questions)

    os.makedirs(OUT, exist_ok=True)
    total, total_ans = 0, 0
    for ch, _, _, _, _ in [
        ('导论',0,0,0,0),('第1章',0,0,0,0),('第2章',0,0,0,0),('第3章',0,0,0,0),
        ('第4章',0,0,0,0),('第5章',0,0,0,0),('第6章',0,0,0,0),('第7章',0,0,0,0),
        ('第8章',0,0,0,0),('第9章',0,0,0,0),('第10章',0,0,0,0),('第11章',0,0,0,0),
        ('第12章',0,0,0,0),('第13章',0,0,0,0),('第14章',0,0,0,0),('第15章',0,0,0,0),
    ]:
        ch_qs = chapters.get(ch, [])
        if not ch_qs:
            continue
        fp = os.path.join(OUT, f'{ch}.txt')
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(f'{ch}\n{"="*50}\n\n')
            for qt, lb in [('single','单选题'),('multiple','多选题'),('blank','填空题'),('judge','判断题')]:
                qs = [q for q in ch_qs if q['type'] == qt]
                if not qs: continue
                f.write(f'【{lb}】（共{len(qs)}题）\n\n')
                for n, q in enumerate(qs, 1):
                    f.write(f'{n}. {q["content"]}\n')
                    if q.get('options'):
                        for o in q['options']:
                            f.write(f' （{o["key"]}）{o["text"]}\n')
                    if q.get('answer'):
                        f.write(f' 答案：{q["answer"]}\n')
                    f.write('\n')
        tc2 = dict(Counter(q['type'] for q in ch_qs))
        ha = sum(1 for q in ch_qs if q['answer'])
        print(f'{ch}: {len(ch_qs)}q {tc2} ans={ha}')
        total += len(ch_qs)
        total_ans += ha
    print(f'\nTotal: {total}q, {total_ans} answers')
    print(f'Output: {OUT}')


if __name__ == '__main__':
    main()
