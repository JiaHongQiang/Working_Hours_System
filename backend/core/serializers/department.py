"""
DRF序列化器 - 部门相关
"""
from rest_framework import serializers
from core.models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    """部门序列化器"""
    
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    full_path = serializers.CharField(read_only=True)
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'parent', 'parent_name',
            'manager', 'manager_name', 'full_path',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DepartmentTreeSerializer(serializers.ModelSerializer):
    """部门树形序列化器 - 用于前端树形组件"""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'manager', 'children']
    
    def get_children(self, obj):
        """递归获取子部门"""
        children = obj.children.all()
        return DepartmentTreeSerializer(children, many=True).data
