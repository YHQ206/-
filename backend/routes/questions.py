from flask import Blueprint, jsonify, request
from models import db, Subject, Chapter, Question, Favorite, Progress, LastPosition
import random
import json

questions_bp = Blueprint('questions', __name__)


@questions_bp.route('/subjects', methods=['GET'])
def get_subjects():
    """获取科目列表"""
    subjects = Subject.query.all()
    return jsonify({
        'code': 0,
        'data': [{'id': s.id, 'name': s.name} for s in subjects],
        'message': 'success'
    })


@questions_bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
def get_chapters(subject_id):
    """获取科目下的章节列表（带进度统计）"""
    chapters = Chapter.query.filter_by(subject_id=subject_id).order_by(Chapter.sort_order).all()
    result = []
    for ch in chapters:
        total = Question.query.filter_by(chapter_id=ch.id).count()
        done = db.session.query(Progress).join(Question).filter(
            Question.chapter_id == ch.id,
            Progress.status != 'unanswered'
        ).count()
        correct = db.session.query(Progress).join(Question).filter(
            Question.chapter_id == ch.id,
            Progress.status == 'correct'
        ).count()
        result.append({
            'id': ch.id,
            'name': ch.name,
            'total': total,
            'done': done,
            'correct': correct
        })
    return jsonify({
        'code': 0,
        'data': result,
        'message': 'success'
    })


@questions_bp.route('/chapters/<int:chapter_id>/questions', methods=['GET'])
def get_chapter_questions(chapter_id):
    """获取章节题目列表（带状态）"""
    chapter = Chapter.query.get(chapter_id)
    questions = Question.query.filter_by(chapter_id=chapter_id).order_by(Question.sort_order).all()
    result = []
    for q in questions:
        progress = Progress.query.filter_by(question_id=q.id).first()
        favorite = Favorite.query.filter_by(question_id=q.id).first()
        result.append({
            'id': q.id,
            'type': q.type,
            'content': q.content,
            'status': progress.status if progress else 'unanswered',
            'is_favorite': favorite is not None
        })
    return jsonify({
        'code': 0,
        'data': {
            'chapter_name': chapter.name if chapter else '',
            'questions': result
        },
        'message': 'success'
    })


@questions_bp.route('/questions/<int:question_id>', methods=['GET'])
def get_question_detail(question_id):
    """获取题目详情"""
    q = Question.query.get_or_404(question_id)
    progress = Progress.query.filter_by(question_id=q.id).first()
    favorite = Favorite.query.filter_by(question_id=q.id).first()
    # options stored as JSON string, parse to list
    options = q.options
    if isinstance(options, str):
        try:
            options = json.loads(options)
        except (json.JSONDecodeError, TypeError):
            options = []
    return jsonify({
        'code': 0,
        'data': {
            'id': q.id,
            'type': q.type,
            'content': q.content,
            'options': options,
            'answer': q.answer,
            'explanation': q.explanation,
            'status': progress.status if progress else 'unanswered',
            'attempt_count': progress.attempt_count if progress else 0,
            'is_favorite': favorite is not None
        },
        'message': 'success'
    })


@questions_bp.route('/questions/random', methods=['GET'])
def get_random_questions():
    """随机获取题目"""
    subject_id = request.args.get('subject_id', type=int)
    count = request.args.get('count', 10, type=int)
    only_unanswered = request.args.get('only_unanswered', 'false') == 'true'

    query = Question.query
    if subject_id:
        query = query.join(Chapter).filter(Chapter.subject_id == subject_id)

    if only_unanswered:
        answered_ids = db.session.query(Progress.question_id).filter(
            Progress.status != 'unanswered'
        ).subquery()
        query = query.filter(~Question.id.in_(answered_ids))

    questions = query.all()
    if len(questions) > count:
        questions = random.sample(questions, count)

    result = []
    for q in questions:
        progress = Progress.query.filter_by(question_id=q.id).first()
        favorite = Favorite.query.filter_by(question_id=q.id).first()
        opts = q.options
        if isinstance(opts, str):
            try:
                opts = json.loads(opts)
            except (json.JSONDecodeError, TypeError):
                opts = []
        result.append({
            'id': q.id,
            'type': q.type,
            'content': q.content,
            'options': opts,
            'answer': q.answer,
            'status': progress.status if progress else 'unanswered',
            'is_favorite': favorite is not None
        })

    return jsonify({
        'code': 0,
        'data': result,
        'message': 'success'
    })


@questions_bp.route('/questions/<int:question_id>/answer', methods=['POST'])
def submit_answer(question_id):
    """提交答案"""
    q = Question.query.get_or_404(question_id)
    data = request.get_json()
    user_answer = data.get('answer', '').strip()

    # 无答案的题不允许提交
    if not q.answer:
        return jsonify({'code': 1, 'message': '该题暂无答案', 'data': None})

    # 判断是否正确
    if q.type == 'multiple':
        # 多选题：全对才算对
        # 清理答案格式，支持 "ABC"、"A,B,C"、"A B C" 等格式
        clean_answer = lambda s: set(s.upper().replace(',', '').replace(' ', '').replace('、', ''))
        correct_set = clean_answer(q.answer)
        user_set = clean_answer(user_answer)
        is_correct = correct_set == user_set
    elif q.type == 'judge':
        # 判断题
        is_correct = user_answer.strip() == q.answer.strip()
    elif q.type == 'blank':
        # 填空题：支持多个答案用顿号分隔，任意顺序
        correct_answers = [a.strip() for a in q.answer.replace('、', ',').replace('，', ',').split(',')]
        user_answers = [a.strip() for a in user_answer.replace('、', ',').replace('，', ',').split(',')]
        is_correct = sorted(correct_answers) == sorted(user_answers)
    else:
        # 单选题
        is_correct = user_answer.upper().strip() == q.answer.upper().strip()

    # 保存做题记录
    from models import Record
    record = Record(
        question_id=q.id,
        user_answer=user_answer,
        is_correct=is_correct
    )
    db.session.add(record)

    # 更新进度
    progress = Progress.query.filter_by(question_id=q.id).first()
    if not progress:
        progress = Progress(question_id=q.id, attempt_count=0)
        db.session.add(progress)
    progress.status = 'correct' if is_correct else 'wrong'
    progress.attempt_count = (progress.attempt_count or 0) + 1
    from datetime import datetime
    progress.last_attempt_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'code': 0,
        'data': {
            'is_correct': is_correct,
            'correct_answer': q.answer,
            'explanation': q.explanation
        },
        'message': 'success'
    })


@questions_bp.route('/favorites/<int:question_id>', methods=['POST'])
def add_favorite(question_id):
    """添加收藏"""
    Question.query.get_or_404(question_id)
    existing = Favorite.query.filter_by(question_id=question_id).first()
    if existing:
        return jsonify({'code': 1, 'message': '已收藏'})
    fav = Favorite(question_id=question_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({'code': 0, 'message': '收藏成功'})


@questions_bp.route('/favorites/<int:question_id>', methods=['DELETE'])
def remove_favorite(question_id):
    """取消收藏"""
    fav = Favorite.query.filter_by(question_id=question_id).first()
    if not fav:
        return jsonify({'code': 1, 'message': '未收藏'})
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'code': 0, 'message': '取消收藏'})


@questions_bp.route('/favorites', methods=['GET'])
def get_favorites():
    """获取收藏列表"""
    subject_id = request.args.get('subject_id', type=int)
    query = db.session.query(Favorite, Question).join(Question)
    if subject_id:
        query = query.join(Chapter).filter(Chapter.subject_id == subject_id)
    favorites = query.order_by(Favorite.created_at.desc()).all()

    result = []
    for fav, q in favorites:
        progress = Progress.query.filter_by(question_id=q.id).first()
        result.append({
            'id': q.id,
            'type': q.type,
            'content': q.content,
            'status': progress.status if progress else 'unanswered',
            'is_favorite': True
        })
    return jsonify({
        'code': 0,
        'data': result,
        'message': 'success'
    })


@questions_bp.route('/progress/last', methods=['GET'])
def get_last_position():
    """获取上次刷题位置"""
    subject_id = request.args.get('subject_id', type=int)
    if not subject_id:
        pos = LastPosition.query.order_by(LastPosition.updated_at.desc()).first()
    else:
        pos = LastPosition.query.filter_by(subject_id=subject_id).first()

    if not pos:
        return jsonify({'code': 0, 'data': None, 'message': '无记录'})

    return jsonify({
        'code': 0,
        'data': {
            'subject_id': pos.subject_id,
            'chapter_id': pos.chapter_id,
            'question_index': pos.question_index
        },
        'message': 'success'
    })


@questions_bp.route('/progress/save', methods=['POST'])
def save_position():
    """保存当前刷题位置"""
    data = request.get_json()
    subject_id = data.get('subject_id')
    chapter_id = data.get('chapter_id')
    question_index = data.get('question_index', 0)

    # 从 chapter 自动获取 subject_id
    if not subject_id and chapter_id:
        chapter = Chapter.query.get(chapter_id)
        if chapter:
            subject_id = chapter.subject_id

    if not subject_id:
        return jsonify({'code': 1, 'message': '缺少 subject_id'}), 400

    pos = LastPosition.query.filter_by(subject_id=subject_id).first()
    if not pos:
        pos = LastPosition(subject_id=subject_id)
        db.session.add(pos)
    pos.chapter_id = chapter_id
    pos.question_index = question_index
    from datetime import datetime
    pos.updated_at = datetime.utcnow()

    db.session.commit()
    return jsonify({'code': 0, 'message': '保存成功'})


@questions_bp.route('/progress', methods=['DELETE'])
def clear_all_progress():
    """清空进度和记录（支持按科目清除）"""
    from models import Record
    subject_id = request.args.get('subject_id', type=int)

    if subject_id:
        # 只清除指定科目的记录
        question_ids = db.session.query(Question.id).join(Chapter).filter(
            Chapter.subject_id == subject_id
        ).subquery()

        Record.query.filter(Record.question_id.in_(question_ids)).delete(synchronize_session=False)
        Progress.query.filter(Progress.question_id.in_(question_ids)).delete(synchronize_session=False)
        Favorite.query.filter(Favorite.question_id.in_(question_ids)).delete(synchronize_session=False)
        LastPosition.query.filter(LastPosition.subject_id == subject_id).delete()
    else:
        # 清除所有记录
        Record.query.delete()
        Progress.query.delete()
        Favorite.query.delete()
        LastPosition.query.delete()

    db.session.commit()
    return jsonify({'code': 0, 'message': '已清空记录'})
