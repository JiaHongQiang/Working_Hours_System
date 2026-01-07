"""
考勤打卡模型
"""
from django.db import models


class AttendanceLog(models.Model):
    """打卡记录表 - 记录原始考勤数据"""
    
    PUNCH_TYPE_CHOICES = (
        ('IN', '上班'),
        ('OUT', '下班'),
    )
    
    SOURCE_CHOICES = (
        ('WECHAT', '微信小程序'),
        ('WEB', 'Web管理端'),
        ('MANUAL', '手动补录'),
    )
    
    user = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='attendance_logs',
        verbose_name='员工'
    )
    punch_time = models.DateTimeField(verbose_name='打卡时间')
    type = models.CharField(
        max_length=3,
        choices=PUNCH_TYPE_CHOICES,
        verbose_name='打卡类型'
    )
    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default='WECHAT',
        verbose_name='数据来源'
    )
    
    # 地理位置信息
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name='纬度'
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name='经度'
    )
    
    # 地理围栏验证
    is_in_geofence = models.BooleanField(
        default=True,
        verbose_name='是否在围栏内',
        help_text='False表示异地打卡，需特殊审批'
    )
    
    # 备注
    note = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'attendance_logs'
        verbose_name = '打卡记录'
        verbose_name_plural = '打卡记录'
        ordering = ['-punch_time']
        indexes = [
            models.Index(fields=['user', 'punch_time']),
            models.Index(fields=['punch_time']),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.get_type_display()} - {self.punch_time}"
