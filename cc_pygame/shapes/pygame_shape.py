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