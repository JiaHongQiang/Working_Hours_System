"""
Django Admin后台配置
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import (
    Department,
    User,
    ShiftDefinition,
    Roster,
    AttendanceLog,
    OvertimeRecord,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """部门管理"""
    list_display = ['id', 'name', 'parent', 'manager', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    raw_id_fields = ['parent', 'manager']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """员工管理"""
    list_display = ['id', 'username', 'full_name', 'department', 'base_hourly_rate', 'status', 'is_staff']
    list_filter = ['status', 'is_staff', 'department']
    search_fields = ['username', 'full_name', 'phone']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {
            'fields': ('full_name', 'department', 'base_hourly_rate', 'phone', 'hire_date', 'status')
        }),
        ('微信小程序', {
            'fields': ('openid',)
        }),
    )


@admin.register(ShiftDefinition)
class ShiftDefinitionAdmin(admin.ModelAdmin):
    """班次定义管理"""
    list_display = ['id', 'name', 'start_time', 'end_time', 'is_cross_day', 'color', 'is_active']
    list_filter = ['is_cross_day', 'is_active']
    search_fields = ['name']


@admin.register(Roster)
class RosterAdmin(admin.ModelAdmin):
    """排班管理"""
    list_display = ['id', 'user', 'shift', 'roster_date', 'created_by', 'created_at']
    list_filter = ['roster_date', 'shift']
    search_fields = ['user__full_name', 'user__username']
    raw_id_fields = ['user', 'created_by']
    date_hierarchy = 'roster_date'


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    """考勤记录管理"""
    list_display = ['id', 'user', 'punch_time', 'type', 'source', 'is_in_geofence']
    list_filter = ['type', 'source', 'is_in_geofence', 'punch_time']
    search_fields = ['user__full_name', 'user__username']
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
    search_fields = ['user__full_name', 'user__username', 'reason']
    raw_id_fields = ['user', 'roster', 'approved_by']
    date_hierarchy = 'work_date'
    
    readonly_fields = ['created_at', 'updated_at']
