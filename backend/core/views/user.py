"""
API视图 - 员工管理
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
import requests
from django.conf import settings
from core.models import Employee
from core.serializers import EmployeeSerializer, EmployeeListSerializer, WechatBindSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    """员工管理ViewSet"""
    
    queryset = Employee.objects.select_related('admin_dept', 'scheduling_ward').filter(work_status=1)
    serializer_class = EmployeeSerializer
    filterset_fields = ['admin_dept', 'scheduling_ward', 'staff_category', 'emp_status', 'work_status']
    search_fields = ['emp_code', 'full_name', 'phone', 'username']
    ordering = ['admin_dept', 'emp_code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def wechat_login(self, request):
        """
        微信小程序登录
        POST /api/users/wechat_login/
        
        Body:
        {
            "code": "微信登录code"
        }
        """
        code = request.data.get('code')
        if not code:
            return Response(
                {'error': '缺少code参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 调用微信API获取openid
        url = 'https://api.weixin.qq.com/sns/jscode2session'
        params = {
            'appid': settings.WECHAT_APP_ID,
            'secret': settings.WECHAT_APP_SECRET,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if 'openid' not in data:
                return Response(
                    {'error': '微信登录失败', 'detail': data.get('errmsg')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            openid = data['openid']
            
            # 查找已绑定的用户
            try:
                user = Employee.objects.get(openid=openid, work_status=1)
                return Response({
                    'token': '生成JWT Token',  # 需要集成JWT
                    'user': EmployeeSerializer(user).data
                })
            except Employee.DoesNotExist:
                return Response({
                    'need_bind': True,
                    'openid': openid
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': '网络请求失败', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def wechat_bind(self, request):
        """
        绑定微信账号
        POST /api/users/wechat_bind/
        
        Body:
        {
            "openid": "微信openid",
            "emp_code": "工号",
            "phone": "手机号(可选)"
        }
        """
        serializer = WechatBindSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        openid = serializer.validated_data['openid']
        emp_code = serializer.validated_data['emp_code']
        
        try:
            employee = Employee.objects.get(emp_code=emp_code, work_status=1)
            employee.openid = openid
            employee.save(update_fields=['openid'])
            
            return Response({
                'message': '绑定成功',
                'user': EmployeeSerializer(employee).data
            })
        except Employee.DoesNotExist:
            return Response(
                {'error': '工号不存在或已离职'},
                status=status.HTTP_400_BAD_REQUEST
            )


# 兼容旧的URL配置
UserViewSet = EmployeeViewSet
