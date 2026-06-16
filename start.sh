#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "   📚 刷题助手 - 思政课客观题复习系统"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python 3.10+"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js，请先安装 Node.js 18+"
    exit 1
fi

# 检查后端依赖
echo "[1/4] 检查后端依赖..."
if [ ! -d "backend/venv" ]; then
    echo "      正在创建虚拟环境..."
    cd backend
    python3 -m venv venv
    cd ..
fi

echo "      正在安装 Python 依赖..."
cd backend
source venv/bin/activate
pip install -r requirements.txt -q
cd ..

# 检查前端依赖
echo "[2/4] 检查前端依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo "      正在安装 npm 依赖..."
    cd frontend
    npm install
    cd ..
fi

# 启动后端
echo "[3/4] 启动后端服务..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..
sleep 2

# 启动前端
echo "[4/4] 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
sleep 2

echo ""
echo "========================================"
echo "   ✅ 启动完成！"
echo "========================================"
echo ""
echo "   🌐 请在浏览器中访问: http://localhost:5173"
echo ""
echo "   💡 提示:"
echo "   - 按 Ctrl+C 停止服务"
echo "   - 后端运行在: http://localhost:5000"
echo ""
echo "========================================"
echo ""

# 捕获 Ctrl+C 信号
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# 等待用户按 Ctrl+C
wait
