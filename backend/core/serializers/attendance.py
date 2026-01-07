"""
DRF序列化器 - 考勤相关
"""
from rest_framework import serializers
from core.models import AttendanceLog


class AttendanceLogSerializer(serializers.ModelSerializer):
    """考勤打卡序列化器"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    
    class Meta:
        model = AttendanceLog
        fields = [
            'id', 'user', 'user_name', 'punch_time',
            'type', 'type_display', 'source', 'source_display',
            'latitude', 'longitude', 'is_in_geofence',
            'note', 'created_at'
        ]
        read_only_fields = ['user', 'is_in_geofence', 'created_at']


class PunchRequestSerializer(serializers.Serializer):
    """打卡请求序列化器 - 小程序端使用"""
    
    type = serializers.ChoiceField(
        choices=['IN', 'OUT'],
        help_text='打卡类型：IN=上班，OUT=下班'
    )
    latitude = serializers.DecimalField(
        max_digits=10,
        decimal_places=7,
        required=False,
        allow_null=True,
        help_text='纬度'
    )
    longitude = serializers.DecimalField(
        max_digits=10,
        decimal_places=7,
        required=False,
        allow_null=True,
        help_text='经度'
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='备注'
    )
