# 医院工时统计系统 - 后端服务

基于 Django 4.2 + MySQL 8.0 的企业级后端服务。

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

```bash
# 连接MySQL并创建数据库
mysql -u root -p

CREATE DATABASE hospital_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hospital_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON hospital_db.* TO 'hospital_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填写数据库密码等配置
```

### 4. 初始化数据库

```bash
# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser
```

### 5. 运行开发服务器

```bash
python manage.py runserver
```

访问 http://localhost:8000/admin 进入管理后台。

## 项目结构

```
backend/
├── hospital_system/     # Django项目配置
├── core/                # 核心应用
│   ├── models/         # 数据模型
│   ├── serializers/    # DRF序列化器
│   ├── views/          # API视图
│   ├── services/       # 业务逻辑层
│   └── utils/          # 工具函数
├── api/                # API路由
├── requirements.txt    # 依赖清单
└── manage.py
```

## 核心功能模块

- **组织架构管理**: 部门、员工管理
- **排班管理**: 自定义班次、灵活排班
- **考勤管理**: 打卡记录、地理围栏
- **加班核算**: 0-4-8阶梯制、动态倍率
- **审批流**: 多级审批
- **报表统计**: 工时统计、薪资报表

## API文档

启动服务后访问: http://localhost:8000/api/docs
