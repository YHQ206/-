"""
最终方案：
1. get_text('text') → 干净文本（格式：题号独立行 + 内容 + 选项）
2. get_text('dict') → 红色正确答案
3. 解析并结合，直接生成 V10 文件
"""
import os, re, fitz
from collections import Counter

PDF = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '习概题库.pdf')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output_xigai_v10')

# 章节分页
CHAPTERS = [
    ('导论', 1, 8), ('第1章', 8, 14), ('第2章', 14, 19), ('第3章', 19, 23),
    ('第4章', 23, 25), ('第5章', 25, 30), ('第6章', 30, 37), ('第7章', 37, 41),
    ('第8章', 41, 52), ('第9章', 52, 55), ('第10章', 55, 61), ('第11章', 61, 66),
    ('第12章', 66, 71), ('第13章', 71, 74), ('第14章', 74, 75), ('第15章', 75, 81),
    ('第16章', 81, 84), ('第17章', 84, 88),
]


def get_red_answers(doc):
    """提取所有红色答案（选择题字母 + 判断题√×）"""
    answers = []
    for pg in range(len(doc)):
        for block in doc[pg].get_text('dict')['blocks']:
            if 'lines' not in block: continue
            for line in block['lines']:
                red = ''.join(s['text'] for s in line['spans']
                              if (s['color'] & 0xFFFFFF) == 0xFF0000).strip()
                if not red: continue
                m = re.match(r'^（([A-G])）', red)
                if m: answers.append(('choice', m.group(1)))
                elif red == '√': answers.append(('judge', '√'))
                elif red == '×': answers.append(('judge', '×'))
    return answers


def parse_chapter(doc, start_pg, end_pg):
    """解析一个章节的页面，返回题目列表"""
    # 1. 收集clean text
    text = ''
    for pg in range(start_pg, end_pg):
        t = doc[pg].get_text('text')
        t = re.sub(r'爬取题库.*?Made by CWA\n?', '', t)
        t = re.sub(r'^— \d+ —$', '', t, flags=re.MULTILINE)
        t = re.sub(r'\[WARNING:[^\]]*\]\n?', '', t)
        text += t + '\n'

    lines = [l.strip() for l in text.split('\n')]

    questions = []
    current_type = None
    i = 0

    while i < len(lines):
        line = lines[i]
        if not line:
            i += 1; continue

        # 题型标记
        if line.startswith('一、单项选择题'):
            current_type = 'single'; i += 1; continue
        elif line.startswith('二、多项选择题'):
            current_type = 'multiple'; i += 1; continue
        elif line.startswith('三、填空题'):
            current_type = 'blank'; i += 1; continue
        elif line.startswith('四、判断题'):
            current_type = 'judge'; i += 1; continue
        elif re.match(r'^[五六七八九十]、', line):
            current_type = None; i += 1; continue

        if not current_type:
            i += 1; continue

        # 题号：单独一行 "N." 或带内容 "N. xxx"
        m = re.match(r'^(\d+)\.\s*(.*)', line)
        if not m:
            i += 1; continue

        q_num = int(m.group(1))
        q_start = m.group(2)

        # 如果题号后没有内容，从下一行取
        if not q_start and i + 1 < len(lines):
            i += 1
            q_start = lines[i]

        if current_type in ('single', 'multiple'):
            content_parts = [q_start]
            option_lines = []
            j = i + 1

            while j < len(lines):
                nl = lines[j]
                if not nl:
                    j += 1; continue
                if re.match(r'^\d+\.\s*', nl) or re.match(r'^[一二三四五六七八九十]、', nl):
                    break
                if re.match(r'^（[A-G]）', nl):
                    option_lines.append(nl)
                    j += 1
                else:
                    content_parts.append(nl)
                    j += 1

            # 合并内容
            content = ''.join(content_parts)
            content = content.replace('__________', '____')
            content = re.sub(r'\s+', '', content)

            # 提取选项
            options = []
            for ol in option_lines:
                om = re.match(r'^（([A-G])）\s*(.+)', ol)
                if om:
                    options.append({'key': om.group(1), 'text': om.group(2).strip()})

            questions.append({
                'type': current_type, 'content': content,
                'options': options, 'answer': ''
            })
            i = j - 1

        elif current_type == 'blank':
            content_parts = [q_start]
            j = i + 1
            while j < len(lines):
                nl = lines[j]
                if not nl: j += 1; continue
                if re.match(r'^\d+\.\s*', nl) or re.match(r'^[一二三四五六七八九十]、', nl):
                    break
                content_parts.append(nl)
                j += 1

            content = ''.join(content_parts)
            content = re.sub(r'\s+', '', content)
            content = content.replace('__________', '____')

            questions.append({
                'type': 'blank', 'content': content,
                'options': None, 'answer': ''
            })
            i = j - 1

        elif current_type == 'judge':
            content_parts = [q_start]
            j = i + 1
            while j < len(lines):
                nl = lines[j]
                if not nl: j += 1; continue
                if re.match(r'^\d+\.\s*', nl) or re.match(r'^[一二三四五六七八九十]、', nl):
                    break
                content_parts.append(nl)
                j += 1

            content = ''.join(content_parts)
            content = re.sub(r'\s+', '', content)
            content = content.replace('（√）','').replace('（×）','')

            questions.append({
                'type': 'judge', 'content': content,
                'options': None, 'answer': ''
            })
            i = j - 1

        i += 1

    return questions


def get_red_answers_for_pages(doc, start_pg, end_pg):
    """只提取指定页面范围内的红字答案"""
    answers = []
    for pg in range(start_pg, end_pg):
        if pg >= len(doc): break
        for block in doc[pg].get_text('dict')['blocks']:
            if 'lines' not in block: continue
            for line in block['lines']:
                red = ''.join(s['text'] for s in line['spans']
                              if (s['color'] & 0xFFFFFF) == 0xFF0000).strip()
                if not red: continue
                m = re.match(r'^（([A-G])）', red)
                if m: answers.append(('choice', m.group(1)))
                elif red == '√': answers.append(('judge', '√'))
                elif red == '×': answers.append(('judge', '×'))
    return answers


def main():
    doc = fitz.open(PDF)
    os.makedirs(OUT, exist_ok=True)
    grand_total = 0
    grand_ans = 0

    for ch_name, start_pg, end_pg in CHAPTERS:
        qs = parse_chapter(doc, start_pg, end_pg)
        red = get_red_answers_for_pages(doc, start_pg, end_pg)
        red_idx = 0

        # 给题目分配红字答案（每章独立）（按题型严格匹配数量）
        for q in qs:
            if q['type'] == 'single' and red_idx < len(red) and red[red_idx][0] == 'choice':
                q['answer'] = red[red_idx][1]
                red_idx += 1
            elif q['type'] == 'multiple' and red_idx < len(red) and red[red_idx][0] == 'choice':
                # 多选题：取连续红字直到遇到非choice或到合理数量(2-5)
                ans_set = set()
                while red_idx < len(red) and red[red_idx][0] == 'choice' and len(ans_set) < 10:
                    ans_set.add(red[red_idx][1])
                    red_idx += 1
                    # 检查：下一个红字属于不同section(遇到judge) → 可能属于下一题
                    if red_idx < len(red) and red[red_idx][0] != 'choice':
                        break
                    # 如果下一个红字字母已经在集合里 → 可能是新题
                    if red_idx < len(red) and red[red_idx][1] in ans_set:
                        break
                q['answer'] = ''.join(sorted(ans_set))
            elif q['type'] == 'judge' and red_idx < len(red) and red[red_idx][0] == 'judge':
                q['answer'] = red[red_idx][1]
                red_idx += 1

        # 跳过简答题（不写入题库）
        objective_qs = [q for q in qs if q['type'] in ('single','multiple','blank','judge')]

        # 写入文件
        fp = os.path.join(OUT, f'{ch_name}.txt')
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(f'{ch_name}\n{"="*50}\n\n')
            for qt, lb in [('single','单选题'),('multiple','多选题'),('blank','填空题'),('judge','判断题')]:
                qs2 = [q for q in objective_qs if q['type']==qt]
                if not qs2: continue
                f.write(f'【{lb}】（共{len(qs2)}题）\n\n')
                for n, q in enumerate(qs2, 1):
                    f.write(f'{n}. {q["content"]}\n')
                    if q.get('options'):
                        for o in q['options']:
                            f.write(f' （{o["key"]}）{o["text"]}\n')
                    if q.get('answer'):
                        f.write(f' 答案：{q["answer"]}\n')
                    f.write('\n')

        tc = dict(Counter(q['type'] for q in objective_qs))
        ha = sum(1 for q in objective_qs if q.get('answer'))
        no = len(objective_qs) - ha
        s = 'OK' if no == 0 else f'WARN:{no}'
        print(f'{ch_name}: {len(objective_qs)}q {tc} ans={ha}/{len(red)}red {s}')
        grand_total += len(objective_qs)
        grand_ans += ha

    print(f'\nTotal: {grand_total}q, {grand_ans} answers')
    print(f'Output: {OUT}')


if __name__ == '__main__':
    main()
