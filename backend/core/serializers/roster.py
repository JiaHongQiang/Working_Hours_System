"""
DRF序列化器 - 班次和排班相关
"""
from rest_framework import serializers
from core.models import ShiftDefinition, Roster


class ShiftDefinitionSerializer(serializers.ModelSerializer):
    """班次定义序列化器"""
    
    duration_hours = serializers.FloatField(source='get_duration_hours', read_only=True)
    
    class Meta:
        model = ShiftDefinition
        fields = [
            'id', 'name', 'start_time', 'end_time', 'is_cross_day',
            'color', 'description', 'is_active', 'duration_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RosterSerializer(serializers.ModelSerializer):
    """排班序列化器"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    shift_color = serializers.CharField(source='shift.color', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Roster
        fields = [
            'id', 'user', 'user_name', 'shift', 'shift_name', 'shift_color',
            'roster_date', 'note', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class RosterCreateSerializer(serializers.Serializer):
    """批量创建排班序列化器"""
    
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='员工ID列表'
    )
    shift_id = serializers.IntegerField(help_text='班次ID')
    start_date = serializers.DateField(help_text='开始日期')
    end_date = serializers.DateField(help_text='结束日期')
    exclude_weekends = serializers.BooleanField(
        default=False,
        help_text='是否排除周末'
    )


class RosterCalendarSerializer(serializers.Serializer):
    """日历视图序列化器 - 用于前端日历展示"""
    
    date = serializers.DateField()
    rosters = RosterSerializer(many=True)
