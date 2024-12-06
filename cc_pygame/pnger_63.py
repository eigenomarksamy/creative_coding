import sys
import math
import pygame

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    center = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    pygame.draw.arc(screen, "white", (400, 400, 400, 400), math.radians(180), math.radians(0))
    pygame.image.save(screen, 'cc_pygame/gen/jpger_63.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
