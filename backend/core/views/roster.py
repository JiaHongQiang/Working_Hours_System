"""
API视图 - 排班管理
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.db.models import Q
from core.models import ShiftDefinition, Roster
from core.serializers import (
    ShiftDefinitionSerializer,
    RosterSerializer,
    RosterCreateSerializer,
)


class ShiftDefinitionViewSet(viewsets.ModelViewSet):
    """班次定义ViewSet"""
    
    queryset = ShiftDefinition.objects.filter(is_active=True)
    serializer_class = ShiftDefinitionSerializer
    filterset_fields = ['is_cross_day', 'is_active']
    search_fields = ['name']
    ordering = ['start_time']


class RosterViewSet(viewsets.ModelViewSet):
    """排班管理ViewSet"""
    
    queryset = Roster.objects.select_related('user', 'shift', 'created_by').all()
    serializer_class = RosterSerializer
    filterset_fields = ['user', 'shift', 'roster_date']
    ordering = ['-roster_date', 'user']
    
    def perform_create(self, serializer):
        """创建排班时记录创建人"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        """
        批量创建排班
        POST /api/rosters/batch_create/
        
        Body:
        {
            "user_ids": [1, 2, 3],
            "shift_id": 1,
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",
            "exclude_weekends": false
        }
        """
        serializer = RosterCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        start_date = data['start_date']
        end_date = data['end_date']
        user_ids = data['user_ids']
        shift_id = data['shift_id']
        exclude_weekends = data.get('exclude_weekends', False)
        
        # 生成日期范围
        created_count = 0
        current_date = start_date
        
        while current_date <= end_date:
            # 如果排除周末且当前是周末，跳过
            if exclude_weekends and current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # 为每个员工创建排班
            for user_id in user_ids:
                Roster.objects.update_or_create(
                    user_id=user_id,
                    roster_date=current_date,
                    defaults={
                        'shift_id': shift_id,
                        'created_by': request.user
                    }
                )
                created_count += 1
            
            current_date += timedelta(days=1)
        
        return Response({
            'message': f'成功创建{created_count}条排班记录',
            'count': created_count
        })
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """
        获取日历视图数据
        GET /api/rosters/calendar/?start_date=2024-01-01&end_date=2024-01-31&user_id=1
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        user_id = request.query_params.get('user_id')
        
        if not start_date or not end_date:
            return Response(
                {'error': '缺少start_date或end_date参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            roster_date__gte=start_date,
            roster_date__lte=end_date
        )
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # 按日期分组
        rosters_by_date = {}
        for roster in queryset:
            date_str = roster.roster_date.isoformat()
            if date_str not in rosters_by_date:
                rosters_by_date[date_str] = []
            rosters_by_date[date_str].append(RosterSerializer(roster).data)
        
        return Response(rosters_by_date)
