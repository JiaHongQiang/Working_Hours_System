# 医院工时统计与排班管理系统

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.0-brightgreen.svg)](https://vuejs.org/)

> 基于 Ubuntu 24.04 + MySQL 8.0 + Django + Vue3 + 微信小程序的企业级医院人力资源管理系统

## 系统概述

本系统为医院提供全方位的工时统计与排班管理解决方案，包含以下核心特性：

- ✅ **灵活排班**：支持自定义班次、跨夜班处理、批量排班
- ✅ **智能考勤**：地理围栏验证、微信小程序打卡
- ✅ **精准核算**：0-4-8阶梯制工时规整、动态薪资倍率（1.5x/2.0x/3.0x）
- ✅ **审批流程**：多级审批、时长调整、驳回重申
- ✅ **数据分析**：多维度统计、Excel导出、薪资报表

## 技术架构

### 后端
- **框架**：Django 4.2 + Django REST Framework
- **数据库**：MySQL 8.0 (utf8mb4)
- **认证**：JWT Token
- **任务队列**：Celery + Redis

### Web管理端
- **框架**：Vue 3 + Vite
- **UI组件**：Element Plus
- **状态管理**：Pinia
- **图表**：ECharts

### 微信小程序
- **UI组件**：Vant Weapp
- **功能**：排班查询、打卡、加班申报

## 快速开始

### 1. 克隆项目

```bash
git clone <repository_url>
cd Working_Hours_System
```

### 2. 后端部署

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写数据库配置

# 初始化数据库
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 运行开发服务器
python manage.py runserver
```

### 3. Web管理端部署

```bash
cd web-admin

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

### 4. 微信小程序

使用微信开发者工具打开 `wechat-miniapp` 目录

## 核心业务逻辑

### 跨夜班处理

系统自动识别跨夜班次（如大夜班 20:00-次日08:00），精确计算工作时长。

### 0-4-8阶梯制工时规整

- 加班 < 4小时：计为 0小时
- 加班 4-8小时：计为 4小时
- 加班 ≥ 8小时：计为 8小时

### 动态薪资倍率

| 场景 | 倍率 |
|------|------|
| 法定节假日 | 3.0x |
| 休息日（无排班） | 2.0x |
| 正常排班日超时 | 1.5x |

## API文档

后端服务启动后访问：
- Admin后台：http://localhost:8000/admin
- API文档：http://localhost:8000/api/

主要API端点：
- `/api/departments/` - 部门管理
- `/api/users/` - 员工管理
- `/api/shifts/` - 班次定义
- `/api/rosters/` - 排班管理
- `/api/attendance/` - 考勤打卡
- `/api/overtime/` - 加班申报与审批

## 项目结构

```
Working_Hours_System/
├── backend/                 # Django后端
│   ├── hospital_system/     # 项目配置
│   ├── core/                # 核心应用
│   │   ├── models/          # 数据模型
│   │   ├── serializers/     # 序列化器
│   │   ├── views/           # API视图
│   │   └── services/        # 业务逻辑层
│   └── requirements.txt     # Python依赖
├── web-admin/               # Vue管理端
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   ├── api/             # API封装
│   │   └── stores/          # 状态管理
│   └── package.json
├── wechat-miniapp/          # 微信小程序
│   ├── pages/               # 页面
│   └── components/          # 组件
└── docs/                    # 文档
```

## 开发团队

本项目由 AI Assistant 协助构建。

## 许可证

MIT License
