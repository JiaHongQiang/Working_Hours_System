"""
员工模型 - 支持医院复杂人事关系
核心设计：双部门归属、人员类别、用工性质
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Employee(AbstractUser):
    """
    员工表 (sys_employee)
    
    医院业务核心设计要点：
    1. 双部门归属：行政归属(admin_dept) + 排班归属(scheduling_ward)
    2. 人员类别区分：医生/护士/医技/行政
    3. 用工性质区分：正式/合同/实习/规培
    4. 考勤统计优先使用 scheduling_ward，若为空则回退到 admin_dept
    """
    
    # ========== 人员类别枚举 ==========
    class StaffCategory(models.TextChoices):
        DOCTOR = 'DOCTOR', '医生'
        NURSE = 'NURSE', '护士'
        TECH = 'TECH', '医技人员'
        ADMIN = 'ADMIN', '行政人员'
    
    # ========== 用工性质枚举 ==========
    class EmpStatus(models.TextChoices):
        REGULAR = 'REGULAR', '正式在编'
        CONTRACT = 'CONTRACT', '合同制'
        INTERN = 'INTERN', '实习生'      # 不计薪
        RESIDENT = 'RESIDENT', '规培生'
    
    # ========== 员工状态枚举 ==========
    class WorkStatus(models.IntegerChoices):
        ACTIVE = 1, '在职'
        RESIGNED = 0, '离职'
        SUSPENDED = 2, '停职'
    
    # ========== 基础信息 ==========
    emp_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='工号',
        help_text='员工工号/打卡ID，唯一标识'
    )
    full_name = models.CharField(
        max_length=50,
        verbose_name='真实姓名'
    )
    
    # ========== 双部门归属（核心业务逻辑） ==========
    admin_dept = models.ForeignKey(
        'Department',
        on_delete=models.PROTECT,
        related_name='admin_employees',
        verbose_name='行政归属科室',
        help_text='人事关系所在科室（如：护理部、内科）'
    )
    scheduling_ward = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scheduling_employees',
        verbose_name='排班归属病区',
        help_text='实际排班和考勤所在的病区/科室，为空时使用行政归属科室'
    )
    
    # ========== 人员类别与用工性质 ==========
    staff_category = models.CharField(
        max_length=20,
        choices=StaffCategory.choices,
        default=StaffCategory.NURSE,
        verbose_name='人员类别'
    )
    emp_status = models.CharField(
        max_length=20,
        choices=EmpStatus.choices,
        default=EmpStatus.CONTRACT,
        verbose_name='用工性质'
    )
    
    # ========== 职称与岗位 ==========
    job_title = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='职称',
        help_text='如：主任医师、护士长、主管护师'
    )
    
    # ========== 排班考勤相关 ==========
    is_scheduling_required = models.BooleanField(
        default=True,
        verbose_name='是否参与排班考勤',
        help_text='行政人员或特殊岗位可能不参与常规排班'
    )
    
    # ========== 薪资相关 ==========
    base_hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='基础时薪',
        help_text='用于加班费计算（实习生不计薪）'
    )
    
    # ========== 微信小程序相关 ==========
    openid = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        verbose_name='微信OpenID'
    )
    
    # ========== 员工状态 ==========
    work_status = models.SmallIntegerField(
        default=WorkStatus.ACTIVE,
        choices=WorkStatus.choices,
        verbose_name='员工状态'
    )
    
    # ========== 扩展信息 ==========
    phone = models.CharField(max_length=11, blank=True, verbose_name='手机号')
    id_card = models.CharField(max_length=18, blank=True, verbose_name='身份证号')
    hire_date = models.DateField(null=True, blank=True, verbose_name='入职日期')
    leave_date = models.DateField(null=True, blank=True, verbose_name='离职日期')
    
    # ========== 时间戳 ==========
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sys_employee'
        verbose_name = '员工'
        verbose_name_plural = '人员管理'
        ordering = ['admin_dept', 'emp_code']

    def __str__(self):
        return f"{self.full_name} ({self.emp_code})"
    
    # ========== 核心业务方法 ==========
    
    @property
    def effective_scheduling_dept(self):
        """
        获取有效的考勤归属部门
        核心逻辑：优先使用 scheduling_ward，若为空则回退到 admin_dept
        """
        return self.scheduling_ward if self.scheduling_ward else self.admin_dept
    
    @property
    def is_active_employee(self):
        """是否在职员工"""
        return self.work_status == self.WorkStatus.ACTIVE
    
    @property
    def is_intern(self):
        """是否实习生（不计薪）"""
        return self.emp_status == self.EmpStatus.INTERN
    
    @property
    def should_calculate_salary(self):
        """是否需要计算薪资（实习生不计薪）"""
        return not self.is_intern and self.is_active_employee
    
    def get_display_dept(self):
        """获取显示用的部门名称"""
        if self.scheduling_ward:
            return f"{self.admin_dept.dept_name} (排班于: {self.scheduling_ward.dept_name})"
        return self.admin_dept.dept_name


# 为了兼容之前的代码，创建别名
User = Employee
