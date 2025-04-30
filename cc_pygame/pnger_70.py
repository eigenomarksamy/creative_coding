import sys
import math
import pygame
from star import draw_sophisticated_star
from utils.randomization import generate_random_color_append

def get_rev_color(color: pygame.Color) -> pygame.Color:
    return pygame.Color(255 - color.r, 255 - color.g, 255 - color.b)

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    colors = [screen_color, pygame.Color("grey30"), pygame.Color("grey70")]
    side_len = 100
    # for i in range(0, int(screen.get_width() + 400), 140):
    #     for j in range(0, int(screen.get_height() + 400), 140):
    #         pos = pygame.Vector2(i, j)
    #         draw_sophisticated_star(screen, "grey30", "grey70", pos, side_len, 10)
    x = 0
    inc = 2
    while x <= screen.get_width():
        color, colors = generate_random_color_append(colors)
        for fact in range(0, 10):
            y = math.sin(x) * 100 + screen.get_height() * fact / 10
            pos = pygame.Vector2(x, y)
            draw_sophisticated_star(screen, color, get_rev_color(color), pygame.Vector2(pos.x, pos.y), side_len, 10)
        x += inc
    pygame.image.save(screen, 'cc_pygame/gen/jpger_70.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
