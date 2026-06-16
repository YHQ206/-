# 📦 如何发布到 GitHub

这是一个发布指南，帮助你把项目发布到 GitHub 让别人使用。

## 🎯 发布前的准备

### 1. 创建 GitHub 仓库

1. 登录 GitHub
2. 点击右上角的 "+" → "New repository"
3. 仓库名建议：`shuti-quiz` 或 `思政课刷题系统`
4. 选择 "Public"（公开）
5. 不要勾选 "Initialize this repository with a README"
6. 点击 "Create repository"

### 2. 准备发布版本

**步骤一：备份原配置**
```bash
cd backend
copy config.py config_local.py  # Windows
# cp config.py config_local.py  # Mac/Linux
```

**步骤二：使用发布配置**
```bash
copy config_release.py config.py  # Windows
# cp config_release.py config.py  # Mac/Linux
```

**步骤三：初始化 Git 并推送**
```bash
# 在项目根目录
git init
git add .
git commit -m "🎉 Initial commit: 刷题助手 v1.0"
git branch -M main
git remote add origin https://github.com/你的用户名/shuti-quiz.git
git push -u origin main
```

## 📋 发布检查清单

发布前确认以下文件都已准备好：

- [x] `README.md` - 项目说明文档
- [x] `LICENSE` - 开源协议
- [x] `.gitignore` - 忽略不需要上传的文件
- [x] `start.bat` - Windows 启动脚本
- [x] `start.sh` - Mac/Linux 启动脚本
- [x] `backend/config_release.py` - SQLite 配置文件
- [x] `backend/requirements.txt` - Python 依赖
- [x] `frontend/package.json` - 前端依赖

## 🔄 发布后更新

如果以后想更新代码：

```bash
git add .
git commit -m "✨ 添加新功能: xxx"
git push
```

## 💡 提示

1. **题库文件不要上传**
   - `.gitignore` 已经配置好忽略 `data/` 目录下的题目文件
   - 题库文件太大，而且每个人的题库可能不同

2. **数据库文件不要上传**
   - SQLite 数据库文件 (`*.db`) 也会被忽略
   - 每个人的做题记录是私有的

3. **本地开发配置**
   - 你本地的 `config_local.py` 会继续使用 MySQL
   - 不会影响你本地的开发

4. **发布版本配置**
   - 发布到 GitHub 的版本默认使用 SQLite
   - 用户下载后无需安装数据库即可使用

## 🎨 让 README 更好看

### 添加截图

在 README.md 中添加项目截图：

```markdown
## 📸 截图

### 首页
![首页截图](screenshots/home.png)

### 做题页
![做题页截图](screenshots/quiz.png)
```

### 添加徽章

README.md 已经包含了常用的徽章，你也可以自定义：

```markdown
![Stars](https://img.shields.io/github/stars/你的用户名/shuti-quiz)
![Forks](https://img.shields.io/github/forks/你的用户名/shuti-quiz)
![Issues](https://img.shields.io/github/issues/你的用户名/shuti-quiz)
```

## 🚀 可选：添加 GitHub Pages

如果你想让用户直接在线体验，可以：

1. 构建前端
```bash
cd frontend
npm run build
```

2. 将 `frontend/dist/` 目录推送到 GitHub 的 `gh-pages` 分支

3. 在 GitHub 仓库设置中开启 GitHub Pages

## 📝 示例仓库描述

在 GitHub 仓库页面添加描述：

```
📚 思政课刷题助手 - 支持习概/马原，四大主题，错题本，收藏夹，进度统计
```

添加 Topics 标签：
```
vue flask sqlite quiz study-tool education
```

---

**发布完成后，把仓库链接分享给同学吧！** 🎉
