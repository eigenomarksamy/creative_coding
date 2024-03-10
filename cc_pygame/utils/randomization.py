import random
import pygame
from typing import Tuple

def get_random_dimensions(max_width: int, max_height: int,
                          min_width: int, min_height: int) -> Tuple[int, int]:
    return random.randint(min_width, max_width),\
           random.randint(min_height, max_height)

def get_random_color_list(og_list: list[pygame.Color]) -> pygame.Color:
    return og_list[random.randrange(0, len(og_list))]

def get_random_pos(pos_limits: tuple[pygame.Vector2,
                                            pygame.Vector2]) -> pygame.Vector2:
    x, y = get_random_dimensions(pos_limits[1].x, pos_limits[1].y,
                                 pos_limits[0].x, pos_limits[0].y)
    return pygame.Vector2(x, y)

def get_random_pos_on_screen(surface: pygame.SurfaceType,
                             width_bounds: tuple = (0, 0),
                             height_bounds: tuple = (0, 0)) -> Tuple[int, int]:
    max_dim_w, max_dim_h = surface.get_size()
    min_dim_w = min_dim_h = 0
    max_dim_w -= width_bounds[1]
    min_dim_w += width_bounds[0]
    max_dim_h -= height_bounds[1]
    min_dim_h += height_bounds[0]
    return get_random_dimensions(max_dim_w, max_dim_h, min_dim_w, min_dim_h)

def generate_random_color(pre_set_a: bool = False) -> pygame.Color:
    if pre_set_a:
        return pygame.Color(random.randint(0, 255), random.randint(0, 255),
                            random.randint(0, 255))
    else:
        return pygame.Color(random.randint(0, 255), random.randint(0, 255),
                            random.randint(0, 255), random.randint(0, 255))

def get_eliminate_color_list(colors: list[pygame.Color]) -> pygame.Color:
    color = get_random_color_list(colors)
    colors.remove(color)
    return color
