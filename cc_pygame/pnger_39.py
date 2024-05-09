import sys
import pygame
from utils.randomization import (get_random_pos, generate_random_color,
                                 get_random_int)
from shapes.pygame_shape import draw_object

def do_generation(surface: pygame.SurfaceType, color: pygame.Color) -> None:
    pos_limits = (pygame.Vector2(surface.get_width() / 2, surface.get_height() / 2),
                  pygame.Vector2(surface.get_width(), surface.get_height()))
    num_points = get_random_int(3, 6)
    pos_1 = []
    pos_2 = []
    pos_3 = []
    pos_4 = []
    for _ in range(num_points):
        p = get_random_pos(pos_limits)
        pos_1.append(p)
        pos_2.append(pygame.Vector2(surface.get_width() - p.x, surface.get_height() - p.y))
        pos_3.append(pygame.Vector2(surface.get_width() - p.x, p.y))
        pos_4.append(pygame.Vector2(p.x, surface.get_height() - p.y))
    poses = [pos_1, pos_2, pos_3, pos_4]
    for i in poses:
        draw_object(surface, i, color)

def main() -> int:
    pygame.init()
    res = (2080, 2080)
    screen = pygame.display.set_mode(res)
    screen_color = generate_random_color()
    screen.fill(screen_color)
    used_colors = [screen_color]
    for _ in range(get_random_int(5, 21)):
        color = generate_random_color(not_this_color=used_colors)
        used_colors.append(color)
        do_generation(screen, color)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_39.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
