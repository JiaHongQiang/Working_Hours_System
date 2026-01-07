"""
API视图 - 考勤管理
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from core.models import AttendanceLog
from core.serializers import AttendanceLogSerializer, PunchRequestSerializer
from core.services import GeofenceValidator


class AttendanceLogViewSet(viewsets.ModelViewSet):
    """考勤打卡ViewSet"""
    
    queryset = AttendanceLog.objects.select_related('user').all()
    serializer_class = AttendanceLogSerializer
    filterset_fields = ['user', 'type', 'source', 'is_in_geofence']
    ordering = ['-punch_time']
    
    @action(detail=False, methods=['post'])
    def punch(self, request):
        """
        打卡接口
        POST /api/attendance/punch/
        
        Body:
        {
            "type": "IN",  // 或 "OUT"
            "latitude": 39.9042,
            "longitude": 116.4074,
            "note": ""
        }
        """
        serializer = PunchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # 地理围栏验证
        is_in_geofence = True
        if latitude and longitude:
            is_in_geofence, distance = GeofenceValidator.is_in_geofence(
                latitude, longitude
            )
            if not is_in_geofence:
                return Response({
                    'error': '您不在医院打卡范围内',
                    'distance': round(distance, 2),
                    'message': f'距离医院{round(distance)}米，允许范围200米'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建打卡记录
        attendance = AttendanceLog.objects.create(
            user=request.user,
            punch_time=timezone.now(),
            type=data['type'],
            source='WECHAT',
            latitude=latitude,
            longitude=longitude,
            is_in_geofence=is_in_geofence,
            note=data.get('note', '')
        )
        
        return Response({
            'message': '打卡成功',
            'data': AttendanceLogSerializer(attendance).data
        })
    
    @action(detail=False, methods=['get'])
    def my_records(self, request):
        """
        获取我的打卡记录
        GET /api/attendance/my_records/?date=2024-01-15
        """
        date_str = request.query_params.get('date')
        
        if date_str:
            # 查询指定日期的打卡记录
            queryset = self.get_queryset().filter(
                user=request.user,
                punch_time__date=date_str
            )
        else:
            # 默认查询最近7天
            from datetime import timedelta
            seven_days_ago = timezone.now() - timedelta(days=7)
            queryset = self.get_queryset().filter(
                user=request.user,
                punch_time__gte=seven_days_ago
            )
        
        serializer = AttendanceLogSerializer(queryset, many=True)
        return Response(serializer.data)
