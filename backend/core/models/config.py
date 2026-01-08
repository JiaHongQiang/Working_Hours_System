"""
系统配置模型 - 存储系统级配置
"""
from django.db import models


class SystemConfig(models.Model):
    """
    系统配置表 (sys_config)
    
    存储系统级配置，如打卡范围、医院坐标等
    使用 key-value 方式存储，便于扩展
    """
    
    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='配置键',
        help_text='配置项的唯一标识'
    )
    value = models.TextField(
        verbose_name='配置值',
        help_text='配置项的值，JSON格式存储复杂数据'
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='配置描述'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        db_table = 'sys_config'
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"
    
    @classmethod
    def get_value(cls, key, default=None):
        """获取配置值"""
        try:
            config = cls.objects.get(key=key)
            return config.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_value(cls, key, value, description=''):
        """设置配置值"""
        config, created = cls.objects.update_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        return config
    
    @classmethod
    def get_punch_config(cls):
        """获取打卡配置"""
        import json
        default_config = {
            'hospital_latitude': 39.9042,
            'hospital_longitude': 116.4074,
            'geofence_radius': 200,
            'hospital_name': '医院'
        }
        
        try:
            config = cls.objects.get(key='punch_config')
            return json.loads(config.value)
        except (cls.DoesNotExist, json.JSONDecodeError):
            return default_config
