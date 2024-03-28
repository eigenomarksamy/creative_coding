import sys
import pygame
from utils.randomization import generate_random_color
from shapes.pygame_line import draw_line_polar
from shapes.pygame_circle import draw_circle
from shapes.pygame_line import draw_line_cartesian

def main() -> int:
    pygame.init()
    res = (2880, 2880)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    s = 0
    count = 0
    l_cl = generate_random_color(True)
    colors_used = [l_cl]
    while s <= screen.get_width():
        draw_line_cartesian(screen, pygame.Vector2(s, 0), pygame.Vector2(screen.get_width() - s, screen.get_height()), l_cl, 5)
        if count >= 1:
            l_cl = generate_random_color(True, colors_used)
            colors_used.append(l_cl)
            count = 0
        count += 1
        s += 40
    s = 0
    count = 0
    l_cl = generate_random_color(True, colors_used)
    while s <= screen.get_height():
        draw_line_cartesian(screen, pygame.Vector2(0, s), pygame.Vector2(screen.get_width(), screen.get_height() - s), l_cl, 5)
        if count >= 1:
            l_cl = generate_random_color(True, colors_used)
            colors_used.append(l_cl)
            count = 0
        count += 1
        s += 40
    s = screen.get_height() / 2
    count = 0
    l_cl = generate_random_color(True, colors_used)
    while s >= 0:
        draw_circle(screen, l_cl, pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2), s, 5)
        s -= 40
        if count >= 1:
            l_cl = generate_random_color(True, colors_used)
            colors_used.append(l_cl)
            count = 0
        count += 1
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
    pygame.image.save(screen, 'cc_pygame/gen/jpger_13.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
