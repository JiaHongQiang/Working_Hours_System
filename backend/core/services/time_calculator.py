"""
时间计算引擎 - 处理跨夜班等复杂时间场景
"""
from datetime import datetime, timedelta, time
from typing import Tuple


class TimeCalculator:
    """时间计算引擎 - 处理跨夜班等复杂场景"""
    
    @staticmethod
    def calculate_scheduled_time(
        roster_date,
        start_time: time,
        end_time: time,
        is_cross_day: bool
    ) -> Tuple[datetime, datetime]:
        """
        计算排班的计划上下班时间
        
        Args:
            roster_date: 排班逻辑日期 (date对象)
            start_time: 班次开始时间 (time对象)
            end_time: 班次结束时间 (time对象)
            is_cross_day: 是否跨天
            
        Returns:
            (scheduled_start, scheduled_end) 时间元组
        
        Example:
            >>> from datetime import date, time
            >>> calculator = TimeCalculator()
            >>> # 大夜班: 2024-01-15 20:00 ~ 2024-01-16 08:00
            >>> start, end = calculator.calculate_scheduled_time(
            ...     roster_date=date(2024, 1, 15),
            ...     start_time=time(20, 0),
            ...     end_time=time(8, 0),
            ...     is_cross_day=True
            ... )
            >>> print(start)  # 2024-01-15 20:00:00
            >>> print(end)    # 2024-01-16 08:00:00
        """
        # 计划上班时间
        scheduled_start = datetime.combine(roster_date, start_time)
        
        # 计划下班时间 - 跨夜班判定
        if is_cross_day or end_time < start_time:
            # 跨天：下班时间在次日
            scheduled_end = datetime.combine(
                roster_date + timedelta(days=1),
                end_time
            )
        else:
            # 不跨天：下班时间在当天
            scheduled_end = datetime.combine(roster_date, end_time)
            
        return scheduled_start, scheduled_end
    
    @staticmethod
    def calculate_overtime_hours(
        punch_out: datetime,
        scheduled_end: datetime
    ) -> float:
        """
        计算加班时长（小时）
        
        Args:
            punch_out: 实际下班打卡时间
            scheduled_end: 计划下班时间
            
        Returns:
            加班小时数（保留2位小数）
        
        Example:
            >>> from datetime import datetime
            >>> # 计划18:00下班，实际21:30下班
            >>> scheduled = datetime(2024, 1, 15, 18, 0)
            >>> actual = datetime(2024, 1, 15, 21, 30)
            >>> hours = TimeCalculator.calculate_overtime_hours(actual, scheduled)
            >>> print(hours)  # 3.5
        """
        if punch_out <= scheduled_end:
            return 0.0
            
        overtime_seconds = (punch_out - scheduled_end).total_seconds()
        overtime_hours = round(overtime_seconds / 3600, 2)
        
        return max(0.0, overtime_hours)
    
    @staticmethod
    def calculate_work_duration(
        start: datetime,
        end: datetime,
        break_minutes: int = 0
    ) -> float:
        """
        计算工作时长（小时）
        
        Args:
            start: 开始时间
            end: 结束时间
            break_minutes: 扣除的休息时间（分钟）
            
        Returns:
            工作小时数（保留2位小数）
        """
        if end <= start:
            return 0.0
        
        duration_seconds = (end - start).total_seconds()
        duration_hours = (duration_seconds / 3600) - (break_minutes / 60)
        
        return max(0.0, round(duration_hours, 2))
