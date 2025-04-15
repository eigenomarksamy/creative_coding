import sys
import pygame
from utils.geometric import get_abs_distance
from utils.randomization import generate_random_color_append
from star import draw_sophisticated_star

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    colors = [screen_color]
    side_len = 100
    center = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    pos_pre = pygame.Vector2(0, 0)
    factor = 0.1
    for i in range(0, int(screen.get_width() + 400), 100):
        for j in range(0, int(screen.get_height() + 400), 100):
            pos = pygame.Vector2(i, j)
            dist = get_abs_distance(pos.x, center.x,
                                    pos.y, center.y)
            dist_pre = get_abs_distance(pos_pre.x, center.x,
                                        pos_pre.y, center.y)
            if dist < dist_pre:
                side_len *= (1 + factor)
            else:
                side_len *= (1 - factor)
            pos_pre = pos
            color1, colors = generate_random_color_append(colors)
            color2, colors = generate_random_color_append(colors)
            draw_sophisticated_star(screen, color1, color2, pos, side_len, 10)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_66.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
