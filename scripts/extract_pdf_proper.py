"""
从习概题库.pdf 正确提取题目和答案。
- 红色(#ff0000)文字标记的是正确答案
- 使用 PyMuPDF (fitz) 保留颜色信息
"""
import os
import re
import fitz  # PyMuPDF

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(PROJECT_DIR, '..', '习概题库.pdf')
OUTPUT_DIR = os.path.join(PROJECT_DIR, '..', 'output_xigai_v10')


class Span:
    """文本片段"""
    def __init__(self, text, color, bbox):
        self.text = text
        self.is_red = (color & 0xFFFFFF) == 0xFF0000  # 红色
        self.bbox = bbox  # (x0, y0, x1, y1)
        self.y = (bbox[1] + bbox[3]) / 2  # 垂直中心

    def __repr__(self):
        c = 'R' if self.is_red else 'B'
        return f'[{c}]{self.text}'


def extract_spans(page):
    """从一页提取所有带颜色信息的文本片段，按阅读顺序排列"""
    blocks = page.get_text('dict')['blocks']
    spans = []
    for block in blocks:
        if 'lines' not in block:
            continue
        for line in block['lines']:
            for span in line['spans']:
                text = span['text'].strip()
                if text:
                    spans.append(Span(
                        text=text,
                        color=span['color'],
                        bbox=span['bbox']
                    ))
    return spans


def spans_to_text(spans, red_only=False):
    """将spans合并为文本"""
    parts = []
    for s in spans:
        if red_only and not s.is_red:
            continue
        if not red_only and s.is_red:
            continue
        parts.append(s.text)
    return ''.join(parts)


def extract_questions_from_pdf():
    """从PDF提取所有题目和答案"""
    doc = fitz.open(PDF_PATH)

    all_text_lines = []  # [(page_num, spans_line)]

    for page_num in range(len(doc)):
        page = doc[page_num]
        spans = extract_spans(page)

        # 将spans按行分组（相近y坐标）
        if not spans:
            continue

        lines = []
        current_line = [spans[0]]
        for s in spans[1:]:
            if abs(s.y - current_line[-1].y) > 3:  # 新行
                lines.append(current_line)
                current_line = [s]
            else:
                current_line.append(s)
        lines.append(current_line)

        for line_spans in lines:
            all_text_lines.append((page_num, line_spans))

    # 合并每行为纯文本（红黑分开）
    processed_lines = []
    for pg, line_spans in all_text_lines:
        full_text = ''.join(s.text for s in line_spans)
        red_text = ''.join(s.text for s in line_spans if s.is_red)
        processed_lines.append({
            'page': pg,
            'text': full_text,
            'red': red_text,
            'has_red': any(s.is_red for s in line_spans),
        })

    return processed_lines


def parse_questions(lines):
    """解析题目列表，提取答案（红色=正确选项）"""
    questions = []
    current_type = None
    current_chapter = None
    chapter_idx = 0
    i = 0

    # 章节序列
    CHAPTERS = ['导论', '第1章', '第2章', '第3章', '第4章', '第5章',
                '第6章', '第7章', '第8章', '第9章', '第10章', '第11章',
                '第12章', '第13章', '第14章', '第15章', '第16章', '第17章']

    # 从第一条单选题开始，遇到章节边界就切换
    # 判断章节边界：遇到新的"一、单项选择题"且与上一章题目数差异大

    chapter_questions = {ch: [] for ch in CHAPTERS}
    current_chapter_questions = []
    chapter_started = False

    for line_data in lines:
        text = line_data['text']
        red = line_data['red']

        # 检测"一、单项选择题" — 新章节开始
        if re.match(r'^一、单项选择题', text):
            if chapter_started and current_chapter_questions and chapter_idx < len(CHAPTERS):
                ch_name = CHAPTERS[chapter_idx]
                chapter_questions[ch_name] = current_chapter_questions
                chapter_idx += 1
                current_chapter_questions = []

            current_type = 'single'
            chapter_started = True
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

        if not current_type or not chapter_started:
            continue

        # 解析题目
        m = re.match(r'^(\d+)\.\s*(.+)', text)
        if not m:
            continue

        q_num = int(m.group(1))
        q_text = m.group(2)

        if current_type in ('single', 'multiple'):
            # 查找这个题目的所有行（题目+选项）
            q_lines = [q_text]
            q_red_lines = [red]

            # 答案来自红色文字
            answer_from_red = set()
            if red:
                # 从红色文字中提取选项字母
                red_letters = re.findall(r'（([A-G])）', red)
                answer_from_red.update(red_letters)

            # 收集后续行直到下一题或新章节
            j = i + 1
            while j < len(lines):
                nl = lines[j]
                nt = nl['text'].strip()
                nr = nl['red'].strip()
                if not nt:
                    j += 1
                    continue
                if re.match(r'^\d+\.', nt) or re.match(r'^[一二三四五六七八九十]、', nt):
                    break
                # 检查是否是选项行
                if re.search(r'（[A-G]）', nt):
                    q_lines.append(nt)
                    if nr:
                        q_red_lines.append(nr)
                        letters = re.findall(r'（([A-G])）', nr)
                        answer_from_red.update(letters)
                    j += 1
                else:
                    q_lines.append(nt)
                    j += 1

            q_content = ''.join(q_lines)
            # 从内容中提取选项
            options = []
            for om in re.finditer(r'（([A-G])）\s*(.+?)(?=（[A-G]）|$)', ''.join(q_lines)):
                opt_text = om.group(2).strip()
                if om.group(1) not in [o['key'] for o in options]:
                    options.append({'key': om.group(1), 'text': opt_text})

            # 清理题目内容（去掉选项部分）
            content = re.sub(r'（[A-G]）.+?(?=（[A-G]）|$)', '', q_content)
            content = content.replace('（ ）', '').replace('（）', '').strip()
            content = re.sub(r'\s+', '', content)

            answer = ''.join(sorted(answer_from_red)) if answer_from_red else ''

            current_chapter_questions.append({
                'type': current_type,
                'content': content,
                'options': options,
                'answer': answer,
            })

            # 更新i到j-1
            # (在外部循环中处理)

        elif current_type == 'blank':
            q_lines = [q_text]
            answer = red if red else ''

            j = i + 1
            while j < len(lines):
                nl = lines[j]
                nt = nl['text'].strip()
                nr = nl['red'].strip()
                if not nt:
                    j += 1
                    continue
                if re.match(r'^\d+\.', nt) or re.match(r'^[一二三四五六七八九十]、', nt):
                    break
                q_lines.append(nt)
                if nr and not answer:
                    answer = nr
                j += 1

            content = ''.join(q_lines).strip()
            content = re.sub(r'\s+', '', content)

            current_chapter_questions.append({
                'type': 'blank',
                'content': content,
                'options': None,
                'answer': answer,
            })

        elif current_type == 'judge':
            q_lines = [q_text]
            answer = ''
            if red:
                if '√' in red:
                    answer = '√'
                elif '×' in red:
                    answer = '×'

            j = i + 1
            while j < len(lines):
                nl = lines[j]
                nt = nl['text'].strip()
                nr = nl['red'].strip()
                if not nt:
                    j += 1
                    continue
                if re.match(r'^\d+\.', nt) or re.match(r'^[一二三四五六七八九十]、', nt):
                    break
                q_lines.append(nt)
                if nr and not answer:
                    if '√' in nr:
                        answer = '√'
                    elif '×' in nr:
                        answer = '×'
                j += 1

            content = ''.join(q_lines).strip()
            content = re.sub(r'\s+', '', content)
            content = content.replace('（√）', '').replace('（×）', '').replace('(√)', '').replace('(×)', '')

            current_chapter_questions.append({
                'type': 'judge',
                'content': content,
                'options': None,
                'answer': answer,
            })

    # 保存最后一章
    if current_chapter_questions and chapter_idx < len(CHAPTERS):
        chapter_questions[CHAPTERS[chapter_idx]] = current_chapter_questions

    return chapter_questions


def main():
    print('📖 读取PDF（带颜色信息）...')
    lines = extract_questions_from_pdf()
    print(f'  共 {len(lines)} 行文本')

    print('\n🔍 解析题目和答案...')
    chapters = parse_questions(lines)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total_q = 0
    total_ans = 0

    for ch_name in ['导论', '第1章', '第2章', '第3章', '第4章', '第5章',
                     '第6章', '第7章', '第8章', '第9章', '第10章', '第11章',
                     '第12章', '第13章', '第14章', '第15章', '第16章', '第17章']:
        questions = chapters.get(ch_name, [])
        if not questions:
            continue

        # 写入文件
        filepath = os.path.join(OUTPUT_DIR, f'{ch_name}.txt')
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

        from collections import Counter
        tc = dict(Counter(q['type'] for q in questions))
        has_ans = sum(1 for q in questions if q.get('answer'))
        no_ans = len(questions) - has_ans
        status = '✅' if no_ans == 0 else f'⚠️ {no_ans}无答案'
        print(f'  {ch_name}: {len(questions)}题 {tc} {status}')

        total_q += len(questions)
        total_ans += has_ans

    print(f'\n📊 总计: {total_q}题, {total_ans}有答案')
    print(f'  输出目录: {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
