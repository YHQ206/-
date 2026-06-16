"""
从习概题库.pdf 正确提取题目和答案 V2。

关键发现：
- 红色(#ff0000)文字单独成行，标记的是每道题的正确答案
- 红色选项行: （字母）选项文本 — 只有正确选项是红色的
- 黑字选项行: 可能包含多个选项（黑色）+ 一个红色选项

策略：
1. 提取所有文本行（标记红色/黑色）
2. 顺序解析题目
3. 用红色选项行匹配答案：每道选择题后遇到的第一个红色选项 = 该题答案
"""
import os, re, fitz
from collections import Counter

PDF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '习概题库.pdf')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output_xigai_v10')


def get_all_lines():
    """提取所有文本行，标记是否含红色文字和红色文字内容"""
    doc = fitz.open(PDF_PATH)
    all_lines = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text('dict')['blocks']

        for block in blocks:
            if 'lines' not in block:
                continue
            for line in block['lines']:
                black_text = ''
                red_text = ''
                has_red = False
                for span in line['spans']:
                    text = span['text']
                    is_red = (span['color'] & 0xFFFFFF) == 0xFF0000
                    if is_red:
                        red_text += text
                        has_red = True
                    else:
                        black_text += text

                full_text = black_text + red_text
                # 跳过页眉
                if full_text.strip().startswith('爬取题库'):
                    continue
                # 跳过页码
                if re.match(r'^—\d+—$', full_text.strip()):
                    continue
                # 跳过分隔线
                if re.match(r'^[=]+$', full_text.strip()):
                    continue

                if full_text.strip():
                    all_lines.append({
                        'text': full_text.strip(),
                        'black': black_text.strip(),
                        'red': red_text.strip(),
                        'has_red': has_red,
                        'page': page_num,
                    })

    return all_lines


def is_red_option_line(line_data):
    """检查是否是红色答案行（只包含红色选项）"""
    text = line_data['text']
    red = line_data['red']
    # 红色行且包含选项格式（字母）选项文本
    if line_data['has_red'] and re.match(r'^（[A-G]）', text):
        return True
    # 判断题：红色√或×
    if line_data['has_red'] and text.strip() in ('√', '×'):
        return True
    return False


def extract_option_letter(text):
    """从红色选项文本提取字母"""
    m = re.match(r'^（([A-G])）', text)
    if m:
        return m.group(1)
    return None


def parse_all():
    """解析所有题目"""
    lines = get_all_lines()
    print(f'📖 共 {len(lines)} 行文本')

    # 收集红色答案行
    red_answers = []  # [(line_index, option_letter)]
    for idx, line_data in enumerate(lines):
        if is_red_option_line(line_data):
            letter = extract_option_letter(line_data['text'])
            if letter:
                red_answers.append((idx, letter))
            elif line_data['text'].strip() == '√':
                red_answers.append((idx, '√'))
            elif line_data['text'].strip() == '×':
                red_answers.append((idx, '×'))

    print(f'🔴 {len(red_answers)} 个红色答案标记')

    # 顺序解析题目，匹配红色答案
    all_questions = []  # [{type, content, options, answer, chapter_hint}]
    current_type = None
    red_idx = 0  # 当前红色答案的索引

    for line_idx, line_data in enumerate(lines):
        text = line_data['text']

        # 检测题型标题
        if re.match(r'^一、单项选择题', text):
            current_type = 'single'
            continue
        elif re.match(r'^二、多项选择题', text):
            current_type = 'multiple'
            continue
        elif re.match(r'^三、填空题', text):
            current_type = 'blank'
            continue
        elif re.match(r'^四、判断题', text):
            current_type = 'judge'
            continue
        elif re.match(r'^[五六七八九十]、', text):
            current_type = None
            continue

        if not current_type:
            continue

        # 题目行
        m = re.match(r'^(\d+)\.\s*(.+)', text)
        if not m:
            continue

        q_num = int(m.group(1))
        q_start = m.group(2)

        if current_type in ('single', 'multiple'):
            # 收集题目内容 + 选项（从后续行）
            content_parts = [q_start]
            option_parts = []
            j = line_idx + 1

            while j < len(lines):
                nl = lines[j]
                nt = nl['text']
                if not nt:
                    j += 1
                    continue
                if re.match(r'^\d+\.', nt) or re.match(r'^[一二三四五六七八九十]、', nt):
                    break
                # 检查是否是选项行（黑字或红字）
                if re.search(r'（[A-G]）', nt):
                    option_parts.append(nt)
                    j += 1
                elif is_red_option_line(nl) and re.match(r'^（[A-G]）', nt):
                    # 纯红色选项行
                    option_parts.append(nt)
                    j += 1
                else:
                    content_parts.append(nt)
                    j += 1

            # 合并内容
            full_content = ''.join(content_parts)
            full_content = re.sub(r'\s+', '', full_content)
            full_content = full_content.replace('（ ）', '').replace('（）', '')

            # 从选项行提取选项
            all_opt_text = ''.join(option_parts)
            options = []
            for om in re.finditer(r'（([A-G])）\s*(.+?)(?=（[A-G]）|$)', all_opt_text):
                key = om.group(1)
                if key not in [o['key'] for o in options]:
                    options.append({'key': key, 'text': om.group(2).strip()})

            # 查找答案：在当前题目之后的第一条红色选项行
            answer = ''
            # 在option_parts中找红色选项
            for opt_line in option_parts:
                if re.match(r'^（[A-G]）', opt_line):
                    # 检查这条option_line是否来自红色行
                    # 需要回查原始行
                    pass

            # 更简单的方法：在 lines[line_idx+1] 到 lines[j] 之间找红色行
            for k in range(line_idx + 1, j + 1):
                if k < len(lines) and is_red_option_line(lines[k]):
                    letter = extract_option_letter(lines[k]['text'])
                    if letter:
                        if current_type == 'single':
                            answer = letter
                        else:  # multiple
                            answer = ''.join(sorted(set(answer + letter)))
                        break

            # 如果上面没找到，在j之后的红色行中找（最近的一个）
            if not answer and red_idx < len(red_answers):
                red_line_idx, red_letter = red_answers[red_idx]
                if red_line_idx >= line_idx and red_line_idx <= j + 5:
                    answer = red_letter
                    red_idx += 1

            # 清理内容（去掉选项文本）
            content = re.sub(r'（[A-G]）.+?(?=（[A-G]）|$)', '', ' '.join(content_parts))
            content = content.replace('（ ）', '').replace('（）', '')
            content = re.sub(r'\s+', '', content)
            content = re.sub(r'[\(（]\s*[\)）]', '', content)

            all_questions.append({
                'type': current_type,
                'content': content,
                'options': options,
                'answer': answer,
            })

        elif current_type == 'blank':
            content_parts = [q_start]
            j = line_idx + 1
            answer = ''

            while j < len(lines):
                nl = lines[j]
                nt = nl['text']
                if not nt:
                    j += 1
                    continue
                if re.match(r'^\d+\.', nt) or re.match(r'^[一二三四五六七八九十]、', nt):
                    break
                if is_red_option_line(nl):
                    answer = nl['text']
                    j += 1
                    break
                content_parts.append(nt)
                j += 1

            content = ''.join(content_parts)
            content = re.sub(r'\s+', '', content)

            all_questions.append({
                'type': 'blank',
                'content': content,
                'options': None,
                'answer': answer,
            })

        elif current_type == 'judge':
            content_parts = [q_start]
            j = line_idx + 1
            answer = ''

            # 检查行内答案
            if '（√）' in q_start:
                answer = '√'
                q_start = q_start.replace('（√）', '')
            elif '（×）' in q_start:
                answer = '×'
                q_start = q_start.replace('（×）', '')

            while j < len(lines):
                nl = lines[j]
                nt = nl['text']
                if not nt:
                    j += 1
                    continue
                if re.match(r'^\d+\.', nt) or re.match(r'^[一二三四五六七八九十]、', nt):
                    break
                if is_red_option_line(nl) and not answer:
                    if '√' in nt:
                        answer = '√'
                    elif '×' in nt:
                        answer = '×'
                    j += 1
                    break
                content_parts.append(nt)
                j += 1

            content = ''.join(content_parts)
            content = re.sub(r'\s+', '', content)
            content = content.replace('（√）', '').replace('（×）', '')

            all_questions.append({
                'type': 'judge',
                'content': content,
                'options': None,
                'answer': answer,
            })

    return all_questions


def split_by_chapter(questions):
    """按章节分割题目（基于题号重置和题型序列）"""
    # 使用已知的每章题目数
    # 从原始统计.txt（v8已验证的统计）
    chapter_counts = [
        ('导论', {'single': 63, 'multiple': 2, 'blank': 2, 'judge': 2}),
        ('第1章', {'single': 42, 'multiple': 5, 'blank': 5, 'judge': 5}),
        ('第2章', {'single': 43, 'multiple': 3, 'blank': 2, 'judge': 4}),
        ('第3章', {'single': 40}),
        ('第4章', {'single': 10, 'multiple': 2, 'blank': 2, 'judge': 4}),
        ('第5章', {'single': 45, 'multiple': 9, 'blank': 3, 'judge': 6}),
        ('第6章', {'single': 52, 'multiple': 12, 'blank': 6, 'judge': 11}),
        ('第7章', {'single': 41}),
        ('第8章', {'single': 70, 'multiple': 16, 'blank': 15, 'judge': 14}),
        ('第9章', {'single': 29, 'multiple': 3}),
        ('第10章', {'single': 36, 'multiple': 19, 'blank': 18, 'judge': 15}),
        ('第11章', {'single': 20, 'multiple': 14, 'blank': 14, 'judge': 12}),
        ('第12章', {'single': 25, 'multiple': 14, 'blank': 13, 'judge': 11}),
        ('第13章', {'single': 25}),
        ('第14章', {'single': 13}),
        ('第15章', {'single': 71, 'multiple': 14, 'blank': 14, 'judge': 11}),
    ]

    chapters = {}
    q_idx = 0

    for ch_name, expected in chapter_counts:
        ch_questions = []
        for qtype in ['single', 'multiple', 'blank', 'judge']:
            count = expected.get(qtype, 0)
            for _ in range(count):
                if q_idx < len(questions):
                    q = questions[q_idx]
                    if q['type'] == qtype:
                        ch_questions.append(q)
                        q_idx += 1
                    else:
                        # 类型不匹配，向前搜索
                        found = False
                        for offset in range(1, 5):
                            if q_idx + offset < len(questions) and questions[q_idx + offset]['type'] == qtype:
                                q_idx += offset
                                ch_questions.append(questions[q_idx])
                                q_idx += 1
                                found = True
                                break
                        if not found:
                            # 跳过这个类型的计数
                            pass

        chapters[ch_name] = ch_questions

    return chapters


def main():
    print('📖 提取文本和红色答案...')
    questions = parse_all()
    print(f'  共 {len(questions)} 题')
    type_counts = Counter(q['type'] for q in questions)
    print(f'  类型: {dict(type_counts)}')
    has = sum(1 for q in questions if q['answer'])
    print(f'  有答案: {has}/{len(questions)}')

    print('\n📂 按章节分割...')
    chapters = split_by_chapter(questions)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total_q = 0
    total_ans = 0

    for ch_name, ch_questions in chapters.items():
        if not ch_questions:
            continue

        filepath = os.path.join(OUTPUT_DIR, f'{ch_name}.txt')
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
                    content = q['content']
                    f.write(f'{num}. {content}\n')
                    if q.get('options'):
                        for opt in q['options']:
                            f.write(f' （{opt["key"]}）{opt["text"]}\n')
                    ans = q.get('answer', '')
                    if ans:
                        f.write(f' 答案：{ans}\n')
                    else:
                        f.write('\n')
                    f.write('\n')

        tc = dict(Counter(q['type'] for q in ch_questions))
        has_ans = sum(1 for q in ch_questions if q.get('answer'))
        no_ans = len(ch_questions) - has_ans
        status = '✅' if no_ans == 0 else f'⚠️ {no_ans}无答案'
        print(f'  {ch_name}: {len(ch_questions)}题 {tc} {status}')

        total_q += len(ch_questions)
        total_ans += has_ans

    print(f'\n📊 总计: {total_q}题, {total_ans}有答案, {total_q - total_ans}无答案')
    print(f'  输出: {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
