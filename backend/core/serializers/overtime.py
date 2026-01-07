"""
DRF序列化器 - 加班相关
"""
from rest_framework import serializers
from core.models import OvertimeRecord


class OvertimeRecordSerializer(serializers.ModelSerializer):
    """加班记录序列化器"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
    class Meta:
        model = OvertimeRecord
        fields = [
            'id', 'roster', 'user', 'user_name', 'work_date',
            'actual_start', 'actual_end',
            'raw_ot_duration', 'approved_ot_duration',
            'multiplier', 'base_hourly_rate', 'final_pay_amount',
            'status', 'status_display', 'reason',
            'approved_by', 'approved_by_name', 'approved_at',
            'reject_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'approved_ot_duration', 'multiplier',
            'base_hourly_rate', 'final_pay_amount',
            'approved_by', 'approved_at',
            'created_at', 'updated_at'
        ]


class OvertimeApplySerializer(serializers.Serializer):
    """加班申报序列化器 - 员工端使用"""
    
    work_date = serializers.DateField(help_text='工作日期')
    actual_start = serializers.DateTimeField(help_text='实际上班时间')
    actual_end = serializers.DateTimeField(help_text='实际下班时间')
    reason = serializers.CharField(help_text='加班原因')


class OvertimeApprovalSerializer(serializers.Serializer):
    """加班审批序列化器 - 管理端使用"""
    
    action = serializers.ChoiceField(
        choices=['approve', 'reject'],
        help_text='审批动作：approve=通过，reject=驳回'
    )
    reject_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='驳回原因（驳回时必填）'
    )
    adjust_duration = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True,
        help_text='调整后的加班时长（管理员可手动调整）'
    )


class OvertimeStatisticsSerializer(serializers.Serializer):
    """加班统计序列化器"""
    
    user_id = serializers.IntegerField()
    user_name = serializers.CharField()
    department_name = serializers.CharField()
    total_overtime_hours = serializers.IntegerField()
    overtime_1_5x_hours = serializers.IntegerField()
    overtime_2_0x_hours = serializers.IntegerField()
    overtime_3_0x_hours = serializers.IntegerField()
    total_pay_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
