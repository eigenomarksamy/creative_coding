import sys
import pygame
from utils.randomization import generate_random_color
from shapes.pygame_line import draw_line_polar

def main() -> int:
    pygame.init()
    res = (2880, 2880)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    l = screen.get_width() / 2
    dl = 50
    for a in range(360):
        draw_line_polar(screen, pygame.Vector2(screen.get_width() / 2,
                                               screen.get_height() / 2),
                        l, a, generate_random_color(), 10)
        if a < 45:
            l -= dl
        elif a < 90:
            l += dl
        elif a < 135:
            l -= dl
        elif a < 180:
            l += dl
        elif a < 225:
            l -= dl
        elif a < 270:
            l += dl
        elif a < 315:
            l -= dl
        elif a < 365:
            l += dl
    pygame.image.save(screen, 'cc_pygame/gen/jpger_17.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
