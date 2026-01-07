"""
API视图 - 加班管理
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, Q
from core.models import OvertimeRecord, Roster
from core.serializers import (
    OvertimeRecordSerializer,
    OvertimeApplySerializer,
    OvertimeApprovalSerializer,
    OvertimeStatisticsSerializer,
)
from core.services import TimeCalculator, OvertimeCalculator


class OvertimeRecordViewSet(viewsets.ModelViewSet):
    """加班记录ViewSet"""
    
    queryset = OvertimeRecord.objects.select_related('user', 'roster', 'approved_by').all()
    serializer_class = OvertimeRecordSerializer
    filterset_fields = ['user', 'status', 'work_date']
    ordering = ['-work_date', '-created_at']
    
    @action(detail=False, methods=['post'])
    def apply(self, request):
        """
        申报加班
        POST /api/overtime/apply/
        
        Body:
        {
            "work_date": "2024-01-15",
            "actual_start": "2024-01-15T08:00:00",
            "actual_end": "2024-01-15T20:00:00",
            "reason": "急诊手术"
        }
        """
        serializer = OvertimeApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        work_date = data['work_date']
        actual_start = data['actual_start']
        actual_end = data['actual_end']
        
        # 查找当天排班
        try:
            roster = Roster.objects.get(user=request.user, roster_date=work_date)
            has_roster = True
        except Roster.DoesNotExist:
            roster = None
            has_roster = False
        
        # 计算加班时长
        if has_roster:
            scheduled_start, scheduled_end = roster.get_scheduled_times()
            raw_overtime = TimeCalculator.calculate_overtime_hours(
                actual_end, scheduled_end
            )
        else:
            # 无排班，整个工作时长都算加班
            raw_overtime = TimeCalculator.calculate_work_duration(
                actual_start, actual_end
            )
        
        # 使用加班计算引擎
        calculator = OvertimeCalculator()
        result = calculator.calculate_full_overtime(
            raw_hours=raw_overtime,
            work_date=work_date,
            has_roster=has_roster,
            base_hourly_rate=float(request.user.base_hourly_rate)
        )
        
        # 创建加班记录
        overtime_record = OvertimeRecord.objects.create(
            roster=roster,
            user=request.user,
            work_date=work_date,
            actual_start=actual_start,
            actual_end=actual_end,
            raw_ot_duration=result['raw_hours'],
            approved_ot_duration=result['approved_hours'],
            multiplier=result['multiplier'],
            base_hourly_rate=request.user.base_hourly_rate,
            final_pay_amount=result['pay_amount'],
            status='PENDING',
            reason=data['reason']
        )
        
        return Response({
            'message': '加班申报成功',
            'data': OvertimeRecordSerializer(overtime_record).data
        })
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        审批加班
        POST /api/overtime/{id}/approve/
        
        Body:
        {
            "action": "approve",  // 或 "reject"
            "reject_reason": "",
            "adjust_duration": 6.0  // 可选，管理员调整时长
        }
        """
        overtime_record = self.get_object()
        
        if overtime_record.status != 'PENDING':
            return Response(
                {'error': '该记录已处理，无法重复审批'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OvertimeApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        action = data['action']
        
        if action == 'approve':
            # 如果管理员调整了时长，重新计算
            if 'adjust_duration' in data and data['adjust_duration'] is not None:
                calculator = OvertimeCalculator()
                adjusted = calculator.apply_step_function(float(data['adjust_duration']))
                overtime_record.approved_ot_duration = adjusted
                overtime_record.final_pay_amount = calculator.calculate_pay(
                    adjusted,
                    float(overtime_record.base_hourly_rate),
                    float(overtime_record.multiplier)
                )
            
            overtime_record.status = 'APPROVED'
            overtime_record.approved_by = request.user
            overtime_record.approved_at = timezone.now()
            
        else:  # reject
            if not data.get('reject_reason'):
                return Response(
                    {'error': '驳回时必须填写原因'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            overtime_record.status = 'REJECTED'
            overtime_record.reject_reason = data['reject_reason']
            overtime_record.approved_by = request.user
            overtime_record.approved_at = timezone.now()
        
        overtime_record.save()
        
        return Response({
            'message': '审批成功',
            'data': OvertimeRecordSerializer(overtime_record).data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        加班统计
        GET /api/overtime/statistics/?start_date=2024-01-01&end_date=2024-01-31&department_id=1
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        department_id = request.query_params.get('department_id')
        
        if not start_date or not end_date:
            return Response(
                {'error': '缺少start_date或end_date参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 查询已通过的加班记录
        queryset = OvertimeRecord.objects.filter(
            status='APPROVED',
            work_date__gte=start_date,
            work_date__lte=end_date
        ).select_related('user', 'user__department')
        
        if department_id:
            queryset = queryset.filter(user__department_id=department_id)
        
        # 按员工分组统计
        from django.db.models import Case, When, IntegerField
        
        stats = queryset.values('user__id', 'user__full_name', 'user__department__name').annotate(
            total_hours=Sum('approved_ot_duration'),
            hours_1_5x=Sum(Case(
                When(multiplier=1.5, then='approved_ot_duration'),
                default=0,
                output_field=IntegerField()
            )),
            hours_2_0x=Sum(Case(
                When(multiplier=2.0, then='approved_ot_duration'),
                default=0,
                output_field=IntegerField()
            )),
            hours_3_0x=Sum(Case(
                When(multiplier=3.0, then='approved_ot_duration'),
                default=0,
                output_field=IntegerField()
            )),
            total_pay=Sum('final_pay_amount')
        )
        
        return Response(list(stats))
