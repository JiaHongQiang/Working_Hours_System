"""
地理围栏验证服务
"""
import math
from typing import Tuple
from django.conf import settings


class GeofenceValidator:
    """地理围栏验证器 - 验证打卡位置是否在允许范围内"""
    
    @staticmethod
    def calculate_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        使用Haversine公式计算两点之间的距离（米）
        
        Args:
            lat1, lon1: 第一个点的纬度和经度
            lat2, lon2: 第二个点的纬度和经度
            
        Returns:
            距离（米）
        """
        # 地球平均半径（米）
        R = 6371000
        
        # 转换为弧度
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        # Haversine公式
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) *
             math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    @classmethod
    def is_in_geofence(
        cls,
        latitude: float,
        longitude: float
    ) -> Tuple[bool, float]:
        """
        验证坐标是否在医院围栏内
        
        Args:
            latitude: 打卡位置纬度
            longitude: 打卡位置经度
            
        Returns:
            (是否在围栏内, 距离医院的距离)
        
        Example:
            >>> validator = GeofenceValidator()
            >>> is_valid, distance = validator.is_in_geofence(39.9042, 116.4074)
            >>> print(f"在围栏内: {is_valid}, 距离: {distance:.2f}米")
        """
        hospital_lat = settings.HOSPITAL_LATITUDE
        hospital_lon = settings.HOSPITAL_LONGITUDE
        allowed_radius = settings.GEOFENCE_RADIUS
        
        distance = cls.calculate_distance(
            hospital_lat,
            hospital_lon,
            latitude,
            longitude
        )
        
        is_valid = distance <= allowed_radius
        
        return is_valid, distance
