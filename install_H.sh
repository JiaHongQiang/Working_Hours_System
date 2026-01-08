#!/bin/bash
# 后端更新脚本
# 使用方法: sudo ./update_backend.sh

set -e

PROJECT_DIR="/home/Working_Hours_System"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"
SERVICE_NAME="hospital"

echo "=========================================="
echo "       后端更新脚本 - Working Hours System"
echo "=========================================="

# 进入项目目录
cd $PROJECT_DIR

# 拉取最新代码
echo "[1/4] 拉取最新代码..."
git pull origin main

# 激活虚拟环境并安装依赖（如有更新）
echo "[2/4] 检查依赖更新..."
source $VENV_DIR/bin/activate
pip install -r $BACKEND_DIR/requirements.txt -q

# 执行数据库迁移（如有）
echo "[3/4] 执行数据库迁移..."
cd $BACKEND_DIR
python manage.py migrate --noinput

# 重启服务
echo "[4/4] 重启后端服务..."
systemctl daemon-reload
systemctl restart $SERVICE_NAME

echo ""
echo "✅ 后端更新完成！"
echo "服务状态："
systemctl status $SERVICE_NAME --no-pager | head -10

