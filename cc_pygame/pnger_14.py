import sys
import pygame
from utils.randomization import get_random_pos_on_screen

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
    pygame.draw.lines(screen, "white", True, pos, 5)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_14.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
