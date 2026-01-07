"""
API视图 - 科室管理
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.models import Department
from core.serializers import (
    DepartmentSerializer, 
    DepartmentTreeSerializer,
    DepartmentSimpleSerializer,
    WardListSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """科室管理ViewSet"""
    
    queryset = Department.objects.select_related('parent', 'manager').filter(is_active=True)
    serializer_class = DepartmentSerializer
    filterset_fields = ['parent', 'dept_type', 'is_active']
    search_fields = ['dept_name', 'dept_code']
    ordering = ['sort_order', 'id']
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        获取科室树形结构
        GET /api/departments/tree/
        """
        # 只获取顶级科室（没有父科室的）
        root_departments = Department.objects.filter(parent__isnull=True, is_active=True)
        serializer = DepartmentTreeSerializer(root_departments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def wards(self, request):
        """
        获取所有病区列表（排班模块用）
        GET /api/departments/wards/
        """
        wards = Department.objects.filter(
            dept_type=Department.DeptType.WARD,
            is_active=True
        ).order_by('sort_order', 'id')
        serializer = WardListSerializer(wards, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def simple_list(self, request):
        """
        获取科室简单列表（下拉选择用）
        GET /api/departments/simple_list/
        """
        dept_type = request.query_params.get('dept_type')
        queryset = Department.objects.filter(is_active=True)
        if dept_type:
            queryset = queryset.filter(dept_type=dept_type)
        serializer = DepartmentSimpleSerializer(queryset.order_by('sort_order'), many=True)
        return Response(serializer.data)
