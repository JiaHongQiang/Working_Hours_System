#!/bin/bash

# --- 配置 ---
# 设置项目路径
PROJECT_DIR="/home/Working_Hours_System/web-admin"
# 设置部署目标路径
TARGET_DIR="/var/www/html/admin/"

# --- 脚本开始 ---

# set -e 表示如果任何一行命令报错，脚本立即停止执行
# 这样可以防止 git pull 失败或 build 失败后继续执行 cp 命令
set -e

echo "🚀 开始自动化部署..."

# 1. 进入项目目录
echo "📂 进入项目目录: $PROJECT_DIR"
cd "$PROJECT_DIR"

# 2. 拉取最新代码
echo "⬇️ 拉取远程代码 (git pull)..."
git pull origin main

# 建议：如果 package.json 有变动，通常需要执行 npm install
# 如果你需要，请取消下面这行的注释
# echo "📦 安装依赖..."
# npm install

# 3. 打包构建
echo "🔨 开始构建项目 (npm run build)..."
npm run build

# 检查 dist 目录是否存在
if [ ! -d "dist" ]; then
    echo "❌ 错误: dist 目录未生成，构建可能失败。"
    exit 1
fi

# 4. 复制文件到服务器目录
echo "📤 正在部署文件到: $TARGET_DIR"
# 使用 sudo 权限复制
sudo cp -r dist/* "$TARGET_DIR"

echo "✅ 部署成功！"
