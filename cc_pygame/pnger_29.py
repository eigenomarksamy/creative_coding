import sys
import pygame
from graph import gamify_life

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    gamify_life(screen, "black", "white", screen.get_width() // 7)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_29.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
