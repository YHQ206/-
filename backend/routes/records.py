from flask import Blueprint, jsonify, request
from models import db, Question, Record, Progress, Chapter
from sqlalchemy import func

records_bp = Blueprint('records', __name__)


@records_bp.route('/records/wrong', methods=['GET'])
def get_wrong_questions():
    """获取错题列表（所有曾经答错过的题目，按状态分为待复习和已掌握）"""
    subject_id = request.args.get('subject_id', type=int)

    # 查询所有曾经答错过至少一次的题目
    wrong_question_ids = db.session.query(Record.question_id).filter(
        Record.is_correct == False
    ).distinct().subquery()

    query = db.session.query(Question, Progress).join(
        wrong_question_ids, Question.id == wrong_question_ids.c.question_id
    ).outerjoin(Progress, Progress.question_id == Question.id)

    if subject_id:
        query = query.join(Chapter).filter(Chapter.subject_id == subject_id)

    results = query.order_by(
        func.coalesce(Progress.last_attempt_at, Question.created_at).desc()
    ).all()

    # 一次查询获取所有错题的统计信息（错误次数 + 最后错误时间）
    wrong_stats = db.session.query(
        Record.question_id,
        func.count().label('wrong_count'),
        func.max(Record.created_at).label('last_wrong_time')
    ).filter(
        Record.is_correct == False
    ).group_by(Record.question_id).all()
    stats_map = {s.question_id: s for s in wrong_stats}

    data = []
    for q, p in results:
        stat = stats_map.get(q.id)
        current_status = p.status if p else 'unanswered'
        data.append({
            'id': q.id,
            'type': q.type,
            'content': q.content,
            'chapter_id': q.chapter_id,
            'attempt_count': stat.wrong_count if stat else 0,
            'last_attempt_at': stat.last_wrong_time.strftime('%Y-%m-%d %H:%M') if stat and stat.last_wrong_time else None,
            'status': current_status,
            'mastered': current_status == 'correct'  # 标记是否已掌握
        })

    return jsonify({
        'code': 0,
        'data': data,
        'message': 'success'
    })
