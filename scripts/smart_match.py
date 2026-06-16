"""
智能匹配：用内容相似度将 V8 每道题匹配到 PDF 原题，
直接取 PDF 的正确答案。不受题目顺序影响。
"""
import os, re, sys, fitz
from collections import Counter
from difflib import SequenceMatcher

PROJECT = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(PROJECT, '..', '习概题库.pdf')
V8_DIR = os.path.join(PROJECT, '..', 'output_xigai_v8')
OUT_DIR = os.path.join(PROJECT, '..', 'output_xigai_v10')

sys.path.insert(0, os.path.join(PROJECT, '..', 'backend'))
from routes.import_routes import parse_txt_file, _clean_content


def extract_pdf_questions():
    """从 PDF 提取题目(clean text) + 答案(red text)"""
    doc = fitz.open(PDF)

    # 收集所有页面文本
    all_text = ''
    for pg in range(len(doc)):
        text = doc[pg].get_text('text')
        text = re.sub(r'爬取题库.*?Made by CWA\n?', '', text)
        text = re.sub(r'^— \d+ —$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\[WARNING:[^\]]*\]\n?', '', text)
        all_text += text + '\n'

    # 收集红字答案（按PDF出现顺序）
    red_answers = []
    for pg in range(len(doc)):
        for block in doc[pg].get_text('dict')['blocks']:
            if 'lines' not in block: continue
            for line in block['lines']:
                red = ''.join(s['text'] for s in line['spans']
                             if (s['color'] & 0xFFFFFF) == 0xFF0000).strip()
                if not red: continue
                m = re.match(r'^（([A-G])）', red)
                if m:
                    red_answers.append(('choice', m.group(1)))
                elif red == '√': red_answers.append(('judge', '√'))
                elif red == '×': red_answers.append(('judge', '×'))

    # 解析题目（改进版：处理题号单独一行的格式）
    lines = [l.strip() for l in all_text.split('\n') if l.strip() and 'WARNING' not in l]

    # 合并：如果一行只是数字+点，合并到下一行
    merged = []
    i = 0
    while i < len(lines):
        if re.match(r'^\d+\.$', lines[i]) and i+1 < len(lines):
            merged.append(f'{lines[i]} {lines[i+1]}')
            i += 2
        else:
            merged.append(lines[i])
            i += 1

    lines = merged

    questions = []
    current_type = None
    red_idx = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # 题型
        if '一、单项选择题' in line:
            current_type = 'single'; i += 1; continue
        elif '二、多项选择题' in line:
            current_type = 'multiple'; i += 1; continue
        elif '三、填空题' in line:
            current_type = 'blank'; i += 1; continue
        elif '四、判断题' in line:
            current_type = 'judge'; i += 1; continue
        elif re.match(r'^[五六七八九十]、', line):
            current_type = None; i += 1; continue

        if not current_type:
            i += 1; continue

        m = re.match(r'^(\d+)\.\s*(.+)', line)
        if not m:
            i += 1; continue

        q_num = int(m.group(1))
        q_start = m.group(2)

        if current_type in ('single', 'multiple'):
            content_parts = [q_start]
            option_lines = []
            j = i + 1
            while j < len(lines):
                nl = lines[j]
                if re.match(r'^\d+\.\s', nl) or re.match(r'^[一二三四五六七八九十]、', nl):
                    break
                if re.match(r'^（[A-G]）', nl):
                    option_lines.append(nl)
                    j += 1
                else:
                    content_parts.append(nl)
                    j += 1

            content = ''.join(content_parts)
            content = content.replace('__________', '____')
            content = re.sub(r'\s+', '', content)

            options = []
            for ol in option_lines:
                om = re.match(r'^（([A-G])）\s*(.+)', ol)
                if om:
                    key = om.group(1)
                    if key not in [o['key'] for o in options]:
                        options.append({'key': key, 'text': om.group(2).strip()})

            # 答案：取最近的红色choice答案
            answer = ''
            while red_idx < len(red_answers) and red_answers[red_idx][0] == 'choice':
                answer = ''.join(sorted(set(answer + red_answers[red_idx][1])))
                red_idx += 1
                if current_type == 'single': break

            questions.append({
                'type': current_type, 'content': content,
                'options': options, 'answer': answer
            })
            i = j - 1

        elif current_type == 'judge':
            content_parts = [q_start]
            j = i + 1
            while j < len(lines):
                nl = lines[j]
                if re.match(r'^\d+\.\s', nl) or re.match(r'^[一二三四五六七八九十]、', nl):
                    break
                content_parts.append(nl)
                j += 1

            content = ''.join(content_parts)
            content = re.sub(r'\s+', '', content)
            content = content.replace('（√）','').replace('（×）','')

            answer = ''
            if red_idx < len(red_answers) and red_answers[red_idx][0] == 'judge':
                answer = red_answers[red_idx][1]
                red_idx += 1

            questions.append({
                'type': 'judge', 'content': content,
                'options': None, 'answer': answer
            })
            i = j - 1

        elif current_type == 'blank':
            content_parts = [q_start]
            j = i + 1
            while j < len(lines):
                nl = lines[j]
                if re.match(r'^\d+\.\s', nl) or re.match(r'^[一二三四五六七八九十]、', nl):
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

        i += 1

    return questions


def content_similarity(a, b):
    """计算两段文本的相似度"""
    # 清理
    a = re.sub(r'[_\s,.，。、；：""''！？（）\(\)\[\]【】]', '', a)[:100]
    b = re.sub(r'[_\s,.，。、；：""''！？（）\(\)\[\]【】]', '', b)[:100]
    if not a or not b:
        return 0
    return SequenceMatcher(None, a, b).ratio()


def match_and_replace():
    """将 V8 题目逐一匹配到 PDF 题目，替换内容和答案"""
    pdf_questions = extract_pdf_questions()
    print(f'PDF: {len(pdf_questions)} questions')
    tc = dict(Counter(q['type'] for q in pdf_questions))
    print(f'Types: {tc}')

    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted([f for f in os.listdir(V8_DIR)
                   if f.endswith('.txt') and f not in ('统计.txt','异常清单.txt')])

    total_replaced = 0
    total_ans_fixed = 0

    for fname in files:
        ch = fname.replace('.txt', '')
        old_qs = parse_txt_file(os.path.join(V8_DIR, fname))
        new_qs = []

        for old_q in old_qs:
            # 尝试匹配 PDF 题目
            best_match = None
            best_score = 0
            best_idx = -1

            for idx, pdf_q in enumerate(pdf_questions):
                if pdf_q['type'] != old_q['type']:
                    continue
                score = content_similarity(old_q['content'], pdf_q['content'])
                if score > best_score:
                    best_score = score
                    best_match = pdf_q
                    best_idx = idx

            if best_match and best_score > 0.4:
                # 使用 PDF 的内容和答案
                new_q = dict(best_match)  # copy
                # 但如果相似度不够高，保留旧内容
                if best_score < 0.7:
                    new_q['content'] = old_q['content']
                total_replaced += 1

                # 检查答案是否变化
                if old_q.get('answer') != best_match.get('answer'):
                    total_ans_fixed += 1
            else:
                # 无匹配，保留旧内容
                new_q = dict(old_q)

            new_qs.append(new_q)

        # 写入文件
        fp = os.path.join(OUT_DIR, fname)
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(f'{ch}\n{"="*50}\n\n')
            for qt, lb in [('single','单选题'),('multiple','多选题'),('blank','填空题'),('judge','判断题')]:
                qs = [q for q in new_qs if q['type']==qt]
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

        tc2 = dict(Counter(q['type'] for q in new_qs))
        ha = sum(1 for q in new_qs if q.get('answer'))
        print(f'{ch}: {len(new_qs)}q {tc2} ans={ha}')

    print(f'\nTotal: {total_replaced} questions matched, {total_ans_fixed} answers fixed')
    print(f'Output: {OUT_DIR}')


if __name__ == '__main__':
    match_and_replace()
