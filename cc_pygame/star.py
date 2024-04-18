import pygame
from shapes.pygame_line import draw_line_polar

def draw_star_lines(surface: pygame.SurfaceType, color: pygame.Color,
                    pos: pygame.Vector2, length: float, width: int) -> None:
    for angle in range(0, 360, 45):
        draw_line_polar(surface, pos, length / 2, angle, color, width)
