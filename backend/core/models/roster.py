"""
排班实例模型
"""
from django.db import models


class Roster(models.Model):
    """排班表 - 记录具体的排班安排"""
    
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='rosters',
        verbose_name='员工'
    )
    shift = models.ForeignKey(
        'ShiftDefinition',
        on_delete=models.PROTECT,
        verbose_name='班次'
    )
    roster_date = models.DateField(
        verbose_name='排班日期',
        help_text='逻辑日期：即使跨夜班，仍属于当天'
    )
    
    # 审计字段
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_rosters',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 备注
    note = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        db_table = 'rosters'
        verbose_name = '排班记录'
        verbose_name_plural = '排班记录'
        unique_together = [['user', 'roster_date']]
        ordering = ['-roster_date', 'user']
        indexes = [
            models.Index(fields=['roster_date']),
            models.Index(fields=['user', 'roster_date']),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.roster_date} - {self.shift.name}"
    
    def get_scheduled_times(self):
        """获取计划上下班时间"""
        from core.services.time_calculator import TimeCalculator
        
        return TimeCalculator.calculate_scheduled_time(
            roster_date=self.roster_date,
            start_time=self.shift.start_time,
            end_time=self.shift.end_time,
            is_cross_day=self.shift.is_cross_day
        )
