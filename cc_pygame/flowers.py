import sys
import pygame
from shapes.pygame_circle import Circle, draw_circles

def draw_simple_flower(screen: pygame.SurfaceType, circles: list[Circle],
                       center_pos_w: int, center_pos_h: int,
                       radius: int, color: pygame.Color,
                       width_center: int = 0, width_corners: int = 0) -> None:
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w - radius,
                                         center_pos_h - radius),
                          radius, width_corners))
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w + radius,
                                         center_pos_h + radius),
                          radius, width_corners))
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w + radius,
                                         center_pos_h - radius),
                          radius, width_corners))
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w - radius,
                                         center_pos_h + radius),
                          radius, width_corners))
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w, center_pos_h),
                          radius, width_center))
    draw_circles(circles)

def draw_nested_flowers(screen: pygame.SurfaceType, pos: pygame.Vector2,
                        max_radius: int, min_radius: int, decrement: int,
                        color1: pygame.Color, color2: pygame.Color,
                        width_center: int = 0, width_corners: int = 0) -> None:
    circles = []
    color = color2
    for r in range(max_radius, min_radius - decrement, -decrement):
        if color == color2:
            color = color1
        else:
            color = color2
        draw_simple_flower(screen, circles, pos.x, pos.y, r,
                           color, width_center, width_corners)
