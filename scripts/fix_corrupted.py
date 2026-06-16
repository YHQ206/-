"""修复内容损坏的题目"""
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from models import db, Question


# 定义需要修复的题目
# 格式: {question_id: new_content}
FIXES = {
    111: '必须大力弘扬________，奋力以中国式现代化全面推进中华民族伟大复兴。',
    137: '在新时代党的建设伟大工程中，摆在首位的是',
    210: '全面深化改革的过程中，摸着石头过河的方法是不可取的。（×）',
    233: '新发展理念中的"共享"是指让全体人民共享发展成果。（√）',
    284: '新时代全方位民主是指在习近平新时代中国特色社会主义思想的指导下，实现________的民主化。',
    314: '统一战线的本质是',
    350: '中华民族共同体意识是中华民族凝聚力的重要体现，也是实现中华民族伟大复兴的基础。（√）',
    441: '坚持党管媒体原则，要求所有传播平台都要纳入党的领导和管理范围。（√）',
    502: '"生态兴则文明兴"仅指物质文明发展，与精神文明无关。（×）',
    545: '澳门"一中心一平台一基地"定位中的"一基地"指？',
    557: '支持香港融入国家发展大局的具体举措包括',
}


def fix_corrupted():
    app = create_app()
    with app.app_context():
        fixed_count = 0
        for qid, new_content in FIXES.items():
            q = db.session.get(Question, qid)
            if not q:
                print(f'题目 ID={qid} 不存在，跳过')
                continue

            old_content = q.content
            q.content = new_content

            print(f'修复 ID={qid}:')
            print(f'  旧内容: {old_content[:60]}...')
            print(f'  新内容: {new_content[:60]}...')
            fixed_count += 1

        db.session.commit()
        print(f'\n共修复 {fixed_count} 道题目')


if __name__ == '__main__':
    fix_corrupted()
