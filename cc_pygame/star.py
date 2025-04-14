import pygame
from utils.geometric import get_p1_from_polar
from shapes.pygame_circle import draw_circle
from shapes.pygame_rectangle import draw_quick_square
from shapes.pygame_line import draw_line_polar, draw_line_cartesian

def draw_star_lines(surface: pygame.SurfaceType, color: pygame.Color,
                    pos: pygame.Vector2, length: float, width: int) -> None:
    for angle in range(0, 360, 45):
        draw_line_polar(surface, pos, length / 2, angle, color, width)

def draw_sophisticated_star(surface: pygame.SurfaceType, color1: pygame.Color,
                            color2: pygame.Color, pos: pygame.Vector2,
                            length: float, line_width: int) -> None:
    diag_len = length * 2 ** 0.5
    draw_circle(surface, color1, pos, diag_len / 2)
    draw_quick_square(surface, color2, pos, length, 45)
    points_stack = []
    for ang in range(0, 361, 45):
        if ang % 90 == 0:
            draw_line_polar(surface, pos, diag_len / 2, ang, color1, line_width)
            p1x, p1y = get_p1_from_polar(pos.x, pos.y, diag_len / 2, ang)
            points_stack.append(pygame.Vector2(p1x, p1y))
        else:
            draw_line_polar(surface, pos, 0.35 * diag_len / 2, ang, color1, line_width)
            p1x, p1y = get_p1_from_polar(pos.x, pos.y, 0.35 * diag_len / 2, ang)
            points_stack.append(pygame.Vector2(p1x, p1y))
        if len(points_stack) > 1:
            draw_line_cartesian(surface, points_stack[0], points_stack[1], color1, line_width)
            points_stack.pop(0)
