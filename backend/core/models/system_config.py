"""
系统配置模型
"""
from django.db import models


class SystemConfig(models.Model):
    """系统配置表"""
    
    # 配置键（唯一）
    config_key = models.CharField('配置键', max_length=50, unique=True, db_index=True)
    
    # 配置值
    config_value = models.TextField('配置值')
    
    # 配置描述
    description = models.CharField('描述', max_length=200, blank=True, default='')
    
    # 配置分组
    group = models.CharField('分组', max_length=50, default='general')
    
    # 是否启用
    is_active = models.BooleanField('启用', default=True)
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'system_config'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        ordering = ['group', 'config_key']
    
    def __str__(self):
        return f"{self.config_key}: {self.config_value}"
