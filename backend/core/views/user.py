"""
API视图 - 员工管理
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import requests
from django.conf import settings
from core.models import Employee
from core.serializers import (
    EmployeeSerializer, 
    EmployeeListSerializer, 
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
    WechatBindSerializer
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """员工管理ViewSet"""
    
    queryset = Employee.objects.select_related('admin_dept', 'scheduling_ward').all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['admin_dept', 'scheduling_ward', 'staff_category', 'emp_status', 'work_status']
    search_fields = ['emp_code', 'full_name', 'phone', 'username']
    ordering_fields = ['emp_code', 'full_name', 'admin_dept', 'created_at']
    ordering = ['admin_dept', 'emp_code']
    
    def get_queryset(self):
        """默认只返回在职员工，可通过参数查询全部"""
        queryset = super().get_queryset()
        # 如果没有明确指定work_status，默认只返回在职员工
        if 'work_status' not in self.request.query_params:
            queryset = queryset.filter(work_status=1)
        # 否则，如果传了work_status（包括空字符串），交由FilterBackend处理
        # 注意：如果传了空字符串，DjangoFilterBackend会自动忽略，从而实现查询全部
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmployeeUpdateSerializer
        return EmployeeSerializer
    
    def perform_create(self, serializer):
        """创建员工时设置密码"""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        重置员工密码
        POST /api/users/{id}/reset_password/
        
        Body:
        {
            "password": "新密码"
        }
        """
        employee = self.get_object()
        password = request.data.get('password')
        
        if not password or len(password) < 6:
            return Response(
                {'error': '密码长度至少6位'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        employee.set_password(password)
        employee.save(update_fields=['password'])
        
        return Response({'message': '密码重置成功'})
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """
        切换员工状态（在职/离职）
        POST /api/users/{id}/toggle_status/
        """
        employee = self.get_object()
        if employee.work_status == 1:
            employee.work_status = 0  # 离职
            message = '已设为离职'
        else:
            employee.work_status = 1  # 在职
            message = '已设为在职'
        employee.save(update_fields=['work_status'])
        
        return Response({'message': message, 'work_status': employee.work_status})
    
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

