"""
加班核算模型
"""
from django.db import models


class OvertimeRecord(models.Model):
    """加班记录表 - 存储经过计算的加班数据"""
    
    STATUS_CHOICES = (
        ('PENDING', '待审批'),
        ('APPROVED', '已通过'),
        ('REJECTED', '已驳回'),
    )
    
    # 关联数据
    roster = models.ForeignKey(
        'Roster',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='关联排班',
        help_text='休息日临时召回时可能无排班'
    )
    user = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='overtime_records',
        verbose_name='员工'
    )
    work_date = models.DateField(verbose_name='工作日期')
    
    # 时间数据
    actual_start = models.DateTimeField(verbose_name='实际上班时间')
    actual_end = models.DateTimeField(verbose_name='实际下班时间')
    
    # 加班计算
    raw_ot_duration = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='原始加班时长(小时)',
        help_text='未经阶梯制规整的原始值'
    )
    approved_ot_duration = models.IntegerField(
        verbose_name='规整后时长(小时)',
        help_text='经0-4-8阶梯制规整后的值'
    )
    
    # 薪资计算
    multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        verbose_name='薪资倍率',
        help_text='1.5/2.0/3.0'
    )
    base_hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='基础时薪',
        help_text='快照，避免员工调薪影响历史数据'
    )
    final_pay_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='加班费金额'
    )
    
    # 审批流程
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name='审批状态'
    )
    reason = models.TextField(verbose_name='加班原因', blank=True)
    
    # 审批人员
    approved_by = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_overtimes',
        verbose_name='审批人'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    reject_reason = models.TextField(blank=True, verbose_name='驳回原因')
    
    # 审计字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'overtime_records'
        verbose_name = '加班记录'
        verbose_name_plural = '加班记录'
        ordering = ['-work_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'work_date']),
            models.Index(fields=['status']),
            models.Index(fields=['work_date']),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.work_date} - {self.approved_ot_duration}h × {self.multiplier}"
    
    @property
    def is_pending(self):
        """是否待审批"""
        return self.status == 'PENDING'
    
    @property
    def is_approved(self):
        """是否已通过"""
        return self.status == 'APPROVED'
