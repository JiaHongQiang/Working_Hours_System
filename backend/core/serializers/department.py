"""
科室/组织序列化器
"""
from rest_framework import serializers
from core.models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    """科室基础序列化器"""
    parent_name = serializers.CharField(source='parent.dept_name', read_only=True)
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    dept_type_display = serializers.CharField(source='get_dept_type_display', read_only=True)
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    
    class Meta:
        model = Department
        fields = [
            'id', 'dept_code', 'dept_name', 'dept_type', 'dept_type_display',
            'parent', 'parent_name', 'manager', 'manager_name',
            'sort_order', 'is_active', 'full_path',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DepartmentTreeSerializer(serializers.ModelSerializer):
    """科室树形结构序列化器"""
    children = serializers.SerializerMethodField()
    dept_type_display = serializers.CharField(source='get_dept_type_display', read_only=True)
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'dept_code', 'dept_name', 'dept_type', 'dept_type_display',
            'manager', 'manager_name', 'sort_order', 'is_active',
            'employee_count', 'children'
        ]
    
    def get_children(self, obj):
        """递归获取子科室"""
        children = obj.children.filter(is_active=True).order_by('sort_order', 'id')
        return DepartmentTreeSerializer(children, many=True).data
    
    def get_employee_count(self, obj):
        """获取科室员工数量（包括行政归属和排班归属）"""
        admin_count = obj.admin_employees.filter(work_status=1).count()
        scheduling_count = obj.scheduling_employees.filter(work_status=1).count()
        return {
            'admin': admin_count,
            'scheduling': scheduling_count,
            'total': admin_count  # 以行政归属为准
        }


class DepartmentSimpleSerializer(serializers.ModelSerializer):
    """科室简单序列化器（下拉选择用）"""
    label = serializers.CharField(source='dept_name', read_only=True)
    value = serializers.IntegerField(source='id', read_only=True)
    
    class Meta:
        model = Department
        fields = ['id', 'dept_code', 'dept_name', 'dept_type', 'label', 'value']


class WardListSerializer(serializers.ModelSerializer):
    """病区列表序列化器（排班选择用）"""
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    
    class Meta:
        model = Department
        fields = ['id', 'dept_code', 'dept_name', 'full_path']
