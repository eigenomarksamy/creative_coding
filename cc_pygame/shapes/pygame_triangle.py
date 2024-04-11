import math
import pygame

class Triangle:
    def __init__(self, surface: pygame.Surface, color: pygame.Color,
                 points: list[pygame.Vector2], width: int = 0) -> None:
        self.surface = surface
        self.color = color
        self.points = points
        self.width = width

    def draw(self) -> None:
        pygame.draw.polygon(self.surface, self.color, self.points, self.width)

def draw_triangle(surface: pygame.SurfaceType, color: pygame.Color,
                  points: list[pygame.Vector2], width: int = 0) -> None:
    Triangle(surface, color, points, width).draw()

def draw_equilateral_from_center(surface: pygame.SurfaceType,
                                 color: pygame.Color, center: pygame.Vector2,
                                 base: int, height: int, width: int = 0,
                                 angle: float = 0) -> None:
    points = [
        pygame.Vector2(center.x, center.y - height / 2),
        pygame.Vector2(center.x + base / 2, center.y + height / 2),
        pygame.Vector2(center.x - base / 2, center.y + height / 2)
    ]
    rotated_points = []
    angle = math.radians(angle)
    for point in points:
        rotated_x = math.cos(angle) * (point.x - center.x) - math.sin(angle) * (point.y - center.y) + center.x
        rotated_y = math.sin(angle) * (point.x - center.x) + math.cos(angle) * (point.y - center.y) + center.y
        rotated_points.append(pygame.Vector2(rotated_x, rotated_y))
    draw_triangle(surface, color, rotated_points, width)
