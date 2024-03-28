import sys
import pygame
from utils.randomization import get_random_pos_on_screen
from utils.randomization import generate_random_color
from utils.randomization import random
from utils.randomization import get_random_angle
from shapes.pygame_line import draw_line_polar

def main() -> int:
    pygame.init()
    res = (2880, 2880)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    pos = []
    for _ in range(1000):
        x, y = get_random_pos_on_screen(screen)
        pos.append(pygame.Vector2(x, y))
    for p in pos:
        draw_line_polar(screen, p, random.randint(1, screen.get_width()), get_random_angle((0, 360, 10)), generate_random_color(), 5)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_15.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
