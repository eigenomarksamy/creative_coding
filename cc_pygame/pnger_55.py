import sys
import pygame
from shapes.pygame_shape import draw_object
from utils.randomization import (generate_random_color, generate_random_points,
                                 get_random_int)

def main() -> int:
    pygame.init()
    res = (2160, 1080)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    used_colors = [screen_color]
    for _ in range(get_random_int(20, 200)):
        color = generate_random_color(not_this_color=used_colors)
        used_colors.append(color)
        points = generate_random_points(screen, num_bounds=(20, 200),
                                        spacing_bounds=(20, 600))
        draw_object(screen, points, color)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_55.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
