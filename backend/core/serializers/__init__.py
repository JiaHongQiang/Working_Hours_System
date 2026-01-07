"""
序列化器导入
"""
from .department import DepartmentSerializer, DepartmentTreeSerializer
from .user import UserSerializer, UserSimpleSerializer, WechatBindSerializer
from .roster import (
    ShiftDefinitionSerializer,
    RosterSerializer,
    RosterCreateSerializer,
    RosterCalendarSerializer,
)
from .attendance import AttendanceLogSerializer, PunchRequestSerializer
from .overtime import (
    OvertimeRecordSerializer,
    OvertimeApplySerializer,
    OvertimeApprovalSerializer,
    OvertimeStatisticsSerializer,
)

__all__ = [
    'DepartmentSerializer',
    'DepartmentTreeSerializer',
    'UserSerializer',
    'UserSimpleSerializer',
    'WechatBindSerializer',
    'ShiftDefinitionSerializer',
    'RosterSerializer',
    'RosterCreateSerializer',
    'RosterCalendarSerializer',
    'AttendanceLogSerializer',
    'PunchRequestSerializer',
    'OvertimeRecordSerializer',
    'OvertimeApplySerializer',
    'OvertimeApprovalSerializer',
    'OvertimeStatisticsSerializer',
]
