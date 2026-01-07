"""
API视图 - 部门管理
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Department
from core.serializers import DepartmentSerializer, DepartmentTreeSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """部门管理ViewSet"""
    
    queryset = Department.objects.select_related('parent', 'manager').all()
    serializer_class = DepartmentSerializer
    filterset_fields = ['parent']
    search_fields = ['name']
    ordering = ['id']
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        获取部门树形结构
        GET /api/departments/tree/
        """
        # 只获取顶级部门（没有父部门的）
        root_departments = Department.objects.filter(parent__isnull=True)
        serializer = DepartmentTreeSerializer(root_departments, many=True)
        return Response(serializer.data)
