"""
DRF序列化器 - 员工相关
"""
from rest_framework import serializers
from core.models import User


class UserSerializer(serializers.ModelSerializer):
    """员工序列化器"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'email', 'phone',
            'department', 'department_name', 'base_hourly_rate',
            'hire_date', 'status', 'status_display',
            'is_active', 'is_staff', 'date_joined'
        ]
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        """创建员工时，正确处理密码"""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class UserSimpleSerializer(serializers.ModelSerializer):
    """员工简单序列化器 - 用于下拉选择等场景"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']


class WechatBindSerializer(serializers.Serializer):
    """微信小程序绑定序列化器"""
    
    code = serializers.CharField(required=True, help_text='微信登录code')
    username = serializers.CharField(required=True, help_text='员工工号')
    password = serializers.CharField(required=True, write_only=True, help_text='员工密码')
