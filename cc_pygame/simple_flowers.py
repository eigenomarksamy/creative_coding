import sys
import random
import pygame
from typing import Tuple
from shapes.pygame_circle import draw_circles, Circle

def draw_non_simple_flower(screen: pygame.SurfaceType, circles: list[Circle],
                           center_pos_w: int, center_pos_h: int,
                           radius: int, color1: pygame.Color, color2: pygame.Color) -> None:
    circles.append(Circle(screen, color2,
                          pygame.Vector2(center_pos_w - radius,
                                         center_pos_h - radius),
                          radius, 5))
    circles.append(Circle(screen, color2,
                          pygame.Vector2(center_pos_w + radius,
                                         center_pos_h + radius),
                          radius, 5))
    circles.append(Circle(screen, color2,
                          pygame.Vector2(center_pos_w + radius,
                                         center_pos_h - radius),
                          radius, 5))
    circles.append(Circle(screen, color2,
                          pygame.Vector2(center_pos_w - radius,
                                         center_pos_h + radius),
                          radius, 5))
    circles.append(Circle(screen, color1, pygame.Vector2(center_pos_w, center_pos_h),
                          radius))
    draw_circles(circles)

def draw_simple_flower(screen: pygame.SurfaceType, circles: list[Circle],
                       center_pos_w: int, center_pos_h: int,
                       radius: int, color: pygame.Color) -> None:
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w - radius,
                                         center_pos_h - radius),
                          radius))
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w + radius,
                                         center_pos_h + radius),
                          radius))
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w + radius,
                                         center_pos_h - radius),
                          radius))
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w - radius,
                                         center_pos_h + radius),
                          radius))
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w, center_pos_h),
                          radius))
    draw_circles(circles)

def randomize_dimensions(width_limits: tuple,
                         height_limits: tuple) -> Tuple[int, int]:
    random_width = random_height = 0
    if len(width_limits) == 2 and len(height_limits) == 2:
        random_width = random.randint(width_limits[0], width_limits[1])
        random_height = random.randint(height_limits[0], height_limits[1])
    return random_width, random_height

def randomize_colors(colors: list[pygame.Color] = [],
                     num: int = 1) -> list[pygame.Color]:
    ret_colors = []
    if len(colors) >= num:
        for _ in range(num):
            random_color = colors[random.randint(0, len(colors) - 1)]
            # if random_color not in ret_colors:
            ret_colors.append(random_color)
    else:
        for _ in range(num):
            random_color = pygame.Color(random.randint(0, 255),
                                        random.randint(0, 255),
                                        random.randint(0, 255),
                                        random.randint(0, 255))
            # if random_color not in ret_colors:
            ret_colors.append(random_color)
    return ret_colors

# def randomize2(dim_limits: dict, colors: dict)

def randomize(width_limits: tuple, height_limits: tuple,
              colors: list[pygame.Color] = []) -> Tuple[int, int, pygame.Color, pygame.Color]:
    random_width = random_height = 0
    color_1 = color_2 = None
    if len(width_limits) == 2 and len(height_limits) == 2:
        random_width = random.randint(width_limits[0], width_limits[1])
        random_height = random.randint(height_limits[0], height_limits[1])
    if len(colors) > 1:
        color_1 = colors[random.randint(0, len(colors) - 1)]
        color_2 = colors[random.randint(0, len(colors) - 1)]
    return random_width, random_height, color_1, color_2

def main() -> int:
    pygame.init()
    res = (1280, 720)
    max_iterations = 35
    iterations = 0
    radius = 50
    colors = ["white", "crimson", "teal", "cyan", "violet", "indigo",
              "orange", "red", "yellow", "green", "grey", "black"]
    circles = []
    screen = pygame.display.set_mode(res)
    clock = pygame.time.Clock()
    running = True
    screen_color = colors[random.randint(0, len(colors) - 1)]
    screen.fill(screen_color)
    colors.remove(screen_color)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if iterations < max_iterations:
            width_tuple = (radius * 1.5, screen.get_width() - radius * 1.5)
            height_tuple = (radius * 1.5, screen.get_height() - radius * 1.5)
            random_width, random_height, random_color_leaves, random_color_center = randomize(width_tuple,
                                                                  height_tuple,
                                                                  colors)
            draw_simple_flower(screen, circles, random_width,
                               random_height, radius, random_color_center)
            iterations += 1
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
