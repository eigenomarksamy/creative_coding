import sys
import random
import pygame
from typing import Tuple
from shapes.pygame_circle import draw_circles, Circle

def draw_simple_flower(screen: pygame.SurfaceType, circles: list[Circle],
                       center_pos_w: int, center_pos_h: int,
                       radius: int, color: pygame.Color) -> None:
    circles.append(Circle(screen, color, pygame.Vector2(center_pos_w, center_pos_h),
                          radius))
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
    draw_circles(circles)

def randomize(width_limits: tuple, height_limits: tuple,
              colors: list[pygame.Color] = []) -> Tuple[int, int, pygame.Color]:
    random_width = random_height = 0
    color = None
    if len(width_limits) == 2 and len(height_limits) == 2:
        random_width = random.randint(width_limits[0], width_limits[1])
        random_height = random.randint(height_limits[0], height_limits[1])
    if len(colors) > 0:
        color = colors[random.randint(0, len(colors) - 1)]
    return random_width, random_height, color

def main():
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
            random_width, random_height, random_color = randomize(width_tuple,
                                                                  height_tuple,
                                                                  colors)
            draw_simple_flower(screen, circles, random_width,
                               random_height, radius, random_color)
            iterations += 1
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    sys.exit(main())
