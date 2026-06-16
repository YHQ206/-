from flask import Blueprint, jsonify, request
from models import db, Subject, Chapter, Question, Progress, Record
from datetime import datetime, timedelta

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/stats/overview', methods=['GET'])
def get_overview():
    """获取总体统计"""
    subject_id = request.args.get('subject_id', type=int)

    query = Question.query
    if subject_id:
        query = query.join(Chapter).filter(Chapter.subject_id == subject_id)

    total = query.count()

    # 已做题数
    done_query = db.session.query(Progress).join(Question)
    if subject_id:
        done_query = done_query.join(Chapter).filter(Chapter.subject_id == subject_id)
    done = done_query.filter(Progress.status != 'unanswered').count()

    # 正确数
    correct = done_query.filter(Progress.status == 'correct').count()

    # 错题数
    wrong = done_query.filter(Progress.status == 'wrong').count()

    # 收藏数
    from models import Favorite
    fav_query = db.session.query(Favorite).join(Question)
    if subject_id:
        fav_query = fav_query.join(Chapter).filter(Chapter.subject_id == subject_id)
    favorites = fav_query.count()

    # 今日做题数
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_query = db.session.query(Record).join(Question).filter(Record.created_at >= today_start)
    if subject_id:
        today_query = today_query.join(Chapter).filter(Chapter.subject_id == subject_id)
    today_count = today_query.count()

    return jsonify({
        'code': 0,
        'data': {
            'total': total,
            'done': done,
            'correct': correct,
            'wrong': wrong,
            'favorites': favorites,
            'accuracy': round(correct / done * 100, 1) if done > 0 else 0,
            'today_count': today_count
        },
        'message': 'success'
    })


@stats_bp.route('/stats/chapters', methods=['GET'])
def get_chapter_stats():
    """获取各章节统计"""
    subject_id = request.args.get('subject_id', type=int)

    query = Chapter.query
    if subject_id:
        query = query.filter_by(subject_id=subject_id)

    chapters = query.order_by(Chapter.sort_order).all()

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
            'correct': correct,
            'accuracy': round(correct / done * 100, 1) if done > 0 else 0
        })

    return jsonify({
        'code': 0,
        'data': result,
        'message': 'success'
    })
