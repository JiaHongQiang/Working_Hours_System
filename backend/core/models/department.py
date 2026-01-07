"""
部门模型 - 支持无限层级嵌套
"""
from django.db import models


class Department(models.Model):
    """部门表 - 支持层级结构"""
    name = models.CharField(max_length=100, verbose_name='部门名称')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='父级部门'
    )
    manager = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name='部门负责人'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'departments'
        verbose_name = '部门'
        verbose_name_plural = '部门'
        ordering = ['id']

    def __str__(self):
        return self.name

    def get_full_path(self):
        """获取部门完整路径，如：医院/内科/心血管科"""
        if self.parent:
            return f"{self.parent.get_full_path()}/{self.name}"
        return self.name
