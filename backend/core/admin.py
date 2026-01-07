"""
Django Admin后台配置 - 医院人员与组织管理
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import (
    Department,
    Employee,
    ShiftDefinition,
    Roster,
    AttendanceLog,
    OvertimeRecord,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """科室管理"""
    list_display = [
        'id', 'dept_code', 'dept_name', 'dept_type', 
        'parent', 'manager', 'is_active', 'sort_order'
    ]
    list_filter = ['dept_type', 'is_active', 'created_at']
    search_fields = ['dept_name', 'dept_code']
    raw_id_fields = ['parent', 'manager']
    list_editable = ['sort_order', 'is_active']
    ordering = ['sort_order', 'id']
    
    fieldsets = (
        ('基础信息', {
            'fields': ('dept_code', 'dept_name', 'dept_type')
        }),
        ('层级结构', {
            'fields': ('parent', 'manager')
        }),
        ('状态', {
            'fields': ('is_active', 'sort_order')
        }),
    )


@admin.register(Employee)
class EmployeeAdmin(BaseUserAdmin):
    """人员管理"""
    list_display = [
        'id', 'emp_code', 'full_name', 'staff_category', 'emp_status',
        'admin_dept', 'scheduling_ward', 'job_title', 'work_status', 'is_scheduling_required'
    ]
    list_filter = [
        'staff_category', 'emp_status', 'work_status', 
        'is_scheduling_required', 'admin_dept'
    ]
    search_fields = ['emp_code', 'full_name', 'phone', 'username']
    raw_id_fields = ['admin_dept', 'scheduling_ward']
    list_editable = ['is_scheduling_required']
    ordering = ['admin_dept', 'emp_code']
    
    # 重新定义fieldsets以适应医院业务
    fieldsets = (
        ('登录信息', {
            'fields': ('username', 'password')
        }),
        ('基础信息', {
            'fields': ('emp_code', 'full_name', 'phone', 'id_card')
        }),
        ('组织归属', {
            'fields': ('admin_dept', 'scheduling_ward'),
            'description': '行政归属为人事关系科室，排班归属为实际考勤科室'
        }),
        ('人员分类', {
            'fields': ('staff_category', 'emp_status', 'job_title')
        }),
        ('排班考勤', {
            'fields': ('is_scheduling_required', 'base_hourly_rate')
        }),
        ('状态信息', {
            'fields': ('work_status', 'hire_date', 'leave_date')
        }),
        ('微信小程序', {
            'fields': ('openid',),
            'classes': ('collapse',)
        }),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 
                'emp_code', 'full_name', 'admin_dept', 
                'staff_category', 'emp_status'
            ),
        }),
    )


@admin.register(ShiftDefinition)
class ShiftDefinitionAdmin(admin.ModelAdmin):
    """班次定义管理"""
    list_display = ['id', 'name', 'start_time', 'end_time', 'is_cross_day', 'color', 'is_active']
    list_filter = ['is_cross_day', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active', 'color']


@admin.register(Roster)
class RosterAdmin(admin.ModelAdmin):
    """排班管理"""
    list_display = ['id', 'user', 'shift', 'roster_date', 'created_by', 'created_at']
    list_filter = ['roster_date', 'shift']
    search_fields = ['user__full_name', 'user__emp_code']
    raw_id_fields = ['user', 'created_by']
    date_hierarchy = 'roster_date'


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    """考勤记录管理"""
    list_display = ['id', 'user', 'punch_time', 'type', 'source', 'is_in_geofence']
    list_filter = ['type', 'source', 'is_in_geofence', 'punch_time']
    search_fields = ['user__full_name', 'user__emp_code']
    raw_id_fields = ['user']
    date_hierarchy = 'punch_time'


@admin.register(OvertimeRecord)
class OvertimeRecordAdmin(admin.ModelAdmin):
    """加班记录管理"""
    list_display = [
        'id', 'user', 'work_date', 'raw_ot_duration', 'approved_ot_duration',
        'multiplier', 'final_pay_amount', 'status'
    ]
    list_filter = ['status', 'work_date', 'multiplier']
    search_fields = ['user__full_name', 'user__emp_code', 'reason']
    raw_id_fields = ['user', 'roster', 'approved_by']
    date_hierarchy = 'work_date'
    
    readonly_fields = ['created_at', 'updated_at']
