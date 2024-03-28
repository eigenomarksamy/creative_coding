import sys
import pygame
from utils.randomization import get_random_int
from utils.randomization import generate_random_color
from shapes.pygame_line import draw_line_polar

def main() -> int:
    pygame.init()
    res = (2880, 2880)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    for a in range(360):
        draw_line_polar(screen, pygame.Vector2(screen.get_width() / 2,
                                               screen.get_height() / 2),
                        get_random_int(1, screen.get_width() / 2), a, generate_random_color(), 5)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_16.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
