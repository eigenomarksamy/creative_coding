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

def get_random_int(lower_bound: int, upper_bound: int) -> int:
    return random.randint(lower_bound, upper_bound)

def get_random_float(lower_bound: int, upper_bound: int) -> int:
    return random.random(lower_bound, upper_bound)

def generate_random_color(pre_set_a: bool = False,
                          a: int = 255,
                          not_this_color: list[pygame.Color] = None) -> pygame.Color:
    if pre_set_a:
        if not_this_color:
            generated_color = pygame.Color(random.randint(0, 255),
                                           random.randint(0, 255),
                                           random.randint(0, 255))
            while generated_color in not_this_color:
                generated_color = pygame.Color(random.randint(0, 255),
                                               random.randint(0, 255),
                                               random.randint(0, 255))
            return generated_color
        return pygame.Color(random.randint(0, 255), random.randint(0, 255),
                            random.randint(0, 255))
    else:
        if not_this_color:
            generated_color = pygame.Color(random.randint(0, 255),
                                           random.randint(0, 255),
                                           random.randint(0, 255), a)
            while generated_color in not_this_color:
                generated_color = pygame.Color(random.randint(0, 255),
                                               random.randint(0, 255),
                                               random.randint(0, 255), a)
            return generated_color
        return pygame.Color(random.randint(0, 255), random.randint(0, 255),
                            random.randint(0, 255), random.randint(0, 255))

def generate_random_color_append(not_this_color: list[pygame.Color] = None,
                                 pre_set_a: bool = False,
                                 a: int = 255,
                                 max_color: int = 255,
                                 min_color: int = 0) -> Tuple[pygame.Color, list[pygame.Color]]:
    if not_this_color == None:
        not_this_color = []
    if pre_set_a:
        if not_this_color:
            generated_color = pygame.Color(random.randint(min_color, max_color),
                                           random.randint(min_color, max_color),
                                           random.randint(min_color, max_color))
            while generated_color in not_this_color:
                generated_color = pygame.Color(random.randint(min_color, max_color),
                                               random.randint(min_color, max_color),
                                               random.randint(min_color, max_color))
            not_this_color.append(generated_color)
            return generated_color, not_this_color
        generated_color = pygame.Color(random.randint(min_color, max_color),
                                       random.randint(min_color, max_color),
                                       random.randint(min_color, max_color),
                                       random.randint(min_color, max_color))
        not_this_color.append(generated_color)
        return generated_color, not_this_color
    else:
        if not_this_color:
            generated_color = pygame.Color(random.randint(min_color, max_color),
                                           random.randint(min_color, max_color),
                                           random.randint(min_color, max_color), a)
            while generated_color in not_this_color:
                generated_color = pygame.Color(random.randint(min_color, max_color),
                                               random.randint(min_color, max_color),
                                               random.randint(min_color, max_color), a)
            not_this_color.append(generated_color)
            return generated_color, not_this_color
        generated_color = pygame.Color(random.randint(min_color, max_color),
                                       random.randint(min_color, max_color),
                                       random.randint(min_color, max_color),
                                       random.randint(min_color, max_color))
        not_this_color.append(generated_color)
        return generated_color, not_this_color

def get_eliminate_color_list(colors: list[pygame.Color]) -> pygame.Color:
    color = get_random_color_list(colors)
    colors.remove(color)
    return color

def get_random_angle(range: tuple = (0, 90, 5)) -> int:
    return random.randrange(range[0], range[1], range[2])

def generate_random_points(surface: pygame.SurfaceType,
                           start: pygame.Vector2 = None,
                           number: int = 0,
                           spacing: int = 0,
                           spacing_bounds: tuple[int] = None,
                           num_bounds: tuple[int] = None) -> list[pygame.Vector2]:
    if number == 0 and num_bounds:
        number = random.randint(num_bounds[0], num_bounds[1])
    if spacing == 0 and spacing_bounds:
        spacing = random.randint(spacing_bounds[0], spacing_bounds[1])
    if not start:
        start = pygame.Vector2(random.randint(0, surface.get_width()),
                               random.randint(0, surface.get_height()))
    points = [start]
    for _ in range(number):
        xy = pygame.Vector2(random.randint(start.x - spacing, start.x + spacing),
                            random.randint(start.y - spacing, start.y + spacing))
        points.append(xy)
        start = xy
    return points

def get_random_int_list(num_list: list[int]) -> int:
    return random.choice(num_list)
