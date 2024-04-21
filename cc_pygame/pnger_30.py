import sys
import pygame
from utils.geometric import get_p1_from_polar
from shapes.pygame_line import draw_line_polar

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    offset = 10
    p0 = pygame.Vector2(0, 0)
    line_length = screen.get_width()
    while line_length > offset:
        for ang in [0, 90, 180]:
            line_length -= offset
            draw_line_polar(screen, p0, line_length, ang, "white", 5)
            p0.x, p0.y = get_p1_from_polar(p0.x, p0.y, line_length, ang)
            line_length -= offset
        line_length -= offset
        draw_line_polar(screen, p0, line_length, 270, "white", 5)
        p0.x, p0.y = get_p1_from_polar(p0.x, p0.y, line_length, 270)
        line_length -= offset
    pygame.image.save(screen, 'cc_pygame/gen/jpger_30.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
