"""
科室/组织模型 - 支持医院复杂组织架构
符合医院业务场景：行政科室、临床科室、病区(护理单元)、医技科室
"""
from django.db import models


class Department(models.Model):
    """
    科室/组织表 (sys_department)
    
    支持无限层级树形结构，核心设计要点：
    1. 支持多种科室类型（行政/临床/病区/医技）
    2. 病区(WARD)是核心排班单位
    3. 科主任/护士长作为管理者
    """
    
    # ========== 科室类型枚举 ==========
    class DeptType(models.TextChoices):
        ADMIN = 'ADMIN', '行政科室'
        CLINICAL = 'CLINICAL', '临床科室'
        WARD = 'WARD', '病区/护理单元'  # 核心排班单位
        TECH = 'TECH', '医技科室'
    
    # ========== 基础信息 ==========
    dept_name = models.CharField(
        max_length=100,
        verbose_name='科室名称'
    )
    dept_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='科室编码',
        help_text='用于对接HIS系统的唯一标识'
    )
    dept_type = models.CharField(
        max_length=20,
        choices=DeptType.choices,
        default=DeptType.CLINICAL,
        verbose_name='科室类型'
    )
    
    # ========== 层级结构 ==========
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='上级科室',
        help_text='用于构建树形结构，如：内科 -> 心内科 -> 心内一病区'
    )
    
    # ========== 管理者 ==========
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name='科室负责人',
        help_text='科主任/护士长'
    )
    
    # ========== 排序与状态 ==========
    sort_order = models.IntegerField(
        default=0,
        verbose_name='排序号'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    
    # ========== 时间戳 ==========
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sys_department'
        verbose_name = '科室'
        verbose_name_plural = '科室管理'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"[{self.get_dept_type_display()}] {self.dept_name}"

    def get_full_path(self):
        """获取科室完整路径，如：医院/内科/心血管科/心内一病区"""
        if self.parent:
            return f"{self.parent.get_full_path()} / {self.dept_name}"
        return self.dept_name
    
    @property
    def is_ward(self):
        """判断是否为病区(核心排班单位)"""
        return self.dept_type == self.DeptType.WARD
    
    def get_all_children(self):
        """递归获取所有子科室"""
        children = list(self.children.filter(is_active=True))
        for child in self.children.filter(is_active=True):
            children.extend(child.get_all_children())
        return children
    
    def get_all_wards(self):
        """获取该科室下所有病区(排班单位)"""
        wards = []
        if self.is_ward:
            wards.append(self)
        for child in self.get_all_children():
            if child.is_ward:
                wards.append(child)
        return wards
