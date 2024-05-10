import math
from typing import Tuple

def get_p1_from_polar(x1: float, y1: float, rho: float,
                      theta_deg: float) -> Tuple[float, float]:
    x2 = x1 + rho * math.cos(math.radians(theta_deg))
    y2 = y1 + rho * math.sin(math.radians(theta_deg))
    return x2, y2

def get_coordinates_top_point_iso_triangle(x1: float, y1: float,
                                           x2: float, y2: float,
                                           height: float) -> Tuple[float, float]:
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    base_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    half_base_length = base_length / 2
    top_point_distance = (height ** 2 + half_base_length ** 2) ** 0.5
    slope = (y2 - y1) / (x2 - x1) if (x2 - x1) != 0 else float('inf')
    if height > 0:
        return mid_x + top_point_distance / base_length * (y2 - y1), \
            mid_y - top_point_distance / base_length * (x2 - x1)
    return mid_x - top_point_distance / base_length * (y2 - y1), \
        mid_y + top_point_distance / base_length * (x2 - x1)
