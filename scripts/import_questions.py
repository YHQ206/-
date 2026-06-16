"""题库导入脚本 - 从output目录或Word文件导入题库"""
import os
import sys

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from models import db, Subject, Chapter, Question, Record, Progress, Favorite
from routes.import_routes import parse_txt_file, _get_question_files, _chapter_sort_key, import_from_docx

# 输出目录配置（使用与API相同的配置）
OUTPUT_DIRS = {
    '习概': os.path.join(os.path.dirname(__file__), '..', 'output_xigai_v10'),
    '马原': os.path.join(os.path.dirname(__file__), '..', 'output_mayuan'),
}

# Word文件配置
DOCX_FILES = {
    '习概': os.path.join(os.path.dirname(__file__), '..', '客观题题库及答案 .docx'),
}

# 马原只导入主文件
MAYUAN_MAIN_FILE = '全部题目.txt'


def import_subject(subject_name, dirpath):
    """导入一个科目的所有题目"""
    if not os.path.isdir(dirpath):
        print(f'❌ 目录不存在: {dirpath}')
        return

    app = create_app()
    with app.app_context():
        # 获取或创建科目
        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            subject = Subject(name=subject_name)
            db.session.add(subject)
            db.session.commit()
            print(f'📁 创建科目: {subject_name}')

        # 删除旧数据
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        chapter_ids = [ch.id for ch in chapters]
        if chapter_ids:
            question_ids = [q.id for q in Question.query.filter(Question.chapter_id.in_(chapter_ids)).all()]
            if question_ids:
                Record.query.filter(Record.question_id.in_(question_ids)).delete(synchronize_session=False)
                Progress.query.filter(Progress.question_id.in_(question_ids)).delete(synchronize_session=False)
                Favorite.query.filter(Favorite.question_id.in_(question_ids)).delete(synchronize_session=False)
                Question.query.filter(Question.chapter_id.in_(chapter_ids)).delete(synchronize_session=False)
            Chapter.query.filter(Chapter.id.in_(chapter_ids)).delete(synchronize_session=False)
        db.session.commit()

        # 获取文件列表
        dir_name = os.path.basename(dirpath)
        files = os.listdir(dirpath)
        result = []
        for filename in files:
            if not filename.endswith('.txt'):
                continue
            if filename in ('统计.txt', '异常清单.txt', '导出说明.txt'):
                continue
            if filename in ('判断题.txt', '单项选择题.txt', 'mayuan_output.txt'):
                continue
            # 马原目录只导入主文件
            if dir_name == 'output_mayuan' and filename != MAYUAN_MAIN_FILE:
                continue
            result.append(filename)
        result.sort(key=_chapter_sort_key)

        total_imported = 0
        total_skipped = 0

        for filename in result:
            filepath = os.path.join(dirpath, filename)
            chapter_name = os.path.splitext(filename)[0]

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

            # 解析并导入
            questions = parse_txt_file(filepath)
            imported = 0
            skipped = 0
            for idx, q in enumerate(questions, 1):
                if not q['answer']:
                    skipped += 1
                db.session.add(Question(
                    chapter_id=chapter.id,
                    type=q['type'],
                    content=q['content'],
                    options=q['options'],
                    answer=q['answer'] or '',
                    sort_order=idx
                ))
                imported += 1

            db.session.commit()
            total_imported += imported
            total_skipped += skipped

            status = '✅' if skipped == 0 else f'⚠️ ({skipped} skipped)'
            print(f'  {chapter_name}: {imported} questions {status}')

        print(f'\n📊 {subject_name} total: {total_imported} imported, {total_skipped} skipped (no answer)')


def import_docx_subject(subject_name, filepath):
    """从Word文件导入一个科目的所有题目"""
    if not os.path.isfile(filepath):
        print(f'❌ 文件不存在: {filepath}')
        return

    app = create_app()
    with app.app_context():
        print(f'📚 从Word文件导入 {subject_name}: {filepath}')
        result = import_from_docx(subject_name, filepath, mode='full')

        if 'error' in result:
            print(f'❌ 导入失败: {result["error"]}')
            return

        print(f'✅ 导入完成:')
        print(f'  章节数: {result["chapters"]}')
        print(f'  题目数: {result["imported"]}')
        print(f'  跳过数: {result["skipped"]} (无答案)')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='导入题库到数据库')
    parser.add_argument('--subject', choices=['习概', '马原', 'all'],
                        default='all', help='要导入的科目')
    parser.add_argument('--dir', help='自定义题库目录路径（覆盖默认配置）')
    parser.add_argument('--docx', action='store_true', help='从Word文件导入')
    parser.add_argument('--file', help='指定Word文件路径')

    args = parser.parse_args()

    if args.docx or args.file:
        # 从Word文件导入
        if args.file:
            # 指定文件路径
            subject_name = args.subject if args.subject != 'all' else '习概'
            import_docx_subject(subject_name, args.file)
        else:
            # 使用默认Word文件配置
            if args.subject == 'all':
                for name, filepath in DOCX_FILES.items():
                    import_docx_subject(name, filepath)
            else:
                if args.subject in DOCX_FILES:
                    import_docx_subject(args.subject, DOCX_FILES[args.subject])
                else:
                    print(f'未知科目: {args.subject}')
    elif args.dir:
        # 自定义目录
        subject_name = args.subject if args.subject != 'all' else '未知'
        import_subject(subject_name, args.dir)
    else:
        if args.subject == 'all':
            for name, dirpath in OUTPUT_DIRS.items():
                print(f'\n📚 导入 {name} (from {dirpath})')
                import_subject(name, dirpath)
        else:
            if args.subject in OUTPUT_DIRS:
                print(f'📚 导入 {args.subject}')
                import_subject(args.subject, OUTPUT_DIRS[args.subject])
            else:
                print(f'未知科目: {args.subject}')
