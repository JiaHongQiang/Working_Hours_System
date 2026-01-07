"""
员工序列化器 - 支持医院复杂人事关系
"""
from rest_framework import serializers
from core.models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    """员工基础序列化器"""
    admin_dept_name = serializers.CharField(source='admin_dept.dept_name', read_only=True)
    scheduling_ward_name = serializers.CharField(source='scheduling_ward.dept_name', read_only=True)
    effective_dept_name = serializers.CharField(source='effective_scheduling_dept.dept_name', read_only=True)
    staff_category_display = serializers.CharField(source='get_staff_category_display', read_only=True)
    emp_status_display = serializers.CharField(source='get_emp_status_display', read_only=True)
    work_status_display = serializers.CharField(source='get_work_status_display', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'emp_code', 'username', 'full_name',
            'admin_dept', 'admin_dept_name',
            'scheduling_ward', 'scheduling_ward_name',
            'effective_dept_name',
            'staff_category', 'staff_category_display',
            'emp_status', 'emp_status_display',
            'job_title', 'is_scheduling_required',
            'base_hourly_rate',
            'work_status', 'work_status_display',
            'phone', 'hire_date', 'leave_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EmployeeListSerializer(serializers.ModelSerializer):
    """员工列表序列化器（精简版）"""
    admin_dept_name = serializers.CharField(source='admin_dept.dept_name', read_only=True)
    scheduling_ward_name = serializers.CharField(source='scheduling_ward.dept_name', read_only=True)
    staff_category_display = serializers.CharField(source='get_staff_category_display', read_only=True)
    emp_status_display = serializers.CharField(source='get_emp_status_display', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'emp_code', 'full_name',
            'admin_dept', 'admin_dept_name',
            'scheduling_ward', 'scheduling_ward_name',
            'staff_category', 'staff_category_display',
            'emp_status', 'emp_status_display',
            'job_title', 'is_scheduling_required', 'work_status'
        ]


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """员工创建序列化器"""
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Employee
        fields = [
            'username', 'password', 'emp_code', 'full_name',
            'admin_dept', 'scheduling_ward',
            'staff_category', 'emp_status', 'job_title',
            'is_scheduling_required', 'base_hourly_rate',
            'phone', 'id_card', 'hire_date'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        employee = Employee(**validated_data)
        employee.set_password(password)
        employee.save()
        return employee


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """员工更新序列化器"""
    
    class Meta:
        model = Employee
        fields = [
            'full_name', 'admin_dept', 'scheduling_ward',
            'staff_category', 'emp_status', 'job_title',
            'is_scheduling_required', 'base_hourly_rate',
            'phone', 'id_card', 'hire_date', 'leave_date', 'work_status'
        ]


class EmployeeSimpleSerializer(serializers.ModelSerializer):
    """员工简单序列化器（下拉选择用）"""
    label = serializers.SerializerMethodField()
    value = serializers.IntegerField(source='id', read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'emp_code', 'full_name', 'label', 'value']
    
    def get_label(self, obj):
        return f"{obj.full_name} ({obj.emp_code})"


class WechatBindSerializer(serializers.Serializer):
    """微信绑定序列化器"""
    openid = serializers.CharField(required=True)
    emp_code = serializers.CharField(required=True)
    phone = serializers.CharField(required=False)
    
    def validate_emp_code(self, value):
        if not Employee.objects.filter(emp_code=value).exists():
            raise serializers.ValidationError('工号不存在')
        return value


class SchedulingEmployeeSerializer(serializers.ModelSerializer):
    """排班员工序列化器（排班模块专用）"""
    effective_dept = serializers.SerializerMethodField()
    can_schedule = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'emp_code', 'full_name',
            'staff_category', 'job_title',
            'effective_dept', 'can_schedule'
        ]
    
    def get_effective_dept(self, obj):
        dept = obj.effective_scheduling_dept
        return {
            'id': dept.id,
            'name': dept.dept_name,
            'is_ward': dept.is_ward
        }
    
    def get_can_schedule(self, obj):
        """判断是否可以排班"""
        return obj.is_scheduling_required and obj.is_active_employee
