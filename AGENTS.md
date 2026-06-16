# 思政课刷题系统 - AGENTS.md

## 项目概述

一个用于思政课客观题复习的网页刷题系统，支持题库导入、章节刷题、错题本、收藏夹、进度统计等功能。

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端 | Vue 3 + Element Plus | Vue 3.4+, Element Plus 2.5+ |
| 后端 | Python + Flask | Python 3.10+, Flask 3.0+ |
| 数据库 | MySQL | 8.0+ |
| ORM | SQLAlchemy | 2.0+ |
| PDF解析 | PyPDF2 | 3.0+ |
| HTTP客户端 | Axios | 1.6+ |

## 项目结构

```
shuti/刷题/
├── AGENTS.md              # 本文件
├── README.md              # 项目说明
│
├── backend/               # Flask 后端
│   ├── app.py             # 主程序入口
│   ├── config.py          # 配置文件
│   ├── models.py          # 数据库模型
│   ├── parser.py          # 题库解析器
│   ├── routes/
│   │   ├── questions.py   # 题目相关API
│   │   ├── records.py     # 做题记录API
│   │   └── stats.py       # 统计数据API
│   └── requirements.txt
│
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── views/
│   │   │   ├── Home.vue       # 首页（进度概览）
│   │   │   ├── Chapter.vue    # 章节列表
│   │   │   ├── Quiz.vue       # 做题页面
│   │   │   ├── WrongBook.vue  # 错题本
│   │   │   └── Favorites.vue  # 收藏夹
│   │   ├── components/
│   │   │   ├── QuestionCard.vue   # 题目卡片
│   │   │   ├── ProgressBar.vue    # 进度条
│   │   │   └── StatsCard.vue      # 统计卡片
│   │   └── api/
│   │       └── index.js     # API调用封装
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── data/                  # 题库存放目录
│   ├── 习概/
│   │   ├── 00_导论_xxx.txt
│   │   ├── 01_第1章_xxx.txt
│   │   └── ...（共16个章节文件）
│   └── 马原/
│       └── 马原期末复习客观题题库三.pdf
│
└── scripts/               # 工具脚本
    └── import_questions.py  # 题库导入脚本
```

## 科目说明

| 科目 | 题库来源 | 格式 |
|------|----------|------|
| 习概（习近平新时代中国特色社会主义思想概论） | `data/习概/` 目录下的 TXT 文件 | TXT |
| 马原（马克思主义基本原理） | `data/马原/` 目录下的 PDF 文件 | PDF |

## 数据库设计

### 表结构

```sql
-- 科目表
CREATE TABLE subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '科目名称（习概/马原）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 章节表
CREATE TABLE chapters (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject_id INT NOT NULL,
    name VARCHAR(100) NOT NULL COMMENT '章节名称',
    sort_order INT DEFAULT 0 COMMENT '排序顺序',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- 题目表
CREATE TABLE questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    chapter_id INT NOT NULL,
    type ENUM('single', 'multiple', 'blank', 'judge') NOT NULL COMMENT '题型',
    content TEXT NOT NULL COMMENT '题目内容',
    options JSON COMMENT '选项列表（选择题用）',
    answer VARCHAR(500) NOT NULL COMMENT '正确答案',
    explanation TEXT COMMENT '解析',
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id)
);

-- 做题记录表
CREATE TABLE records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question_id INT NOT NULL,
    user_answer VARCHAR(500) COMMENT '用户答案',
    is_correct BOOLEAN NOT NULL COMMENT '是否正确',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

-- 收藏表
CREATE TABLE favorites (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id),
    UNIQUE KEY unique_question (question_id)
);

-- 刷题进度表（记录每道题的完成状态）
CREATE TABLE progress (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question_id INT NOT NULL,
    status ENUM('unanswered', 'correct', 'wrong') DEFAULT 'unanswered',
    last_attempt_at DATETIME,
    attempt_count INT DEFAULT 0,
    FOREIGN KEY (question_id) REFERENCES questions(id),
    UNIQUE KEY unique_question (question_id)
);
```

## 题库格式规范

### TXT格式（习概）

```text
一、单项选择题
1. 题目内容__________。
（A）选项A （B）选项B （C）选项C （D）选项D
答案：C

二、多项选择题
64. 题目内容。
（A）选项A （B）选项B （C）选项C （D）选项D （E）选项E
答案：CD

三、填空题
66. 题目内容__________。
（答案：关键词）

四、判断题
68. 题目内容。（×）
69. 题目内容。（√）
```

### PDF格式（马原）

```text
一.单项选择题
1、题目内容（）
A.选项A
B.选项B
C.选项C
D.选项D
答案：D
```

## 核心功能

### 1. 题库导入
- 支持导入 TXT 和 PDF 格式
- 自动识别题型（单选/多选/填空/判断）
- 自动提取题目、选项、答案
- 按章节文件自动创建章节
- 区分科目（习概/马原）

### 2. 章节刷题
- 按章节顺序做题
- 显示当前进度（第X/Y题）
- 提交后显示答案和解析
- 记录做题结果

### 3. 随机刷题
- 从全部题目中随机抽取
- 可设置抽取数量
- 支持只抽未做过的题

### 4. 错题本
- 自动收集答错的题目
- 支持重做错题
- 显示错误次数和上次错误时间
- 答对后可移出错题本

### 5. 收藏夹
- 手动收藏重点题目
- 支持取消收藏
- 可从收藏夹直接刷题

### 6. 进度统计
- 总题数、已做题数、正确率
- 各章节完成进度
- 今日做题数
- 做题趋势图表

### 7. 题目状态标记
- ○ 未做
- ✓ 正确
- ✗ 错误
- ★ 收藏

### 8. 进度保存与恢复
- 自动保存刷题位置（章节+题号）
- 下次进入自动跳转到上次位置
- 支持手动清空所有做题记录

## API设计

### 题目相关

```
GET  /api/subjects              # 获取科目列表
GET  /api/subjects/:id/chapters # 获取科目下的章节列表
GET  /api/chapters/:id/questions # 获取章节题目
GET  /api/questions/random      # 随机获取题目（可指定科目）
GET  /api/questions/:id         # 获取单个题目详情
POST /api/questions/:id/answer  # 提交答案
```

### 记录相关

```
GET  /api/records/wrong         # 获取错题列表
GET  /api/favorites             # 获取收藏列表
POST /api/favorites/:id         # 添加收藏
DELETE /api/favorites/:id       # 取消收藏
DELETE /api/records             # 清空所有记录
```

### 统计相关

```
GET /api/stats/overview         # 总体统计
GET /api/stats/chapters         # 各章节统计
GET /api/stats/today            # 今日统计
```

### 进度相关

```
GET  /api/progress/last         # 获取上次刷题位置（含科目、章节、题号）
POST /api/progress/save         # 保存当前刷题位置
DELETE /api/progress            # 清空所有进度和记录
```

## 开发规范

### 代码风格

- Python: PEP8，使用 type hints
- JavaScript/Vue: ESLint + Prettier
- 变量命名：snake_case (Python), camelCase (JS)

### Git提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

### 错误处理

- API返回统一格式：`{ code: 0, data: ..., message: "success" }`
- 错误返回：`{ code: 非0, data: null, message: "错误信息" }`

## 环境配置

### 后端环境变量 (.env)

```env
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/shuti
SECRET_KEY=your-secret-key
```

### 前端配置 (vite.config.js)

```javascript
export default {
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
}
```

## 启动命令

### 后端

```bash
cd backend
pip install -r requirements.txt
flask db upgrade  # 初始化数据库
python app.py
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

### 导入题库

```bash
cd scripts
python import_questions.py --dir ../data/习概 --subject 习概
python import_questions.py --file ../data/马原/马原期末复习客观题题库三.pdf --subject 马原
```

## 题型说明

| 科目 | 题型 |
|------|------|
| 习概 | 单选、多选、填空、判断 |
| 马原 | 单选、判断（无多选） |

## 评分规则

- **无计分系统**，纯粹刷题用
- **多选题**：必须全对才算对，部分选对算错

## 填空题处理

- 导入时自动扫描没有答案的填空题
- 生成列表供用户手动补充答案
- 没有答案的填空题暂不进入刷题列表

## 开发计划

| 阶段 | 内容 | 状态 |
|------|------|------|
| 1 | 数据库搭建 + 后端基础API | 待开发 |
| 2 | 题库解析器（TXT + PDF） | 待开发 |
| 3 | 前端基础页面框架 | 待开发 |
| 4 | 做题功能 + 答案判断 | 待开发 |
| 5 | 错题本 + 收藏夹 | 待开发 |
| 6 | 进度统计 + 进度保存 | 待开发 |
| 7 | 测试 + 调试 | 待开发 |
