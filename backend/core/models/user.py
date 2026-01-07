"""
员工模型 - 扩展Django用户系统
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """员工表 - 扩展Django用户模型"""
    
    # 基础信息
    full_name = models.CharField(max_length=50, verbose_name='真实姓名')
    department = models.ForeignKey(
        'Department',
        on_delete=models.PROTECT,
        related_name='employees',
        verbose_name='所属部门'
    )
    
    # 薪资相关
    base_hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='基础时薪'
    )
    
    # 微信小程序相关
    openid = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        verbose_name='微信OpenID'
    )
    
    # 状态
    STATUS_CHOICES = (
        (1, '在职'),
        (0, '离职'),
    )
    status = models.SmallIntegerField(
        default=1,
        choices=STATUS_CHOICES,
        verbose_name='员工状态'
    )
    
    # 扩展字段
    phone = models.CharField(max_length=11, blank=True, verbose_name='手机号')
    hire_date = models.DateField(null=True, blank=True, verbose_name='入职日期')
    
    class Meta:
        db_table = 'users'
        verbose_name = '员工'
        verbose_name_plural = '员工'
        ordering = ['-id']

    def __str__(self):
        return f"{self.full_name} ({self.username})"
    
    @property
    def is_active_employee(self):
        """是否在职员工"""
        return self.status == 1
