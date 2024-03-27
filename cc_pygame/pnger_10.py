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
    a = 0
    cc = 0
    c = generate_random_color(True)
    cs = [c]
    while l > 0:
        draw_line_polar(screen, pygame.Vector2(screen.get_width() / 2,
                                               screen.get_height() / 2),
                        l, a, c, 5)
        cc += 1
        l -= 1
        a += 1
        if cc >= 1:
            c = generate_random_color(True, not_this_color=cs)
            cs.append(c)
            cc = 0
    pygame.image.save(screen, 'cc_pygame/gen/jpger_10.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())