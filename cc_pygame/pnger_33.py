import sys
import random
import pygame
from utils.randomization import generate_random_color

def draw_object(surface: pygame.SurfaceType, points: list[pygame.Vector2],
                color: pygame.Color,
                excl_area: list[list[pygame.Vector2]] = None) -> None:
    pygame.draw.polygon(surface, color, points)

def generate_random_points(surface: pygame.SurfaceType,
                           start: pygame.Vector2 = None,
                           number: int = 3,
                           spacing: int = 10) -> list[pygame.Vector2]:
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

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    used_colors = [screen_color]
    for _ in range(random.randint(10, 100)):
        color = generate_random_color(not_this_color=used_colors)
        used_colors.append(color)
        points = generate_random_points(screen, number=random.randint(10, 100), spacing=random.randint(10, 800))
        draw_object(screen, points, color)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_33.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
