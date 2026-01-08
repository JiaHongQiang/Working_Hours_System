"""
系统配置相关序列化器和视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.models import SystemConfig


class SystemConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """
    系统配置ViewSet（只读）
    
    获取公开配置：GET /api/system/config/public/
    """
    queryset = SystemConfig.objects.filter(is_active=True)
    permission_classes = [AllowAny]  # 允许匿名访问
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public(self, request):
        """
        获取公开的系统配置
        返回前端需要的配置信息
        """
        try:
            configs = SystemConfig.objects.filter(is_active=True, group='public')
            config_dict = {item.config_key: item.config_value for item in configs}
            
            # 如果没有配置，返回默认值
            if 'system_name' not in config_dict:
                config_dict['system_name'] = '考勤系统'
           
            if 'system_name_en' not in config_dict:
                config_dict['system_name_en'] = 'Attendance System'
                
            return Response(config_dict)
        except Exception as e:
            return Response({
                'system_name': '考勤系统',
                'system_name_en': 'Attendance System'
            })
