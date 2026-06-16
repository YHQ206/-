# 📚 刷题助手 - 思政课客观题复习系统

一个帮助大学生复习思政课客观题的网页刷题系统，支持题库导入、章节刷题、错题本、收藏夹、进度统计等功能。

![Vue 3](https://img.shields.io/badge/Vue-3-4FC08D?style=flat&logo=vuedotjs)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-blue)

<p align="center">
  <img src="https://img.shields.io/badge/功能-四大主题-orange" />
  <img src="https://img.shields.io/badge/功能-错题本-green" />
  <img src="https://img.shields.io/badge/功能-收藏夹-yellow" />
  <img src="https://img.shields.io/badge/功能-进度统计-purple" />
</p>

## ✨ 功能特色

### 📝 刷题功能
- **章节刷题**：按章节顺序做题，支持单选、多选、填空、判断四种题型
- **随机刷题**：从全部题目中随机抽取，可设置数量和范围
- **进度保存**：自动记住上次做到哪里，下次继续

### 📖 错题本
- **智能分类**：自动分为「待复习」和「已掌握」
- **顽固错题**：错误次数 ≥ 3 次的题目重点标记
- **复习模式**：可以专门刷错题，答对后自动移入已掌握

### ⭐ 收藏夹
- 手动收藏重点题目
- 按科目分类查看

### 📊 进度统计
- 总题数、已完成、正确率
- 今日做题数
- 各章节完成进度

### 🎨 多主题切换
| 主题 | 风格 |
|------|------|
| 🌸 清新可爱 | 粉色渐变、圆润卡片、浮动装饰 |
| 🌙 暗黑酷炫 | 深蓝背景、霓虹渐变、科技感 |
| ✨ 玻璃拟态 | 彩色背景、毛玻璃卡片、质感 |
| 🎨 简约精致 | 浅灰背景、精致阴影、干净 |

### 💬 小彩蛋
- **鼓励语系统**：答对/答错时显示随机鼓励语
- **连对特效**：连续答对 3/5/10 题时放烟花庆祝！

## 🚀 快速开始

### 环境要求

- **Python** 3.10+
- **Node.js** 18+
- **无需安装数据库**（使用 SQLite）

### 1. 下载项目

```bash
git clone https://github.com/你的用户名/shuti-quiz.git
cd shuti-quiz
```

### 2. 安装后端依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd ../frontend
npm install
```

### 4. 启动项目

#### 方式一：一键启动（推荐）

```bash
# Windows 用户
double-click start.bat

# Mac/Linux 用户
chmod +x start.sh
./start.sh
```

#### 方式二：手动启动

**终端 1 - 启动后端：**
```bash
cd backend
python app.py
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm run dev
```

### 5. 访问系统

打开浏览器访问 http://localhost:5173

## 📥 导入题库

系统支持两种题库格式：

### 格式一：TXT 文件

```
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

### 格式二：Word 文档 (.docx)

- 支持红色字体标记正确选项
- 支持下划线标记填空答案
- 支持表格中的判断题

### 导入方式

1. 将题库文件放入 `data/` 目录
2. 在首页点击「导入题库」按钮
3. 选择「增量更新」或「全部重导」

## 📁 项目结构

```
shuti-quiz/
├── backend/                # Flask 后端
│   ├── app.py              # 主程序
│   ├── config.py           # 配置文件
│   ├── models.py           # 数据库模型
│   ├── docx_parser.py      # Word 解析器
│   ├── routes/             # API 路由
│   │   ├── questions.py    # 题目相关 API
│   │   ├── records.py      # 错题本 API
│   │   ├── stats.py        # 统计 API
│   │   └── import_routes.py # 导入 API
│   └── requirements.txt    # Python 依赖
│
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   │   ├── Home.vue    # 首页
│   │   │   ├── Quiz.vue    # 做题页
│   │   │   ├── Chapter.vue # 章节页
│   │   │   ├── WrongBook.vue # 错题本
│   │   │   ├── Favorites.vue # 收藏夹
│   │   │   └── RandomQuiz.vue # 随机刷题
│   │   ├── components/     # 公共组件
│   │   │   ├── ThemeSwitcher.vue # 主题切换
│   │   │   ├── CelebrationEffect.vue # 庆祝特效
│   │   │   └── EncourageMessage.vue # 鼓励语
│   │   ├── api/            # API 封装
│   │   └── utils/          # 工具函数
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── data/                   # 题库存放目录
│   ├── 习概/               # 习近平新时代中国特色社会主义思想概论
│   └── 马原/               # 马克思主义基本原理
│
├── start.bat               # Windows 启动脚本
├── start.sh                # Mac/Linux 启动脚本
└── README.md               # 本文件
```

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 3 | 渐进式 JavaScript 框架 |
| UI 组件库 | Element Plus | Vue 3 组件库 |
| 构建工具 | Vite | 下一代前端构建工具 |
| 后端框架 | Flask | Python 轻量级 Web 框架 |
| 数据库 | SQLite | 轻量级数据库，无需安装 |
| ORM | SQLAlchemy | Python SQL 工具包 |
| Word 解析 | python-docx | Word 文档解析库 |

## ⚙️ 配置说明

### 数据库配置

默认使用 SQLite，**无需任何配置**，开箱即用。

如需使用 MySQL，修改 `backend/config.py`：

```python
# 默认 SQLite
DATABASE_URL = 'sqlite:///shuti.db'

# 使用 MySQL（需要安装 MySQL）
# DATABASE_URL = 'mysql+pymysql://root:password@localhost:3306/shuti'
```

### 前端配置

修改 `frontend/vite.config.js`：

```javascript
export default {
  server: {
    port: 5173,  // 前端端口
    proxy: {
      '/api': {
        target: 'http://localhost:5000',  // 后端地址
        changeOrigin: true
      }
    }
  }
}
```

## 📝 使用建议

### 首次使用
1. 先导入题库
2. 从第一章开始刷题
3. 用「继续上次」功能保持进度

### 日常复习
1. 使用「错题本」复习做错的题
2. 重点刷「待复习」和「顽固错题」
3. 答对的题会自动移到「已掌握」

### 考前冲刺
1. 用「随机刷题」全面检测
2. 查看统计页面找薄弱章节
3. 重点复习正确率低的章节

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 如何贡献

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📄 开源协议

本项目基于 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件

## 💖 致谢

- [Vue 3](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

---

**祝大家考试顺利！加油！** 🎓✨

<p align="center">
  如果觉得有用，请给个 ⭐ Star 支持一下！
</p>
