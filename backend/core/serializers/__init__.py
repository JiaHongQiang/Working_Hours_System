"""
序列化器导入
"""
from .department import (
    DepartmentSerializer, 
    DepartmentTreeSerializer,
    DepartmentSimpleSerializer,
    WardListSerializer,
)
from .user import (
    EmployeeSerializer,
    EmployeeListSerializer,
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
    EmployeeSimpleSerializer,
    WechatBindSerializer,
    SchedulingEmployeeSerializer,
)
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

# 兼容别名
UserSerializer = EmployeeSerializer
UserSimpleSerializer = EmployeeSimpleSerializer

__all__ = [
    # Department
    'DepartmentSerializer',
    'DepartmentTreeSerializer',
    'DepartmentSimpleSerializer',
    'WardListSerializer',
    # Employee
    'EmployeeSerializer',
    'EmployeeListSerializer',
    'EmployeeCreateSerializer',
    'EmployeeUpdateSerializer',
    'EmployeeSimpleSerializer',
    'WechatBindSerializer',
    'SchedulingEmployeeSerializer',
    # 兼容别名
    'UserSerializer',
    'UserSimpleSerializer',
    # Shift & Roster
    'ShiftDefinitionSerializer',
    'RosterSerializer',
    'RosterCreateSerializer',
    'RosterCalendarSerializer',
    # Attendance
    'AttendanceLogSerializer',
    'PunchRequestSerializer',
    # Overtime
    'OvertimeRecordSerializer',
    'OvertimeApplySerializer',
    'OvertimeApprovalSerializer',
    'OvertimeStatisticsSerializer',
]
