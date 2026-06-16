"""
从习概题库.pdf 完整提取：内容(黑字) + 答案(红字)。
完全替代 output_xigai_v8 的损坏数据。
"""
import os, re, sys, fitz
from collections import Counter, OrderedDict

PDF = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '习概题库.pdf')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output_xigai_v10')


class Span:
    __slots__ = ('text', 'red', 'x', 'y')
    def __init__(self, text, color, bbox):
        self.text = text
        self.red = (color & 0xFFFFFF) == 0xFF0000
        self.x = bbox[0]
        self.y = (bbox[1] + bbox[3]) / 2


def get_spans():
    """提取所有span，保留坐标和颜色"""
    doc = fitz.open(PDF)
    all_spans = []
    for pg in range(len(doc)):
        for block in doc[pg].get_text('dict')['blocks']:
            if 'lines' not in block:
                continue
            for line in block['lines']:
                line_spans = []
                for s in line['spans']:
                    if s['text'].strip():
                        line_spans.append(Span(s['text'], s['color'], s['bbox']))
                if line_spans:
                    all_spans.append(line_spans)
    return all_spans


def lines_to_paragraphs(all_spans):
    """将span行合并为段落（题干/选项行）"""
    rows = []
    for line_spans in all_spans:
        black = ''.join(s.text for s in line_spans if not s.red)
        red = ''.join(s.text for s in line_spans if s.red)
        full = black + red
        # 跳过页眉页脚
        if '爬取题库' in full or re.match(r'^—?\d+—?$', full.strip()):
            continue
        if full.strip():
            rows.append({'text': full.strip(), 'red': red.strip(), 'has_red': bool(red)})
    return rows


def extract():
    rows = lines_to_paragraphs(get_spans())
    print(f'Total rows: {len(rows)}')

    # === 第一步：提取所有红字答案 ===
    red_answers = []  # [letter]
    for r in rows:
        red = r['red']
        if not red:
            continue
        m = re.match(r'^（([A-G])）', red)
        if m:
            red_answers.append(m.group(1))
        elif red.strip() == '√':
            red_answers.append('√')
        elif red.strip() == '×':
            red_answers.append('×')

    print(f'Red answers: {len(red_answers)}')

    # === 第二步：解析题目结构 ===
    all_qs = []  # [{type, content, options, answer}]
    current_type = None
    current_chapter_start = True  # 标记新章节开始
    chapter_q_count = 0
    red_idx = 0

    for row in rows:
        text = row['text']

        # 章节/题型标记
        if text.startswith('一、单项选择题'):
            current_type = 'single'
            continue
        elif text.startswith('二、多项选择题'):
            current_type = 'multiple'
            continue
        elif text.startswith('三、填空题'):
            current_type = 'blank'
            continue
        elif text.startswith('四、判断题'):
            current_type = 'judge'
            continue
        elif re.match(r'^[五六七八九十]、', text):
            current_type = None
            continue

        if not current_type:
            continue

        # 题目行: N. xxx
        m = re.match(r'^(\d+)\.\s*(.+)', text)
        if not m:
            continue

        q_num = int(m.group(1))
        content = m.group(2)
        row_red = row['red']

        if current_type in ('single', 'multiple'):
            # 收集题目内容（可能跨多行）和选项
            # 选项特征：以（字母）开头
            # 需要从后续row中收集

            # 注意：PDF中选项可能在同一行或不同行
            # 在当前行中提取选项
            current_content = content
            current_options = []

            # 从当前行提取选项
            for om in re.finditer(r'（([A-G])）\s*(.+?)(?=（[A-G]）|$)', current_content):
                current_options.append({'key': om.group(1), 'text': om.group(2).strip()})

            if current_options:
                # 选项在同一行 -> 去掉选项部分得到纯内容
                content = re.sub(r'（[A-G]）.+?(?=（[A-G]）|$)', '', content).strip()
                content = re.sub(r'\s+', '', content)
            else:
                # 选项可能在后续行 -> 标记需要跨行收集
                content = re.sub(r'\s+', '', content)

            # 答案：从红字提取
            answer = ''
            if row_red:
                rm = re.match(r'^（([A-G])）', row_red)
                if rm:
                    answer = rm.group(1)
            elif red_idx < len(red_answers):
                # 尝试从最近的红色答案匹配
                # 简单策略：每道选择题消耗一个红字答案
                answer = red_answers[red_idx]
                red_idx += 1

            all_qs.append({
                'type': current_type,
                'content': content,
                'options': current_options if current_options else None,
                'answer': answer,
            })

        elif current_type == 'blank':
            content = re.sub(r'\s+', '', content)
            answer = row_red if row_red else ''
            all_qs.append({
                'type': 'blank',
                'content': content,
                'options': None,
                'answer': answer,
            })

        elif current_type == 'judge':
            content = re.sub(r'\s+', '', content)
            content = content.replace('（√）', '').replace('（×）', '')
            answer = ''
            if row_red:
                if '√' in row_red:
                    answer = '√'
                elif '×' in row_red:
                    answer = '×'
            elif red_idx < len(red_answers):
                ra = red_answers[red_idx]
                if ra in ('√', '×'):
                    answer = ra
                    red_idx += 1

            all_qs.append({
                'type': 'judge',
                'content': content,
                'options': None,
                'answer': answer,
            })

    # === 第三步：修复选项（跨行收集）===
    # 对于options为None的选择题，从下一道题的内容中反向提取
    for i, q in enumerate(all_qs):
        if q['type'] in ('single', 'multiple') and q['options'] is None:
            # 简单fallback：在content中找选项
            opts = []
            for om in re.finditer(r'（([A-G])）\s*(.+?)(?=（[A-G]）|$)', q['content']):
                opts.append({'key': om.group(1), 'text': om.group(2).strip()})
            if opts:
                q['options'] = opts
                q['content'] = re.sub(r'（[A-G]）.+?(?=（[A-G]）|$)', '', q['content']).strip()

    # === 第四步：按章节分割 ===
    # 使用已知的每章题目数
    chapters_spec = [
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

    # 先验证总数
    expected_total = sum(sc+mc+bl+ju for _, sc, mc, bl, ju in chapters_spec)
    print(f'Expected total: {expected_total}, Actual: {len(all_qs)}')

    chapters = {}
    q_idx = 0
    for ch_name, sc, mc, bl, ju in chapters_spec:
        ch_qs = []
        for qtype, count in [('single', sc), ('multiple', mc), ('blank', bl), ('judge', ju)]:
            taken = 0
            while taken < count and q_idx < len(all_qs):
                q = all_qs[q_idx]
                if q['type'] == qtype:
                    ch_qs.append(q)
                    q_idx += 1
                    taken += 1
                else:
                    # 类型不匹配，尝试skip
                    q_idx += 1
        chapters[ch_name] = ch_qs

    # === 第五步：写入文件 ===
    os.makedirs(OUT, exist_ok=True)
    total, total_ans = 0, 0
    for ch_name, _, _, _, _ in chapters_spec:
        ch_qs = chapters.get(ch_name, [])
        if not ch_qs:
            continue

        fp = os.path.join(OUT, f'{ch_name}.txt')
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(f'{ch_name}\n{"="*50}\n\n')
            for qtype, label in [('single', '单选题'), ('multiple', '多选题'),
                                  ('blank', '填空题'), ('judge', '判断题')]:
                qs = [q for q in ch_qs if q['type'] == qtype]
                if not qs:
                    continue
                f.write(f'【{label}】（共{len(qs)}题）\n\n')
                for num, q in enumerate(qs, 1):
                    f.write(f'{num}. {q["content"]}\n')
                    if q.get('options'):
                        for o in q['options']:
                            f.write(f' （{o["key"]}）{o["text"]}\n')
                    if q.get('answer'):
                        f.write(f' 答案：{q["answer"]}\n')
                    f.write('\n')

        tc = dict(Counter(q['type'] for q in ch_qs))
        has = sum(1 for q in ch_qs if q.get('answer'))
        no = len(ch_qs) - has
        s = 'OK' if no == 0 else f'WARN:{no}'
        print(f'{ch_name}: {len(ch_qs)}q {tc} ans={has} {s}')
        total += len(ch_qs)
        total_ans += has

    print(f'\nTotal: {total}q, {total_ans} with answers, {total-total_ans} without')
    print(f'Output: {OUT}')


if __name__ == '__main__':
    extract()
