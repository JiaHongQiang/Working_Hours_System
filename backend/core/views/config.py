"""
API视图 - 系统配置管理
"""
import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from core.models import SystemConfig


class SystemConfigViewSet(viewsets.ViewSet):
    """系统配置ViewSet"""
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def punch_config(self, request):
        """
        获取打卡配置（公开接口，小程序调用）
        GET /api/config/punch_config/
        """
        config = SystemConfig.get_punch_config()
        return Response(config)
    
    @action(detail=False, methods=['post'])
    def save_punch_config(self, request):
        """
        保存打卡配置（需要管理员权限）
        POST /api/config/save_punch_config/
        
        Body:
        {
            "hospital_name": "XX医院",
            "hospital_latitude": 39.9042,
            "hospital_longitude": 116.4074,
            "geofence_radius": 200
        }
        """
        data = request.data
        
        # 验证必填字段
        required_fields = ['hospital_latitude', 'hospital_longitude', 'geofence_radius']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'缺少必填字段: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 验证数值范围
        try:
            lat = float(data['hospital_latitude'])
            lng = float(data['hospital_longitude'])
            radius = int(data['geofence_radius'])
            
            if not (-90 <= lat <= 90):
                return Response({'error': '纬度范围应在 -90 到 90 之间'}, status=status.HTTP_400_BAD_REQUEST)
            if not (-180 <= lng <= 180):
                return Response({'error': '经度范围应在 -180 到 180 之间'}, status=status.HTTP_400_BAD_REQUEST)
            if radius < 10 or radius > 10000:
                return Response({'error': '打卡范围应在 10 到 10000 米之间'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({'error': '数值格式错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        config_data = {
            'hospital_name': data.get('hospital_name', '医院'),
            'hospital_latitude': lat,
            'hospital_longitude': lng,
            'geofence_radius': radius
        }
        
        SystemConfig.set_value(
            key='punch_config',
            value=json.dumps(config_data),
            description='打卡地理围栏配置'
        )
        
        return Response({
            'message': '配置保存成功',
            'data': config_data
        })
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """
        获取所有配置（管理员）
        GET /api/config/all/
        """
        configs = SystemConfig.objects.all()
        data = {}
        for config in configs:
            try:
                data[config.key] = json.loads(config.value)
            except json.JSONDecodeError:
                data[config.key] = config.value
        return Response(data)
