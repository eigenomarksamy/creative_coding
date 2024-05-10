import pygame

class Shape:
    def __init__(self, surface: pygame.SurfaceType,
                 color: pygame.Color, pos: pygame.Vector2,
                 width: int = 0, angle: float = 0) -> None:
        self._surface = surface
        self._color = color
        self._center_pos = pos
        self._width = width
        self._angle = angle

    def rotate(self) -> pygame.SurfaceType:
        return pygame.transform.rotate(self._surface, self._angle)

def draw_object(surface: pygame.SurfaceType, points: list[pygame.Vector2],
                color: pygame.Color, width: int = 0) -> None:
    pygame.draw.polygon(surface, color, points, width)

def mirror_on_vertical(surface: pygame.SurfaceType,
                       points: list[pygame.Vector2]) -> list[pygame.Vector2]:
    ret_points = []
    for p in points:
        ret_points.append(pygame.Vector2(surface.get_width() - p.x, p.y))
    return ret_points

def mirror_on_horizontal(surface: pygame.SurfaceType,
                         points: list[pygame.Vector2]) -> list[pygame.Vector2]:
    ret_points = []
    for p in points:
        ret_points.append(pygame.Vector2(p.x, surface.get_height() - p.y))
    return ret_points

def mirror_on_diagonal(surface: pygame.SurfaceType,
                       points: list[pygame.Vector2]) -> list[pygame.Vector2]:
    ret_points = []
    for p in points:
        ret_points.append(pygame.Vector2(surface.get_width() - p.x,
                                         surface.get_height() - p.y))
    return ret_points

def mirror_4_quads(surface: pygame.SurfaceType,
                   points: list[pygame.Vector2]) -> list[list[pygame.Vector2]]:
    ret_points = [points]
    ret_points.append(mirror_on_vertical(surface, points))
    ret_points.append(mirror_on_horizontal(surface, points))
    ret_points.append(mirror_on_diagonal(surface, points))
    return ret_points
