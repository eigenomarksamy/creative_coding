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

def check_point_within_bounds(bounds: tuple[tuple[float]],
                              point: tuple[float]) -> bool:
    x_bounds = (min(bounds[0][0], bounds[0][1]), max(bounds[0][0], bounds[0][1]))
    y_bounds = (min(bounds[1][0], bounds[1][1]), max(bounds[1][0], bounds[1][1]))
    if point[0] > x_bounds[0] and point[0] < x_bounds[1] \
        and point[1] > y_bounds[0] and point[1] < y_bounds[1]:
        return True
    return False

def check_points_within_bounds(bounds: tuple[tuple[float]],
                               points: list[tuple[float]]) -> bool:
    for point in  points:
        if not check_point_within_bounds(bounds, point):
            return False
    return True

def get_opposite_points_equ_triangle(x: float, y: float, len: float,
                                     angle: float) -> Tuple[tuple[float],
                                                            tuple[float]]:
    angle_rad = math.radians(angle)
    x2 = x + len * math.cos(angle_rad)
    y2 = y + len * math.sin(angle_rad)
    angle_rad2 = angle_rad + 2 * math.pi / 3
    x3 = x + len * math.cos(angle_rad2)
    y3 = y + len * math.sin(angle_rad2)
    return (x2, y2), (x3, y3)

def get_equ_tri_vertices_from_center(x: float, y: float, len: float,
                                     angle: float) -> list[tuple[float]]:
    angle_rad = math.radians(angle)
    radius = len * math.sqrt(3) / 3
    x1 = x + radius * math.cos(angle_rad)
    y1 = y + radius * math.sin(angle_rad)
    angle_rad2 = angle_rad + 2 * math.pi / 3
    x2 = x + radius * math.cos(angle_rad2)
    y2 = y + radius * math.sin(angle_rad2)
    angle_rad3 = angle_rad + 4 * math.pi / 3
    x3 = x + radius * math.cos(angle_rad3)
    y3 = y + radius * math.sin(angle_rad3)
    return [(x1, y1), (x2, y2), (x3, y3)]
