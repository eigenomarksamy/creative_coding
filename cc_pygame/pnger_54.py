import sys
import pygame
from utils.randomization import (get_random_int, get_random_pos_on_screen,
                                 generate_random_color, get_random_angle,
                                 generate_random_points)
from shapes.pygame_rectangle import draw_quick_rect
from shapes.pygame_circle import draw_circle
from shapes.pygame_line import draw_line_polar
from shapes.pygame_triangle import draw_triangle
from shapes.pygame_shape import draw_object

def draw_random_object(surface: pygame.SurfaceType,
                       excl_colors: list[pygame.Color]=[],
                       max_num_vertex: int=4) -> pygame.Color:
    x, y = get_random_pos_on_screen(surface)
    point0 = pygame.Vector2(x, y)
    color = generate_random_color(not_this_color=excl_colors)
    num_vertex = get_random_int(1, max_num_vertex)
    if num_vertex == 1:
        draw_circle(surface, color, point0, get_random_int(10, 100))
    elif num_vertex == 2:
        draw_line_polar(surface, point0, get_random_int(10, 100),
                        get_random_angle((0, 350, 1)), color,
                        get_random_int(1, 10))
    elif num_vertex == 3:
        x1, y1 = get_random_pos_on_screen(surface)
        point1 = pygame.Vector2(x1, y1)
        x2, y2 = get_random_pos_on_screen(surface)
        point2 = pygame.Vector2(x2, y2)
        draw_triangle(surface, color, [point0, point1, point2])
    elif num_vertex == 4:
        draw_quick_rect(surface, color, point0, get_random_int(10, 100),
                        get_random_int(10, 100))
    else:
        points = generate_random_points(surface, num_bounds=(20, 200),
                                        spacing_bounds=(20, 600),
                                        start=point0)
        draw_object(surface, points, color)
    return color

def main() -> int:
    pygame.init()
    res = (2160, 1080)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    used_colors = [screen_color]
    for _ in range(get_random_int(20, 200)):
        used_colors.append(draw_random_object(screen, used_colors))
    pygame.image.save(screen, 'cc_pygame/gen/jpger_54.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
