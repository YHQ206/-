import sys, json
sys.path.insert(0, '.')
from app import create_app
from models import db, Question, Progress

app = create_app()
with app.app_context():
    # 删除第6章所有题目
    qs = Question.query.filter_by(chapter_id=605).all()
    qids = [q.id for q in qs]
    Progress.query.filter(Progress.question_id.in_(qids)).delete()
    for q in qs:
        db.session.delete(q)
    db.session.flush()
    print(f'已删除 {len(qs)} 道旧题')

    # === 一、单选题 (8题) ===
    single_questions = [
        {
            "content": '新发展阶段的"新"主要体现在',
            "options": [
                {"key": "A", "text": "经济发展速度加快"},
                {"key": "B", "text": "经济总量大幅增加"},
                {"key": "C", "text": "社会主要矛盾发生变化"},
                {"key": "D", "text": "国际地位显著提升"}
            ],
            "answer": "C"
        },
        {
            "content": "新发展阶段的社会主要矛盾为",
            "options": [
                {"key": "A", "text": "经济发展速度与环境保护之间的矛盾"},
                {"key": "B", "text": "人民日益增长的美好生活需要和不平衡不充分的发展之间的矛盾"},
                {"key": "C", "text": "城乡发展差距"},
                {"key": "D", "text": "国际竞争压力"}
            ],
            "answer": "B"
        },
        {
            "content": "高质量发展的重要意义在于",
            "options": [
                {"key": "A", "text": "提高经济增长速度"},
                {"key": "B", "text": "增强经济竞争力"},
                {"key": "C", "text": "扩大对外贸易规模"},
                {"key": "D", "text": "增加财政收入"}
            ],
            "answer": "B"
        },
        {
            "content": "高质量发展的重要标志是",
            "options": [
                {"key": "A", "text": "GDP总量"},
                {"key": "B", "text": "创新能力"},
                {"key": "C", "text": "出口总额"},
                {"key": "D", "text": "固定资产投资"}
            ],
            "answer": "B"
        },
        {
            "content": '新发展阶段的"新"还体现在',
            "options": [
                {"key": "A", "text": "人口红利"},
                {"key": "B", "text": "科技驱动"},
                {"key": "C", "text": "土地资源"},
                {"key": "D", "text": "资本积累"}
            ],
            "answer": "B"
        },
        {
            "content": "新时代对社会主义基本经济制度的新概括为",
            "options": [
                {"key": "A", "text": "公有制为主体、多种所有制经济共同发展"},
                {"key": "B", "text": "按劳分配为主体、多种分配方式并存"},
                {"key": "C", "text": "社会主义市场经济体制"},
                {"key": "D", "text": "以上都是"}
            ],
            "answer": "D"
        },
        {
            "content": '什么是"两个毫不动摇"？',
            "options": [
                {"key": "A", "text": "毫不动摇地巩固和发展公有制经济"},
                {"key": "B", "text": "毫不动摇地鼓励、支持、引导非公有制经济发展"},
                {"key": "C", "text": "以上都是"},
                {"key": "D", "text": "以上都不是"}
            ],
            "answer": "C"
        },
        {
            "content": "新时代中国构建现代化产业体系的具体举措包括",
            "options": [
                {"key": "A", "text": "推进制造业高质量发展"},
                {"key": "B", "text": "加强农业基础设施建设"},
                {"key": "C", "text": "深化服务业对外开放"},
                {"key": "D", "text": "加快科技创新体系建设"}
            ],
            "answer": "A"
        }
    ]

    for i, sq in enumerate(single_questions):
        q = Question(chapter_id=605, type="single", sort_order=i+1,
                     content=sq["content"], options=json.dumps(sq["options"], ensure_ascii=False), answer=sq["answer"])
        db.session.add(q)
        db.session.flush()
        db.session.add(Progress(question_id=q.id, status="unanswered"))
    print("✅ 单选题 8题 已插入")

    # === 二、多选题 (8题) ===
    multi_questions = [
        {
            "content": "新发展阶段的主要特征包括",
            "options": [
                {"key": "A", "text": "高质量发展"},
                {"key": "B", "text": "创新驱动发展"},
                {"key": "C", "text": "全面深化改革"},
                {"key": "D", "text": "扩大对外开放"},
                {"key": "E", "text": "实现共同富裕"}
            ],
            "answer": "ABCD"
        },
        {
            "content": "新发展阶段的政策导向包括",
            "options": [
                {"key": "A", "text": "创新驱动发展战略"},
                {"key": "B", "text": "区域协调发展"},
                {"key": "C", "text": "绿色发展"},
                {"key": "D", "text": "人口老龄化应对策略"},
                {"key": "E", "text": "乡村振兴战略"}
            ],
            "answer": "ABCE"
        },
        {
            "content": "新发展理念中的协调发展包括",
            "options": [
                {"key": "A", "text": "城乡协调发展"},
                {"key": "B", "text": "区域协调发展"},
                {"key": "C", "text": "产业协调发展"},
                {"key": "D", "text": "国际协调发展"},
                {"key": "E", "text": "社会协调发展"}
            ],
            "answer": "ABCE"
        },
        {
            "content": "新发展理念包括",
            "options": [
                {"key": "A", "text": "创新"},
                {"key": "B", "text": "协调"},
                {"key": "C", "text": "绿色"},
                {"key": "D", "text": "开放"},
                {"key": "E", "text": "共享"}
            ],
            "answer": "ABCDE"
        },
        {
            "content": "社会主义市场经济的特点有",
            "options": [
                {"key": "A", "text": "市场在资源配置中起决定性作用"},
                {"key": "B", "text": "政府发挥宏观调控作用"},
                {"key": "C", "text": "以公有制为主体"},
                {"key": "D", "text": "鼓励非公有制经济发展"},
                {"key": "E", "text": "实行计划经济"}
            ],
            "answer": "ABCD"
        },
        {
            "content": '如何坚持"两个毫不动摇"？',
            "options": [
                {"key": "A", "text": "深化国有企业改革"},
                {"key": "B", "text": "优化营商环境"},
                {"key": "C", "text": "限制非公有制经济发展"},
                {"key": "D", "text": "加强产权保护"},
                {"key": "E", "text": "推动科技创新"}
            ],
            "answer": "ABDE"
        },
        {
            "content": "构建新发展格局的意义包括",
            "options": [
                {"key": "A", "text": "提升国家经济竞争力"},
                {"key": "B", "text": "促进区域协调发展"},
                {"key": "C", "text": "加强国际合作"},
                {"key": "D", "text": "减少对外依赖"},
                {"key": "E", "text": "提高人民生活水平"}
            ],
            "answer": "ABCE"
        },
        {
            "content": "国内国际双循环的主要特征包括",
            "options": [
                {"key": "A", "text": "国内大循环为主体"},
                {"key": "B", "text": "国际市场为主导"},
                {"key": "C", "text": "内外市场相互促进"},
                {"key": "D", "text": "减少对外依赖"},
                {"key": "E", "text": "增强国内产业链稳定性"}
            ],
            "answer": "ACE"
        }
    ]

    for i, mq in enumerate(multi_questions):
        q = Question(chapter_id=605, type="multiple", sort_order=9+i,
                     content=mq["content"], options=json.dumps(mq["options"], ensure_ascii=False), answer=mq["answer"])
        db.session.add(q)
        db.session.flush()
        db.session.add(Progress(question_id=q.id, status="unanswered"))
    print("✅ 多选题 8题 已插入")

    # === 三、填空题 (6题) ===
    blank_questions = [
        {"content": "新发展阶段要实现高质量和可持续发展。", "answer": ""},
        {"content": "社会主义市场经济体制是____。", "answer": "使市场在资源配置中起决定性作用和更好发挥政府作用的经济体制"},
        {"content": "国内国际双循环是____，国内国际双循环相互促进的新发展格局。", "answer": "以国内大循环为主体"},
        {"content": "新发展格局强调以____为主体，国内国际双循环相互促进的新发展格局。", "answer": "国内大循环"},
        {"content": "新时代我国全面实施乡村振兴战略，需要在农业供给侧结构性改革、农村基础设施建设、农民就业创业和提高农村教育水平等方面下功夫。", "answer": ""},
        {"content": "新时代我国全面实施乡村振兴战略，要以____为基础，以人才振兴为核心，以文化振兴为支撑，以生态振兴为保障。", "answer": "产业振兴"}
    ]

    for i, bq in enumerate(blank_questions):
        q = Question(chapter_id=605, type="blank", sort_order=17+i,
                     content=bq["content"], options=None, answer=bq["answer"])
        db.session.add(q)
        db.session.flush()
        db.session.add(Progress(question_id=q.id, status="unanswered"))
    print("✅ 填空题 6题 已插入")

    # === 四、判断题 (9题) ===
    judge_questions = [
        ("新发展阶段强调的是经济高速增长。", "×"),
        ("高质量发展意味着放弃经济增长速度，只追求质量。", "×"),
        ('新发展理念中的"共享"是指让全体人民共享发展成果。', "√"),
        ('坚持"两个毫不动摇"的目的是为了巩固和发展公有制经济，激发非公有制经济活力和创造力。', "√"),
        ("基本分配制度是以按劳分配为主体，多种分配方式并存。", "√"),
        ("国内大循环是指国内生产、分配、流通、消费等环节形成闭环。", "√"),
        ("构建新发展格局是为了应对全球经济环境变化，增强国内市场的自主性和韧性。", "√"),
        ("区域协调发展是指通过政策引导和资源配置，实现不同地区之间的均衡发展。", "√"),
        ("乡村振兴战略的目标是实现农业现代化和农村城镇化。", "×")
    ]

    for i, (content, answer) in enumerate(judge_questions):
        q = Question(chapter_id=605, type="judge", sort_order=23+i,
                     content=content, options=None, answer=answer)
        db.session.add(q)
        db.session.flush()
        db.session.add(Progress(question_id=q.id, status="unanswered"))
    print("✅ 判断题 9题 已插入")

    db.session.commit()

    # === 验证 ===
    total = Question.query.filter_by(chapter_id=605).count()
    print(f"\n🎉 第6章重建完成！共 {total} 题")
    print("   单选题: 8题")
    print("   多选题: 8题")
    print("   填空题: 6题")
    print("   判断题: 9题")

    qs = Question.query.filter_by(chapter_id=605).order_by(Question.sort_order).all()
    for q in qs:
        opts = json.loads(q.options) if isinstance(q.options, str) else (q.options or [])
        oc = len(opts) if opts else 0
        print(f"  {q.sort_order:2d}. [{q.type:6s}] {q.answer:10s} opts={oc:2d}  {q.content[:50]}")
