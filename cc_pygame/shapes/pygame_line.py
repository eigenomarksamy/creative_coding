import math
import pygame

class Line:

    def __init__(self, surface: pygame.SurfaceType,
                 p0: pygame.Vector2, p1: pygame.Vector2,
                 color: pygame.Color, width: int) -> None:
        self._surface = surface
        self._p0 = p0
        self._p1 = p1
        self._color = color
        self._width = width

    def draw(self):
        raise NotImplementedError("Subclasses must implement draw()")

    def _draw_line(self):
        pygame.draw.line(self._surface, self._color,
                         self._p0, self._p1, self._width)

class LineWithTwoPoints(Line):
    def draw(self):
        self._draw_line()

class LineWithOnePointAndLengthAngle(Line):

    def __init__(self, surface: pygame.SurfaceType,
                 p0: pygame.Vector2, length: float,
                 angle: float, color: pygame.Color,
                 width: int) -> None:
        x2 = p0.x + length * math.cos(math.radians(angle))
        y2 = p0.y + length * math.sin(math.radians(angle))
        super().__init__(surface, p0, pygame.Vector2(x2, y2), color, width)

    def draw(self):
        self._draw_line()

def draw_line_cartesian(surface: pygame.SurfaceType,
                        p0: pygame.Vector2, p1: pygame.Vector2,
                        color: pygame.Color, width: int) -> None:
    LineWithTwoPoints(surface, p0, p1, color, width).draw()

def draw_line_polar(surface: pygame.SurfaceType,
                    p0: pygame.Vector2, length: float,
                    angle: float, color: pygame.Color,
                    width: int) -> None:
    LineWithOnePointAndLengthAngle(surface, p0, length, angle, color, width).draw()
