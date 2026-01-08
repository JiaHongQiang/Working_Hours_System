#!/bin/bash

# --- 医院工时系统 - 后端部署脚本 ---

# 配置
BACKEND_DIR="/home/Working_Hours_System/backend"
VENV_PATH="$BACKEND_DIR/venv"

set -e

echo "🚀 开始后端部署..."

# 1. 进入项目目录
echo "📂 进入后端目录: $BACKEND_DIR"
cd "$BACKEND_DIR"

# 2. 拉取最新代码
echo "⬇️ 拉取远程代码 (git pull)..."
git pull origin main

# 3. 激活虚拟环境
echo "🐍 激活虚拟环境..."
source "$VENV_PATH/bin/activate"

# 4. 安装/更新依赖（如果需要）
# echo "📦 安装依赖..."
# pip install -r requirements.txt

# 5. 运行数据库迁移（如果需要）
# echo "🗄️ 运行数据库迁移..."
# python manage.py migrate

# 6. 停止旧的服务进程
echo "🛑 停止旧服务进程..."
pkill -f "python manage.py runserver" || true

# 7. 启动新服务
echo "🚀 启动后端服务..."
nohup python manage.py runserver 0.0.0.0:8000 > "$BACKEND_DIR/server.log" 2>&1 &

# 等待启动
sleep 2

# 8. 检查是否启动成功
if pgrep -f "python manage.py runserver" > /dev/null; then
    echo "✅ 后端服务启动成功！"
    echo "📋 日志文件: $BACKEND_DIR/server.log"
    echo "🌐 服务地址: http://0.0.0.0:8000/"
else
    echo "❌ 后端服务启动失败，请检查日志"
    tail -20 "$BACKEND_DIR/server.log"
    exit 1
fi
