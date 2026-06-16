"""修复题库中选项解析错误的题目"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from models import db, Question


# 定义需要修复的题目
# 格式: {question_id: {'options': [...], 'answer': '...'}}
FIXES = {
    # ID=29: 选项A合并了A和B
    29: {
        'options': [
            {'key': 'A', 'text': '第一个百年奋斗目标'},
            {'key': 'B', 'text': '第二个百年奋斗目标'},
            {'key': 'C', 'text': '第三个百年奋斗目标'},
            {'key': 'D', 'text': '第四个百年奋斗目标'},
        ],
        'answer': 'B'
    },
    # ID=37: 选项A合并了A和B
    37: {
        'options': [
            {'key': 'A', 'text': '坚持改革开放'},
            {'key': 'B', 'text': '加强国际合作'},
            {'key': 'C', 'text': '构建人类命运共同体'},
            {'key': 'D', 'text': '深化经济体制改革'},
        ],
        'answer': 'C'
    },
    # ID=66: 所有选项合并成一个
    66: {
        'options': [
            {'key': 'A', 'text': '中国共产党的领导'},
            {'key': 'B', 'text': '政府的领导'},
            {'key': 'C', 'text': '民主党派的领导'},
            {'key': 'D', 'text': '中国特色社会主义'},
        ],
        'answer': 'A'
    },
    # ID=188: 所有选项合并成一个
    188: {
        'options': [
            {'key': 'A', 'text': '高质量发展'},
            {'key': 'B', 'text': '共同富裕'},
            {'key': 'C', 'text': '改革发展'},
            {'key': 'D', 'text': '收入分配'},
        ],
        'answer': 'C'
    },
    # ID=222: 多选题选项合并
    222: {
        'options': [
            {'key': 'A', 'text': '创新'},
            {'key': 'B', 'text': '协调'},
            {'key': 'C', 'text': '绿色'},
            {'key': 'D', 'text': '开放'},
            {'key': 'E', 'text': '共享'},
        ],
        'answer': 'ABCDE'
    },
    # ID=267: 选项A合并了A和B
    267: {
        'options': [
            {'key': 'A', 'text': '国际视野和全球化思维'},
            {'key': 'B', 'text': '良好的综合素质'},
            {'key': 'C', 'text': '扎实的专业知识和技能'},
            {'key': 'D', 'text': '良好的应变能力'},
        ],
        'answer': 'A'
    },
    # ID=305: 选项A合并了A和B
    305: {
        'options': [
            {'key': 'A', 'text': '国家安全'},
            {'key': 'B', 'text': '中华民族伟大复兴'},
            {'key': 'C', 'text': '维护民族地区长治久安'},
            {'key': 'D', 'text': '转变经济发展方式'},
        ],
        'answer': 'B'
    },
    # ID=392: 选项A合并了A和B
    392: {
        'options': [
            {'key': 'A', 'text': '物质财富的积累'},
            {'key': 'B', 'text': '价值观和意识形态'},
            {'key': 'C', 'text': '科学技术发展水平'},
            {'key': 'D', 'text': '自然地理环境'},
        ],
        'answer': 'B'
    },
    # ID=403: 选项A合并了A和B
    403: {
        'options': [
            {'key': 'A', 'text': '第一时间抢占流量'},
            {'key': 'B', 'text': '主动设置议题引导舆论'},
            {'key': 'C', 'text': '保持沉默等待官方通报'},
            {'key': 'D', 'text': '转载境外媒体报道'},
        ],
        'answer': 'B'
    },
    # ID=413: 多选题选项合并
    413: {
        'options': [
            {'key': 'A', 'text': '坚守中华文化立场'},
            {'key': 'B', 'text': '提炼展示中华文明精神标识'},
            {'key': 'C', 'text': '削弱民族文化主体性'},
            {'key': 'D', 'text': '全面否定革命文化传统'},
        ],
        'answer': 'AB'
    },
    # ID=521: 所有选项合并成一个
    521: {
        'options': [
            {'key': 'A', 'text': '国家安全制度'},
            {'key': 'B', 'text': '国家政治制度'},
            {'key': 'C', 'text': '国家生态制度'},
            {'key': 'D', 'text': '国家法律制度'},
        ],
        'answer': 'A'
    },
}


def fix_questions():
    app = create_app()
    with app.app_context():
        fixed_count = 0
        for qid, fix in FIXES.items():
            q = db.session.get(Question, qid)
            if not q:
                print(f'题目 ID={qid} 不存在，跳过')
                continue

            old_options = q.options
            old_answer = q.answer

            q.options = fix['options']
            q.answer = fix['answer']

            print(f'修复 ID={qid}:')
            print(f'  选项: {old_options} -> {fix["options"]}')
            print(f'  答案: {old_answer} -> {fix["answer"]}')
            fixed_count += 1

        db.session.commit()
        print(f'\n共修复 {fixed_count} 道题目')


if __name__ == '__main__':
    fix_questions()
