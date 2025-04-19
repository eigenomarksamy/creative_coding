import pygame
from shapes.pygame_line import draw_line_polar

class Arrow:

    def __init__(self, head_pos: pygame.Vector2, color: pygame.Color,
                 angle: float, tail_length: float, head_angle: float,
                 head_length: float, head_width: int,
                 tail_width: int, hollow_width: int = 0) -> None:
        self.pos = head_pos
        self.color = color
        self.angle = angle
        self.tail_length = tail_length
        self.head_angle = head_angle
        self.head_length = head_length
        self.head_width = head_width
        self.tail_width = tail_width
        self.hollow_width = hollow_width

    def _draw_head(self, surface: pygame.SurfaceType) -> None:
        draw_line_polar(surface, self.pos, self.head_length, self.head_angle,
                        self.color, self.head_width)
        draw_line_polar(surface, self.pos, self.head_length,
                        360 - self.head_angle, self.color, self.head_width)

    def _draw_tail(self, surface: pygame.SurfaceType) -> None:
        draw_line_polar(surface, self.pos, self.tail_length, self.angle,
                        self.color, self.tail_width)

    def draw(self, surface: pygame.SurfaceType) -> None:
        self._draw_tail(surface)
        self._draw_head(surface)

def draw_quick_arrow(surface: pygame.SurfaceType, head_pos: pygame.Vector2,
                     color: pygame.Color, angle: float, tail_length: float,
                     head_angle: float, head_length: float, head_width: int,
                     tail_width: int, hollow_width: int = 0) -> None:
    Arrow(head_pos, color, angle, tail_length, head_angle, head_length,
          head_width, tail_width, hollow_width).draw(surface)


class SophisticatedArrow:
    pass
