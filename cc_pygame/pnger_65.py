import sys
import pygame
from star import draw_sophisticated_star

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    side_len = 100
    for i in range(0, int(screen.get_width() + 400), 200):
        for j in range(0, int(screen.get_height() + 400), 200):
            pos = pygame.Vector2(i, j)
            draw_sophisticated_star(screen, "grey30", "grey70", pos, side_len, 10)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_65.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
