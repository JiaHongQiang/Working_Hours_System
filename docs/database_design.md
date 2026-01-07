# 数据库设计文档

## 概述

医院工时统计系统采用MySQL 8.0数据库，字符集统一为`utf8mb4_unicode_ci`，支持中文和特殊字符。

## 核心数据表

### 1. departments (部门表)

```sql
CREATE TABLE `departments` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL COMMENT '部门名称',
  `parent_id` bigint DEFAULT NULL COMMENT '父级部门ID',
  `manager_id` bigint DEFAULT NULL COMMENT '部门负责人ID',
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent` (`parent_id`),
  KEY `idx_manager` (`manager_id`),
  FOREIGN KEY (`parent_id`) REFERENCES `departments` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`manager_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门表';
```

**字段说明**：
- 支持无限层级嵌套（通过parent_id自关联）
- 部门负责人用于审批流路由

### 2. users (员工表)

```sql
CREATE TABLE `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(150) NOT NULL UNIQUE COMMENT '工号/登录名',
  `password` varchar(128) NOT NULL,
  `full_name` varchar(50) NOT NULL COMMENT '真实姓名',
  `department_id` bigint NOT NULL COMMENT '所属部门',
  `base_hourly_rate` decimal(10,2) NOT NULL COMMENT '基础时薪',
  `openid` varchar(64) DEFAULT NULL UNIQUE COMMENT '微信OpenID',
  `status` smallint NOT NULL DEFAULT 1 COMMENT '状态: 1在职/0离职',
  `phone` varchar(11) DEFAULT NULL,
  `hire_date` date DEFAULT NULL COMMENT '入职日期',
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `is_staff` tinyint(1) NOT NULL DEFAULT 0,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_department` (`department_id`),
  KEY `idx_openid` (`openid`),
  FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`) ON DELETE PROTECT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='员工表';
```

**核心字段**：
- `base_hourly_rate`: 基础时薪，用于加班费计算
- `openid`: 微信小程序绑定标识

### 3. shift_definitions (班次定义表)

```sql
CREATE TABLE `shift_definitions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL COMMENT '班次名称',
  `start_time` time NOT NULL COMMENT '标准上班时间',
  `end_time` time NOT NULL COMMENT '标准下班时间',
  `is_cross_day` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否跨天',
  `color` varchar(7) NOT NULL DEFAULT '#409EFF' COMMENT 'UI颜色',
  `description` text COMMENT '班次说明',
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='班次定义表';
```

**示例数据**：
```sql
INSERT INTO shift_definitions (name, start_time, end_time, is_cross_day) VALUES
('早班', '07:00:00', '15:00:00', 0),
('中班', '15:00:00', '23:00:00', 0),
('大夜班', '20:00:00', '08:00:00', 1);
```

### 4. rosters (排班实例表)

```sql
CREATE TABLE `rosters` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `shift_id` bigint NOT NULL,
  `roster_date` date NOT NULL COMMENT '排班逻辑日期',
  `note` text,
  `created_by_id` bigint DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_date` (`user_id`, `roster_date`),
  KEY `idx_roster_date` (`roster_date`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`shift_id`) REFERENCES `shift_definitions` (`id`) ON DELETE PROTECT,
  FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='排班表';
```

**唯一约束**：
- 每个员工每天只能有一个排班（`uk_user_date`）

### 5. attendance_logs (考勤打卡表)

```sql
CREATE TABLE `attendance_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `punch_time` datetime(6) NOT NULL COMMENT '打卡时间',
  `type` varchar(3) NOT NULL COMMENT 'IN/OUT',
  `source` varchar(10) NOT NULL COMMENT 'WECHAT/WEB/MANUAL',
  `latitude` decimal(10,7) DEFAULT NULL,
  `longitude` decimal(10,7) DEFAULT NULL,
  `is_in_geofence` tinyint(1) NOT NULL DEFAULT 1,
  `note` text,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_time` (`user_id`, `punch_time`),
  KEY `idx_punch_time` (`punch_time`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打卡记录表';
```

### 6. overtime_records (加班核算表)

```sql
CREATE TABLE `overtime_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `roster_id` bigint DEFAULT NULL COMMENT '关联排班',
  `user_id` bigint NOT NULL,
  `work_date` date NOT NULL COMMENT '工作日期',
  `actual_start` datetime(6) NOT NULL COMMENT '实际上班时间',
  `actual_end` datetime(6) NOT NULL COMMENT '实际下班时间',
  `raw_ot_duration` decimal(5,2) NOT NULL COMMENT '原始加班时长',
  `approved_ot_duration` int NOT NULL COMMENT '规整后时长(0/4/8)',
  `multiplier` decimal(3,2) NOT NULL COMMENT '倍率(1.5/2.0/3.0)',
  `base_hourly_rate` decimal(10,2) NOT NULL COMMENT '时薪快照',
  `final_pay_amount` decimal(10,2) NOT NULL COMMENT '加班费',
  `status` varchar(10) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/APPROVED/REJECTED',
  `reason` text COMMENT '加班原因',
  `approved_by_id` bigint DEFAULT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `reject_reason` text,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_date` (`user_id`, `work_date`),
  KEY `idx_status` (`status`),
  KEY `idx_work_date` (`work_date`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`roster_id`) REFERENCES `rosters` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`approved_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='加班记录表';
```

**关键设计**：
- `base_hourly_rate`为快照字段，避免员工调薪影响历史数据
- `approved_ot_duration`存储0/4/8阶梯制规整后的值

## ER图关系

```
departments ──┐
             ├──> users ──┐
             │            ├──> rosters ──> shift_definitions
             │            │
             │            ├──> attendance_logs
             │            │
             │            └──> overtime_records
             │
             └──> shift_definitions
```

## 索引设计

### 高频查询索引

1. **排班查询**：`idx_roster_date`, `uk_user_date`
2. **考勤查询**：`idx_user_time`, `idx_punch_time`
3. **加班统计**：`idx_user_date`, `idx_work_date`, `idx_status`

## 数据迁移脚本

生成Django迁移文件：

```bash
python manage.py makemigrations
python manage.py migrate
```

## 初始化数据

```sql
-- 创建顶级部门
INSERT INTO departments (name, parent_id, manager_id) VALUES ('人民医院', NULL, NULL);

-- 创建班次定义
INSERT INTO shift_definitions (name, start_time, end_time, is_cross_day, color) VALUES
('早班7-15', '07:00:00', '15:00:00', 0, '#67C23A'),
('中班15-23', '15:00:00', '23:00:00', 0, '#E6A23C'),
('大夜班20-8', '20:00:00', '08:00:00', 1, '#F56C6C');
```
