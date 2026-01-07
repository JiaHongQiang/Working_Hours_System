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
from core.models import User
from core.serializers import UserSerializer, WechatBindSerializer


class UserViewSet(viewsets.ModelViewSet):
    """员工管理ViewSet"""
    
    queryset = User.objects.select_related('department').filter(status=1)
    serializer_class = UserSerializer
    filterset_fields = ['department', 'status']
    search_fields = ['username', 'full_name', 'phone']
    ordering = ['-id']
    
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
                user = User.objects.get(openid=openid, status=1)
                return Response({
                    'token': '生成JWT Token',  # 需要集成JWT
                    'user': UserSerializer(user).data
                })
            except User.DoesNotExist:
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
            "code": "微信code",
            "username": "工号",
            "password": "密码"
        }
        """
        serializer = WechatBindSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 验证员工账号
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if not user:
            return Response(
                {'error': '工号或密码错误'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: 获取openid并绑定
        # user.openid = openid
        # user.save()
        
        return Response({
            'message': '绑定成功',
            'user': UserSerializer(user).data
        })
