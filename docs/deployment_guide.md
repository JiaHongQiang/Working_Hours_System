# 部署指南

## Ubuntu 24.04 + MySQL 8.0 生产环境部署

### 一、系统环境准备

#### 1.1 更新系统

```bash
sudo apt update
sudo apt upgrade -y
```

#### 1.2 安装MySQL 8.0

```bash
sudo apt install mysql-server -y

# 安全配置
sudo mysql_secure_installation

# 登录MySQL
sudo mysql

# 创建数据库和用户
CREATE DATABASE hospital_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hospital_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON hospital_db.* TO 'hospital_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 1.3 安装Python环境

```bash
sudo apt install python3.10 python3.10-venv python3-pip python3-dev -y
sudo apt install default-libmysqlclient-dev build-essential -y
```

#### 1.4 安装Nginx

```bash
sudo apt install nginx -y
sudo systemctl enable nginx
```

### 二、后端部署

#### 2.1 创建部署目录

```bash
sudo mkdir -p /var/www/hospital
sudo chown $USER:$USER /var/www/hospital
cd /var/www/hospital
```

#### 2.2 克隆项目代码

```bash
git clone <your-repo-url> .
cd backend
```

#### 2.3 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.4 配置环境变量

```bash
cp .env.example .env
vim .env
```

填写以下配置：

```env
SECRET_KEY=<生成一个强密钥>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

DB_NAME=hospital_db
DB_USER=hospital_user
DB_PASSWORD=your_strong_password
DB_HOST=localhost
DB_PORT=3306

REDIS_HOST=localhost
REDIS_PORT=6379

WECHAT_APP_ID=your_wechat_appid
WECHAT_APP_SECRET=your_wechat_secret

HOSPITAL_LATITUDE=39.9042
HOSPITAL_LONGITUDE=116.4074
GEOFENCE_RADIUS=200
```

#### 2.5 初始化数据库

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

#### 2.6 配置Gunicorn服务

创建systemd服务文件：

```bash
sudo vim /etc/systemd/system/hospital.service
```

内容：

```ini
[Unit]
Description=Hospital Working Hours System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/hospital/backend
Environment="PATH=/var/www/hospital/backend/venv/bin"
ExecStart=/var/www/hospital/backend/venv/bin/gunicorn \
          --workers 4 \
          --bind unix:/run/gunicorn.sock \
          --timeout 300 \
          hospital_system.wsgi:application

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start hospital
sudo systemctl enable hospital
sudo systemctl status hospital
```

### 三、Nginx配置

创建Nginx配置文件：

```bash
sudo vim /etc/nginx/sites-available/hospital
```

内容：

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 20M;

    location /static/ {
        alias /var/www/hospital/backend/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/hospital/backend/media/;
        expires 7d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/hospital /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 四、SSL证书配置（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 五、Redis安装（用于Celery）

```bash
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

配置Celery服务：

```bash
sudo vim /etc/systemd/system/celery.service
```

内容：

```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/hospital/backend
Environment="PATH=/var/www/hospital/backend/venv/bin"
ExecStart=/var/www/hospital/backend/venv/bin/celery -A hospital_system worker -l info

[Install]
WantedBy=multi-user.target
```

启动Celery：

```bash
sudo systemctl daemon-reload
sudo systemctl start celery
sudo systemctl enable celery
```

### 六、前端部署（Web管理端）

#### 6.1 安装Node.js

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
```

#### 6.2 构建前端

```bash
cd /var/www/hospital/web-admin
npm install
npm run build
```

生成的`dist`目录部署到Nginx：

```bash
sudo mkdir -p /var/www/html/admin
sudo cp -r dist/* /var/www/html/admin/
```

更新Nginx配置，添加前端路由：

```nginx
location /admin {
    alias /var/www/html/admin;
    try_files $uri $uri/ /admin/index.html;
}
```

### 七、数据库备份

创建备份脚本：

```bash
sudo vim /usr/local/bin/backup_hospital_db.sh
```

内容：

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/hospital"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

mysqldump -u hospital_user -p'your_strong_password' hospital_db | \
    gzip > $BACKUP_DIR/hospital_db_$DATE.sql.gz

# 保留最近30天的备份
find $BACKUP_DIR -name "hospital_db_*.sql.gz" -mtime +30 -delete
```

设置定时任务：

```bash
sudo chmod +x /usr/local/bin/backup_hospital_db.sh
sudo crontab -e
```

添加：

```cron
0 3 * * * /usr/local/bin/backup_hospital_db.sh
```

### 八、防火墙配置

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 九、监控与日志

查看应用日志：

```bash
# Gunicorn日志
sudo journalctl -u hospital -f

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Celery日志
sudo journalctl -u celery -f
```

### 十、微信小程序配置

1. 在微信公众平台配置服务器域名：`https://your-domain.com`
2. 修改小程序`app.js`中的`apiBase`为生产环境地址
3. 使用微信开发者工具上传代码并提交审核

---

## 常见问题

### 1. Gunicorn启动失败

检查sock文件权限：

```bash
sudo chown www-data:www-data /run/gunicorn.sock
```

### 2. 静态文件404

重新收集静态文件：

```bash
cd /var/www/hospital/backend
source venv/bin/activate
python manage.py collectstatic --noinput
```

### 3. 数据库连接失败

检查MySQL服务状态：

```bash
sudo systemctl status mysql
```

确认数据库配置正确：

```bash
mysql -u hospital_user -p
```
