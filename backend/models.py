from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, comment='科目名称')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chapters = db.relationship('Chapter', backref='subject', lazy=True)


class Chapter(db.Model):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False, comment='章节名称')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('Question', backref='chapter', lazy=True)


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    type = db.Column(db.Enum('single', 'multiple', 'blank', 'judge'), nullable=False)
    content = db.Column(db.Text, nullable=False, comment='题目内容')
    options = db.Column(db.JSON, comment='选项列表')
    answer = db.Column(db.String(500), nullable=False, comment='正确答案')
    explanation = db.Column(db.Text, comment='解析')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    records = db.relationship('Record', backref='question', lazy=True)
    progress = db.relationship('Progress', backref='question', uselist=False, lazy=True)
    favorite = db.relationship('Favorite', backref='question', uselist=False, lazy=True)


class Record(db.Model):
    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_answer = db.Column(db.String(500), comment='用户答案')
    is_correct = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Progress(db.Model):
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), unique=True, nullable=False)
    status = db.Column(db.Enum('unanswered', 'correct', 'wrong'), default='unanswered')
    last_attempt_at = db.Column(db.DateTime)
    attempt_count = db.Column(db.Integer, default=0)


class LastPosition(db.Model):
    """记录上次刷题位置"""
    __tablename__ = 'last_position'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    question_index = db.Column(db.Integer, default=0, comment='题目在章节中的索引')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
