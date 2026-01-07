"""
班次定义模型
"""
from django.db import models


class ShiftDefinition(models.Model):
    """班次定义表 - 存储可重用的班次模板"""
    
    name = models.CharField(max_length=50, verbose_name='班次名称')
    start_time = models.TimeField(verbose_name='标准上班时间')
    end_time = models.TimeField(verbose_name='标准下班时间')
    
    # 跨夜班标识
    is_cross_day = models.BooleanField(
        default=False,
        verbose_name='是否跨天',
        help_text='如大夜班20:00-次日08:00'
    )
    
    # UI显示
    color = models.CharField(
        max_length=7,
        default='#409EFF',
        verbose_name='UI颜色',
        help_text='用于前端日历展示，如#409EFF'
    )
    
    # 备注
    description = models.TextField(blank=True, verbose_name='班次说明')
    
    # 启用状态
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'shift_definitions'
        verbose_name = '班次定义'
        verbose_name_plural = '班次定义'
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')})"
    
    def get_duration_hours(self):
        """计算班次时长（小时）"""
        from datetime import datetime, timedelta
        
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        
        if self.is_cross_day or end < start:
            end += timedelta(days=1)
        
        duration = (end - start).total_seconds() / 3600
        return round(duration, 2)
