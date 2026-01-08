"""
核心模型导入
"""
from .department import Department
from .user import Employee, User  # Employee是新模型，User是兼容别名
from .shift import ShiftDefinition
from .roster import Roster
from .attendance import AttendanceLog
from .overtime import OvertimeRecord
from .system_config import SystemConfig

__all__ = [
    'Department',
    'Employee',
    'User',  # 兼容别名
    'ShiftDefinition',
    'Roster',
    'AttendanceLog',
    'OvertimeRecord',
    'SystemConfig',
]
