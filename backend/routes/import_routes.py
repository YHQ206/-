"""题库导入API"""
import os
import re
from flask import Blueprint, jsonify, request
from models import db, Subject, Chapter, Question, Record, Progress, Favorite, LastPosition
from docx_parser import parse_docx_file, parse_docx_to_chapters

import_bp = Blueprint('import', __name__)

# 题库目录配置
OUTPUT_DIRS = {
    '习概': os.path.join(os.path.dirname(__file__), '..', '..', 'output_xigai_v10'),
    '马原': os.path.join(os.path.dirname(__file__), '..', '..', 'output_mayuan'),
}

# Word文件配置
DOCX_FILES = {
    '习概': os.path.join(os.path.dirname(__file__), '..', '..', '客观题题库及答案 .docx'),
}

# 马原只用一个文件，避免重复导入
MAYUAN_MAIN_FILE = '全部题目.txt'

# 需要跳过的文件名（非题库文件）
SKIP_FILES = {'导出说明.txt', '统计.txt', '异常清单.txt',
              '判断题.txt', '单项选择题.txt', 'mayuan_output.txt'}

def _clean_content(text):
    """清理PDF提取残留标记（中文字符间的ASCII artifacts）

    清理策略：在中文政治试题中，题目内容不会包含独立的ASCII大写字母组合。
    选项标签（A/B/C/D）在解析时已作为key单独存储，所以移除所有大写字母是安全的。
    """
    # 1. 移除完整的 [WARNING: ...] 块和孤立的中括号
    text = re.sub(r'\[WARNING:[^\]]*\]', '', text)
    text = text.replace('[', '').replace(']', '')
    # 2. 移除 -X 形式（-F, -S, -E 等标记）
    text = re.sub(r'-[A-Z]-?', '', text)
    # 3. 移除所有ASCII大写字母序列（artifact核心）
    #    在中文政治题中，内容不会出现独立的ASCII大写单词
    text = re.sub(r'[A-Z]+', '', text)
    # 4. 移除残留的ASCII冒号（G:, ING: 等artifact的残余）
    text = text.replace(':', '')
    # 5. 清理多余空格
    text = re.sub(r'\s{2,}', ' ', text)
    # 6. 移除中文字符间的不必要空格（如 "复 杂" → "复杂"）
    text = re.sub(r'(?<=[^\x00-\x7f])\s(?=[^\x00-\x7f])', '', text)
    return text.strip()


def _is_section_header(line):
    """判断是否是题型小节标题"""
    return bool(re.search(r'(单项选择题|单选题|多项选择题|多选题|填空题|判断题|简答题|论述题|材料题|案例分析)', line))


def _is_new_question(line):
    """判断是否是下一道题的开始"""
    return bool(re.match(r'^\d+[.、]', line))


def parse_txt_file(filepath):
    """解析TXT格式的题库文件，兼容多种格式（习概/马原）"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    questions = []
    lines = content.split('\n')

    current_type = None
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # 跳过空行
        if not line:
            i += 1
            continue

        # 跳过分隔线（==== 或 ----）
        if re.match(r'^[=]{3,}$', line) or re.match(r'^[-]{3,}$', line):
            i += 1
            continue

        # 跳过统计/校验/异常清单等元信息行
        if line in ('提取统计', '统计', '校验详情', '异常清单'):
            i += 1
            continue
        if re.match(r'^(说明|校验详情|⚠|原始)', line):
            i += 1
            continue

        # 识别题型（必须在【】跳过之前，因为【单选题】等同时触发类型切换）
        if '单项选择题' in line or '单选题' in line:
            current_type = 'single'
            i += 1
            continue
        elif '多项选择题' in line or '多选题' in line:
            current_type = 'multiple'
            i += 1
            continue
        elif '填空题' in line:
            current_type = 'blank'
            i += 1
            continue
        elif '判断题' in line:
            current_type = 'judge'
            i += 1
            continue
        elif any(x in line for x in ['简答题', '论述题', '材料题', '案例分析']):
            current_type = None
            i += 1
            continue

        # 跳过【单选题】等小节标记行（必须在类型识别之后，因为需要先触发类型切换）
        if re.match(r'^【.+?】', line):
            i += 1
            continue

        if not current_type:
            i += 1
            continue

        # 解析题目（支持 1. 和 1、 两种编号格式）
        match = re.match(r'^(\d+)[.、]\s*(.+)', line)
        if match:
            q_num = match.group(1)
            q_start = q_content = match.group(2).strip()

            if current_type in ('single', 'multiple'):
                # === 选择题 ===
                # 分别收集题干续行和选项行（保持选项行原始格式用于提取key）
                content_parts = [q_start]
                option_lines = []
                j = i + 1
                answer_line_idx = None

                while j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue

                    # 下一道题 → 停止
                    if _is_new_question(next_line):
                        break
                    # 小节标题 → 停止
                    if re.match(r'^【', next_line) or _is_section_header(next_line):
                        break
                    # 答案行 → 记录位置，停止收集
                    if '答案' in next_line:
                        answer_line_idx = j
                        j += 1
                        break
                    # 选项行 → 收集到option_lines（不混入题干）
                    if re.match(r'^[A-G][.、]', next_line) or re.match(r'^（[A-G]?）', next_line):
                        option_lines.append(next_line)
                        j += 1
                    else:
                        # 题干续行（多行题目内容）→ 收集
                        content_parts.append(next_line)
                        j += 1

                # 清洗题干内容（不包含选项行，避免破坏选项标记）
                q_content = _clean_content(' '.join(content_parts))

                # 从原始选项行提取选项
                options = []
                if option_lines:
                    option_text = ' '.join(option_lines)
                    # 格式1: A.选项 或 A、选项（马原格式）
                    option_matches = re.findall(r'([A-G])[.、]\s*(.+?)(?=[A-G][.、]|$)', option_text)
                    if option_matches:
                        options = [{'key': m[0], 'text': _clean_content(m[1])} for m in option_matches]
                    else:
                        # 格式2: （A）选项 或 （）选项（习概格式）
                        option_matches = re.findall(r'（([A-G]?)）\s*(.+?)(?=（[A-G]?）|$)', option_text)
                        if option_matches:
                            letters = 'ABCDEFGH'
                            for idx, m in enumerate(option_matches):
                                key = m[0] if m[0] else (letters[idx] if idx < len(letters) else str(idx))
                                options.append({'key': key, 'text': _clean_content(m[1])})

                # 清理题干中的空括号和末尾标点
                q_content = q_content.replace('（ ）', '').replace('()', '').strip()
                q_content = re.sub(r'[，,。．、\s]+$', '', q_content).strip()

                # 提取答案
                answer = ''
                if answer_line_idx is not None and answer_line_idx < len(lines):
                    ans_line = lines[answer_line_idx].strip()
                    answer_match = re.search(r'答案[：:]\s*([A-G]+)', ans_line)
                    if answer_match:
                        answer = answer_match.group(1).strip()

                i = answer_line_idx if answer_line_idx is not None else (j - 1)

                # 验证答案：选项字母必须在提取的选项中存在
                if answer and options:
                    opt_keys = {o['key'] for o in options}
                    if any(letter not in opt_keys for letter in answer):
                        answer = ''  # 答案引用不存在的选项，视为无效

                questions.append({
                    'type': current_type,
                    'content': q_content,
                    'options': options,
                    'answer': answer
                })

            elif current_type == 'blank':
                # === 填空题 ===
                content_parts = [q_start]
                j = i + 1
                answer_line_idx = None

                while j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue
                    if _is_new_question(next_line):
                        break
                    if re.match(r'^【', next_line) or _is_section_header(next_line):
                        break
                    if '答案' in next_line:
                        answer_line_idx = j
                        j += 1
                        break
                    content_parts.append(next_line)
                    j += 1

                full_content = _clean_content(' '.join(content_parts))

                # 从内容中提取括号内的答案
                answers = re.findall(r'（(.+?)）', full_content)
                if not answers:
                    answers = re.findall(r'\((.+?)\)', full_content)

                if answers:
                    clean_content = re.sub(r'（.+?）', '____', full_content)
                    clean_content = re.sub(r'\(.+?\)', '____', clean_content)
                    answer = '、'.join(a.strip() for a in answers)
                else:
                    clean_content = full_content
                    answer = ''

                # 如果答案行有内容，也尝试提取
                if not answer and answer_line_idx is not None:
                    ans_line = lines[answer_line_idx].strip()
                    ans_content = re.search(r'答案[：:]\s*(.+)', ans_line)
                    if ans_content:
                        answer = ans_content.group(1).strip()

                i = answer_line_idx if answer_line_idx is not None else (j - 1)

                questions.append({
                    'type': 'blank',
                    'content': clean_content,
                    'options': None,
                    'answer': answer
                })

            elif current_type == 'judge':
                # === 判断题 ===
                content_parts = [q_start]
                answer = ''

                # 检查题干内联答案
                if '（√）' in q_start or '(√)' in q_start:
                    answer = '√'
                    q_start = q_start.replace('（√）', '').replace('(√)', '').strip()
                elif '（×）' in q_start or '(×)' in q_start:
                    answer = '×'
                    q_start = q_start.replace('（×）', '').replace('(×)', '').strip()

                j = i + 1

                while j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue
                    if _is_new_question(next_line):
                        break
                    if re.match(r'^【', next_line) or _is_section_header(next_line):
                        break
                    # 答案行
                    if '答案' in next_line:
                        if not answer:
                            if '√' in next_line:
                                answer = '√'
                            elif '×' in next_line:
                                answer = '×'
                        j += 1
                        break
                    # 独立 √ / × 行
                    if next_line.strip() in ('√', '×') and not answer:
                        answer = next_line.strip()
                        j += 1
                        break
                    # 题干续行
                    content_parts.append(next_line)
                    j += 1

                q_content = _clean_content(' '.join(content_parts))

                i = j - 1

                questions.append({
                    'type': 'judge',
                    'content': q_content,
                    'options': None,
                    'answer': answer
                })

        i += 1

    return questions


def _question_key(q):
    """生成题目的指纹，用于判断内容是否变化"""
    opt_str = str(sorted(q['options'], key=lambda x: x['key'])) if q['options'] else ''
    return f"{q['type']}|{q['content']}|{opt_str}|{q['answer']}"


def _chapter_sort_key(filename):
    """提取章节序号用于排序，导论排最前"""
    name = os.path.splitext(filename)[0]
    if '导论' in name:
        return 0
    m = re.search(r'第(\d+)章', name)
    if m:
        return int(m.group(1))
    m = re.search(r'^(\d+)', name)
    if m:
        return int(m.group(1))
    return 999


def _get_question_files(dirpath):
    """获取目录下需要导入的题库文件列表，按章节顺序排列"""
    files = os.listdir(dirpath)
    result = []
    for filename in files:
        if not filename.endswith(('.txt', '.pdf')):
            continue
        if filename in SKIP_FILES:
            continue
        # 马原目录：只导入主文件，跳过分离的判断题/单选题等分文件
        dir_name = os.path.basename(dirpath)
        if dir_name == 'output_mayuan' and filename != MAYUAN_MAIN_FILE:
            continue
        result.append(filename)
    result.sort(key=_chapter_sort_key)
    return result


def import_full(subject_name, dirpath):
    """全量导入：重新导入题目，保留做题记录"""
    if not os.path.isdir(dirpath):
        return {'error': f'目录不存在: {dirpath}'}

    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        subject = Subject(name=subject_name)
        db.session.add(subject)
        db.session.commit()

    # 删除该科目下旧数据（保留有做题记录的题目）
    chapters = Chapter.query.filter_by(subject_id=subject.id).all()
    chapter_ids = [ch.id for ch in chapters]
    if chapter_ids:
        LastPosition.query.filter(LastPosition.chapter_id.in_(chapter_ids)).delete(synchronize_session=False)
        question_ids = [q.id for q in Question.query.filter(Question.chapter_id.in_(chapter_ids)).all()]
        if question_ids:
            # 只删没有做题记录的题目
            questions_with_records = set(
                r.question_id for r in Record.query.filter(Record.question_id.in_(question_ids)).all()
            )
            safe_ids = [qid for qid in question_ids if qid not in questions_with_records]
            if safe_ids:
                Favorite.query.filter(Favorite.question_id.in_(safe_ids)).delete(synchronize_session=False)
                Progress.query.filter(Progress.question_id.in_(safe_ids)).delete(synchronize_session=False)
                Question.query.filter(Question.id.in_(safe_ids)).delete(synchronize_session=False)
        Chapter.query.filter(Chapter.id.in_(chapter_ids)).delete(synchronize_session=False)
    db.session.commit()

    # 导入
    imported = 0
    for filename in _get_question_files(dirpath):
        filepath = os.path.join(dirpath, filename)
        chapter_name = os.path.splitext(filename)[0]

        max_order = db.session.query(db.func.max(Chapter.sort_order)).filter_by(subject_id=subject.id).scalar() or 0
        chapter = Chapter(subject_id=subject.id, name=chapter_name, sort_order=max_order + 1)
        db.session.add(chapter)
        db.session.flush()

        questions = parse_txt_file(filepath)
        for idx, q in enumerate(questions, 1):
            db.session.add(Question(
                chapter_id=chapter.id, type=q['type'], content=q['content'],
                options=q['options'], answer=q['answer'] or '', sort_order=idx
            ))
            imported += 1

    db.session.commit()
    return {'subject': subject_name, 'imported': imported, 'mode': 'full'}


def import_incremental(subject_name, dirpath):
    """增量导入：对比差异，只更新变化的部分，保留做题记录"""
    if not os.path.isdir(dirpath):
        return {'error': f'目录不存在: {dirpath}'}

    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        subject = Subject(name=subject_name)
        db.session.add(subject)
        db.session.commit()

    # 建立旧章节索引 {章节名: chapter}
    old_chapters = {ch.name: ch for ch in Chapter.query.filter_by(subject_id=subject.id).all()}
    new_file_names = {_get_question_name(f): f for f in _get_question_files(dirpath)}

    added_chapters = 0
    updated_chapters = 0
    deleted_chapters = 0
    added_questions = 0
    updated_questions = 0
    deleted_questions = 0
    unchanged_questions = 0

    # 处理新文件（新增或更新章节）
    for filename in _get_question_files(dirpath):
        filepath = os.path.join(dirpath, filename)
        chapter_name = os.path.splitext(filename)[0]

        if chapter_name in old_chapters:
            # 章节已存在 → 增量更新题目
            chapter = old_chapters[chapter_name]
            a, u, d, n = _sync_chapter_questions(chapter, filepath)
            added_questions += a
            updated_questions += u
            deleted_questions += d
            unchanged_questions += n
            updated_chapters += 1
        else:
            # 新章节 → 创建
            max_order = db.session.query(db.func.max(Chapter.sort_order)).filter_by(subject_id=subject.id).scalar() or 0
            chapter = Chapter(subject_id=subject.id, name=chapter_name, sort_order=max_order + 1)
            db.session.add(chapter)
            db.session.flush()

            questions = parse_txt_file(filepath)
            for idx, q in enumerate(questions, 1):
                db.session.add(Question(
                    chapter_id=chapter.id, type=q['type'], content=q['content'],
                    options=q['options'], answer=q['answer'] or '', sort_order=idx
                ))
                added_questions += 1
            added_chapters += 1

    # 删除不再存在的章节
    for name, chapter in old_chapters.items():
        if name not in new_file_names:
            _delete_chapter_data(chapter)
            deleted_chapters += 1

    db.session.commit()
    return {
        'subject': subject_name,
        'chapters': {'added': added_chapters, 'updated': updated_chapters, 'deleted': deleted_chapters},
        'questions': {'added': added_questions, 'updated': updated_questions, 'deleted': deleted_questions, 'unchanged': unchanged_questions},
        'mode': 'incremental'
    }


def _get_question_name(filename):
    """从文件名提取章节名"""
    return os.path.splitext(filename)[0]


def _sync_chapter_questions(chapter, filepath):
    """同步一个章节的题目，返回 (added, updated, deleted, unchanged)"""
    new_questions = parse_txt_file(filepath)
    old_questions = Question.query.filter_by(chapter_id=chapter.id).order_by(Question.sort_order).all()

    # 按 sort_order 建立旧题目索引
    old_by_order = {q.sort_order: q for q in old_questions}

    added = 0
    updated = 0
    deleted = 0
    unchanged = 0

    seen_orders = set()
    for idx, q in enumerate(new_questions, 1):
        seen_orders.add(idx)

        new_key = _question_key(q)
        old_q = old_by_order.get(idx)

        if old_q is None:
            # 新增题目
            db.session.add(Question(
                chapter_id=chapter.id, type=q['type'], content=q['content'],
                options=q['options'], answer=q['answer'] or '', sort_order=idx
            ))
            added += 1
        else:
            old_key = _question_key({
                'type': old_q.type, 'content': old_q.content,
                'options': old_q.options, 'answer': old_q.answer
            })
            if old_key != new_key:
                # 内容变化 → 更新题目，保留做题记录
                old_q.type = q['type']
                old_q.content = q['content']
                old_q.options = q['options']
                old_q.answer = q['answer'] or ''
                updated += 1
            else:
                unchanged += 1

    # 删除文件中不再存在的题目（有做题记录的保留）
    for order, old_q in old_by_order.items():
        if order not in seen_orders:
            has_records = Record.query.filter_by(question_id=old_q.id).first() is not None
            if has_records:
                # 有记录的题不删，保留用户的做题数据
                unchanged += 1
            else:
                Favorite.query.filter_by(question_id=old_q.id).delete()
                Progress.query.filter_by(question_id=old_q.id).delete()
                db.session.delete(old_q)
                deleted += 1

    return added, updated, deleted, unchanged


def _delete_chapter_data(chapter):
    """删除一个章节及其所有关联数据"""
    # 先删除 last_position 中引用该章节的记录
    LastPosition.query.filter(LastPosition.chapter_id == chapter.id).delete(synchronize_session=False)

    question_ids = [q.id for q in Question.query.filter_by(chapter_id=chapter.id).all()]
    if question_ids:
        Record.query.filter(Record.question_id.in_(question_ids)).delete(synchronize_session=False)
        Progress.query.filter(Progress.question_id.in_(question_ids)).delete(synchronize_session=False)
        Favorite.query.filter(Favorite.question_id.in_(question_ids)).delete(synchronize_session=False)
        Question.query.filter(Question.chapter_id == chapter.id).delete(synchronize_session=False)
    db.session.delete(chapter)


def import_from_docx(subject_name, filepath, mode='full'):
    """从Word文件导入题库

    Args:
        subject_name: 科目名称
        filepath: Word文件路径
        mode: 'full' (全量) 或 'incremental' (增量)
    """
    if not os.path.isfile(filepath):
        return {'error': f'文件不存在: {filepath}'}

    # 解析Word文件
    chapters_data = parse_docx_to_chapters(filepath)
    if not chapters_data:
        return {'error': '未能从Word文件中解析出任何题目'}

    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        subject = Subject(name=subject_name)
        db.session.add(subject)
        db.session.commit()

    if mode == 'full':
        # === 备份刷题记录（按题目内容匹配） ===
        old_qs = Question.query.join(Chapter).filter(Chapter.subject_id == subject.id).all()
        old_records = []
        old_progress = []
        old_favs = []
        old_lastpos = []
        if old_qs:
            old_ids = [q.id for q in old_qs]
            # 按题目内容建立索引（取前40字作为匹配key）
            old_content_map = {q.id: q.content[:40] for q in old_qs}

            records = Record.query.filter(Record.question_id.in_(old_ids)).all()
            for r in records:
                key = old_content_map.get(r.question_id, '')
                old_records.append((key, r.user_answer, r.is_correct, r.created_at))

            progress = Progress.query.filter(Progress.question_id.in_(old_ids)).all()
            for p in progress:
                key = old_content_map.get(p.question_id, '')
                old_progress.append((key, p.status, p.last_attempt_at, p.attempt_count))

            favs = Favorite.query.filter(Favorite.question_id.in_(old_ids)).all()
            for f in favs:
                key = old_content_map.get(f.question_id, '')
                old_favs.append((key, f.created_at))

            lastpos = LastPosition.query.filter(LastPosition.subject_id == subject.id).all()
            for lp in lastpos:
                old_lastpos.append((lp.chapter_id, lp.question_index, lp.updated_at))

        print(f'📦 备份: 记录{len(old_records)}条, 进度{len(old_progress)}条, 收藏{len(old_favs)}条')

        # 删除该科目下所有旧数据
        old_chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        for chapter in old_chapters:
            _delete_chapter_data(chapter)
        db.session.commit()

        # 导入新数据
        imported = 0
        skipped = 0
        new_qs_by_content = {}  # content[:40] -> Question
        for chapter_name, questions in chapters_data.items():
            # 创建章节
            max_order = db.session.query(db.func.max(Chapter.sort_order)).filter_by(
                subject_id=subject.id).scalar() or 0
            chapter = Chapter(
                subject_id=subject.id,
                name=chapter_name,
                sort_order=max_order + 1
            )
            db.session.add(chapter)
            db.session.flush()

            # 导入题目
            for idx, q in enumerate(questions, 1):
                if not q['answer']:
                    skipped += 1
                new_q = Question(
                    chapter_id=chapter.id,
                    type=q['type'],
                    content=q['content'],
                    options=q['options'],
                    answer=q['answer'] or '',
                    sort_order=idx
                )
                db.session.add(new_q)
                db.session.flush()
                new_qs_by_content[q['content'][:40]] = new_q
                imported += 1

        db.session.commit()

        # === 恢复刷题记录 ===
        restored_rec = 0
        for key, user_answer, is_correct, created_at in old_records:
            if key in new_qs_by_content:
                db.session.add(Record(
                    question_id=new_qs_by_content[key].id,
                    user_answer=user_answer,
                    is_correct=is_correct,
                    created_at=created_at
                ))
                restored_rec += 1
            else:
                # 模糊匹配
                for nk, nq in new_qs_by_content.items():
                    if key[:25] in nk or nk[:25] in key:
                        db.session.add(Record(
                            question_id=nq.id,
                            user_answer=user_answer,
                            is_correct=is_correct,
                            created_at=created_at
                        ))
                        restored_rec += 1
                        break

        restored_prog = 0
        for key, status, last_attempt_at, attempt_count in old_progress:
            if key in new_qs_by_content:
                db.session.add(Progress(
                    question_id=new_qs_by_content[key].id,
                    status=status,
                    last_attempt_at=last_attempt_at,
                    attempt_count=attempt_count
                ))
                restored_prog += 1
            else:
                for nk, nq in new_qs_by_content.items():
                    if key[:25] in nk or nk[:25] in key:
                        db.session.add(Progress(
                            question_id=nq.id,
                            status=status,
                            last_attempt_at=last_attempt_at,
                            attempt_count=attempt_count
                        ))
                        restored_prog += 1
                        break

        restored_fav = 0
        for key, created_at in old_favs:
            if key in new_qs_by_content:
                db.session.add(Favorite(
                    question_id=new_qs_by_content[key].id,
                    created_at=created_at
                ))
                restored_fav += 1
            else:
                for nk, nq in new_qs_by_content.items():
                    if key[:25] in nk or nk[:25] in key:
                        db.session.add(Favorite(
                            question_id=nq.id,
                            created_at=created_at
                        ))
                        restored_fav += 1
                        break

        db.session.commit()
        print(f'♻️  恢复: 记录{restored_rec}条, 进度{restored_prog}条, 收藏{restored_fav}条')

        return {
            'subject': subject_name,
            'imported': imported,
            'skipped': skipped,
            'chapters': len(chapters_data),
            'mode': 'full',
            'restored': {
                'records': restored_rec,
                'progress': restored_prog,
                'favorites': restored_fav
            }
        }
    else:
        # 增量导入
        old_chapters = {ch.name: ch for ch in Chapter.query.filter_by(subject_id=subject.id).all()}

        added_chapters = 0
        updated_chapters = 0
        added_questions = 0
        updated_questions = 0
        unchanged_questions = 0

        for chapter_name, questions in chapters_data.items():
            if chapter_name in old_chapters:
                # 更新现有章节
                chapter = old_chapters[chapter_name]
                a, u, n = _sync_chapter_questions_from_list(chapter, questions)
                added_questions += a
                updated_questions += u
                unchanged_questions += n
                updated_chapters += 1
            else:
                # 创建新章节
                max_order = db.session.query(db.func.max(Chapter.sort_order)).filter_by(
                    subject_id=subject.id).scalar() or 0
                chapter = Chapter(
                    subject_id=subject.id,
                    name=chapter_name,
                    sort_order=max_order + 1
                )
                db.session.add(chapter)
                db.session.flush()

                for idx, q in enumerate(questions, 1):
                    db.session.add(Question(
                        chapter_id=chapter.id,
                        type=q['type'],
                        content=q['content'],
                        options=q['options'],
                        answer=q['answer'] or '',
                        sort_order=idx
                    ))
                    added_questions += 1
                added_chapters += 1

        # 删除不再存在的章节
        for name, chapter in old_chapters.items():
            if name not in chapters_data:
                _delete_chapter_data(chapter)

        db.session.commit()
        return {
            'subject': subject_name,
            'chapters': {'added': added_chapters, 'updated': updated_chapters},
            'questions': {'added': added_questions, 'updated': updated_questions, 'unchanged': unchanged_questions},
            'mode': 'incremental'
        }


def _sync_chapter_questions_from_list(chapter, new_questions):
    """同步一个章节的题目（从列表），返回 (added, updated, unchanged)"""
    old_questions = Question.query.filter_by(chapter_id=chapter.id).order_by(Question.sort_order).all()
    old_by_order = {q.sort_order: q for q in old_questions}

    added = 0
    updated = 0
    unchanged = 0

    seen_orders = set()
    for idx, q in enumerate(new_questions, 1):
        seen_orders.add(idx)
        new_key = _question_key(q)
        old_q = old_by_order.get(idx)

        if old_q is None:
            # 新增题目
            db.session.add(Question(
                chapter_id=chapter.id,
                type=q['type'],
                content=q['content'],
                options=q['options'],
                answer=q['answer'] or '',
                sort_order=idx
            ))
            added += 1
        else:
            old_key = _question_key({
                'type': old_q.type,
                'content': old_q.content,
                'options': old_q.options,
                'answer': old_q.answer
            })
            if old_key != new_key:
                # 内容变化 → 更新题目，保留做题记录
                old_q.type = q['type']
                old_q.content = q['content']
                old_q.options = q['options']
                old_q.answer = q['answer'] or ''
                updated += 1
            else:
                unchanged += 1

    # 删除文件中不再存在的题目（有做题记录的保留）
    for order, old_q in old_by_order.items():
        if order not in seen_orders:
            has_records = Record.query.filter_by(question_id=old_q.id).first() is not None
            if has_records:
                unchanged += 1
            else:
                Favorite.query.filter_by(question_id=old_q.id).delete()
                Progress.query.filter_by(question_id=old_q.id).delete()
                db.session.delete(old_q)

    return added, updated, unchanged


@import_bp.route('/import', methods=['POST'])
def import_all():
    """
    导入题库
    body: {
        "mode": "full" | "incremental",
        "source": "txt" | "docx" | "all"  // 可选，默认 "all"
    }
      - full: 清空所有旧数据后重新导入
      - incremental: 增量更新，只更新变化的题目，保留做题记录
      - source: 导入来源，txt=从output目录，docx=从Word文件，all=两者都导入
    """
    data = request.get_json() or {}
    mode = data.get('mode', 'incremental')
    source = data.get('source', 'all')

    if mode not in ('full', 'incremental'):
        return jsonify({'code': 1, 'message': 'mode 必须为 full 或 incremental'}), 400
    if source not in ('txt', 'docx', 'all'):
        return jsonify({'code': 1, 'message': 'source 必须为 txt、docx 或 all'}), 400

    results = []

    # 从TXT文件导入
    if source in ('txt', 'all'):
        for subject_name, dirpath in OUTPUT_DIRS.items():
            if mode == 'full':
                result = import_full(subject_name, dirpath)
            else:
                result = import_incremental(subject_name, dirpath)
            results.append(result)

    # 从Word文件导入
    if source in ('docx', 'all'):
        for subject_name, filepath in DOCX_FILES.items():
            result = import_from_docx(subject_name, filepath, mode)
            results.append(result)

    return jsonify({
        'code': 0,
        'data': results,
        'message': '导入完成'
    })
