"""
核心应用URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    DepartmentViewSet,
    UserViewSet,
    ShiftDefinitionViewSet,
    RosterViewSet,
    AttendanceLogViewSet,
    OvertimeRecordViewSet,
)
from core.views.system_config import SystemConfigViewSet

router = DefaultRouter()
router.register('departments', DepartmentViewSet, basename='department')
router.register('users', UserViewSet, basename='user')
router.register('shifts', ShiftDefinitionViewSet, basename='shift')
router.register('rosters', RosterViewSet, basename='roster')
router.register('attendance', AttendanceLogViewSet, basename='attendance')
router.register('overtime', OvertimeRecordViewSet, basename='overtime')
router.register('system', SystemConfigViewSet, basename='system')

urlpatterns = [
    path('', include(router.urls)),
]
