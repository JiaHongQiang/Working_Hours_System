"""
视图导入
"""
from .department import DepartmentViewSet
from .user import UserViewSet
from .roster import ShiftDefinitionViewSet, RosterViewSet
from .attendance import AttendanceLogViewSet
from .overtime import OvertimeRecordViewSet

__all__ = [
    'DepartmentViewSet',
    'UserViewSet',
    'ShiftDefinitionViewSet',
    'RosterViewSet',
    'AttendanceLogViewSet',
    'OvertimeRecordViewSet',
]
