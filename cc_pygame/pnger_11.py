import sys
import pygame
from utils.geometric import get_p1_from_polar

def main() -> int:
    pygame.init()
    res = (2880, 2880)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    l = screen.get_width() / 2
    a = 0
    points = []
    while l > 0:
        x, y = get_p1_from_polar(x1=screen.get_width() / 2, y1=screen.get_height() / 2,
                                 rho=l, theta_deg=a)
        points.append(pygame.Vector2(x, y))
        l -= 1
        a += 1
    pygame.draw.lines(screen, "white", False, points, 2)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_11.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())