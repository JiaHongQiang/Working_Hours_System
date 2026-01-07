"""
加班计算引擎 - 实现0-4-8阶梯制和倍率判定
"""
from datetime import date
import holidays


class OvertimeCalculator:
    """加班计算引擎 - 实现0-4-8阶梯制和倍率判定"""
    
    def __init__(self):
        """初始化中国法定节假日库"""
        self.cn_holidays = holidays.CN()
    
    def apply_step_function(self, raw_hours: float) -> int:
        """
        0-4-8阶梯制工时规整
        
        这是医院特有的规则，用于减少碎片化加班成本：
        - 加班不足4小时：计为0小时（不支付加班费）
        - 加班4-8小时：计为4小时
        - 加班8小时及以上：计为8小时
        
        Args:
            raw_hours: 原始加班小时数
            
        Returns:
            规整后的小时数 (0, 4, 或 8)
        
        Examples:
            >>> calc = OvertimeCalculator()
            >>> calc.apply_step_function(3.9)
            0
            >>> calc.apply_step_function(4.0)
            4
            >>> calc.apply_step_function(7.8)
            4
            >>> calc.apply_step_function(8.5)
            8
            >>> calc.apply_step_function(12.0)
            8
        """
        if raw_hours < 4.0:
            return 0
        elif 4.0 <= raw_hours < 8.0:
            return 4
        else:
            # 即使超过8小时，也只记8小时
            return 8
    
    def calculate_multiplier(
        self,
        work_date: date,
        has_roster: bool
    ) -> float:
        """
        计算薪资倍率
        
        判定优先级：
        1. 法定节假日 → 3.0倍（最高优先级）
        2. 休息日（周末）且无排班 → 2.0倍
        3. 其他情况（正常排班日超时） → 1.5倍
        
        Args:
            work_date: 工作日期
            has_roster: 当天是否有排班
            
        Returns:
            倍率 (1.5, 2.0, 或 3.0)
        
        Examples:
            >>> from datetime import date
            >>> calc = OvertimeCalculator()
            >>> # 2024年国庆节
            >>> calc.calculate_multiplier(date(2024, 10, 1), True)
            3.0
            >>> # 普通周六有排班
            >>> calc.calculate_multiplier(date(2024, 10, 5), True)
            1.5
            >>> # 普通周六无排班（临时召回）
            >>> calc.calculate_multiplier(date(2024, 10, 5), False)
            2.0
            >>> # 普通工作日
            >>> calc.calculate_multiplier(date(2024, 10, 8), True)
            1.5
        """
        # 1. 法定节假日判定 - 最高优先级
        if work_date in self.cn_holidays:
            return 3.0
        
        # 2. 休息日（周末）无排班判定
        # weekday(): 0-4为周一至周五，5-6为周六日
        is_weekend = work_date.weekday() >= 5
        if is_weekend and not has_roster:
            return 2.0
        
        # 3. 其他情况：正常排班日超时
        # 注意：周末如果有排班，按1.5倍计算
        return 1.5
    
    def calculate_pay(
        self,
        approved_hours: int,
        base_hourly_rate: float,
        multiplier: float
    ) -> float:
        """
        计算加班费
        
        Args:
            approved_hours: 规整后的加班小时数
            base_hourly_rate: 基础时薪
            multiplier: 薪资倍率
            
        Returns:
            加班费金额（保留2位小数）
        
        Example:
            >>> calc = OvertimeCalculator()
            >>> # 加班8小时，时薪50元，1.5倍
            >>> calc.calculate_pay(8, 50.0, 1.5)
            600.0
        """
        return round(approved_hours * base_hourly_rate * multiplier, 2)
    
    def calculate_full_overtime(
        self,
        raw_hours: float,
        work_date: date,
        has_roster: bool,
        base_hourly_rate: float
    ) -> dict:
        """
        完整的加班计算流程
        
        Args:
            raw_hours: 原始加班时长
            work_date: 工作日期
            has_roster: 是否有排班
            base_hourly_rate: 基础时薪
            
        Returns:
            dict包含：
                - approved_hours: 规整后时长
                - multiplier: 倍率
                - pay_amount: 加班费
                - is_holiday: 是否节假日
        """
        approved_hours = self.apply_step_function(raw_hours)
        multiplier = self.calculate_multiplier(work_date, has_roster)
        pay_amount = self.calculate_pay(approved_hours, base_hourly_rate, multiplier)
        
        return {
            'raw_hours': raw_hours,
            'approved_hours': approved_hours,
            'multiplier': multiplier,
            'pay_amount': pay_amount,
            'is_holiday': work_date in self.cn_holidays,
        }
