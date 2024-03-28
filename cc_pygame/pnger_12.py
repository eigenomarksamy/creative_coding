import sys
import pygame
from utils.geometric import get_p1_from_polar

def main() -> int:
    pygame.init()
    res = (2880, 2880)
    screen = pygame.display.set_mode(res)
    screen_color = "grey10"
    screen.fill(screen_color)
    l = screen.get_width() / 2
    a0 = 0
    a1 = 180
    a2 = 0
    a3 = 180
    a4 = 90
    a5 = 270
    a6 = 90
    a7 = 270
    points0 = points1 = points2 = points3 = points4 = points5 = points6 = points7 = []
    while l > 0:
        x0, y0 = get_p1_from_polar(x1=screen.get_width() / 2, y1=screen.get_height() / 2,
                                   rho=l, theta_deg=a0)
        x1, y1 = get_p1_from_polar(x1=screen.get_width() / 2, y1=screen.get_height() / 2,
                                   rho=l, theta_deg=a1)
        x2, y2 = get_p1_from_polar(x1=screen.get_width() / 2, y1=screen.get_height() / 2,
                                   rho=l, theta_deg=a2)
        x3, y3 = get_p1_from_polar(x1=screen.get_width() / 2, y1=screen.get_height() / 2,
                                   rho=l, theta_deg=a3)
        # x4, y4 = get_p1_from_polar(x1=screen.get_width() / 2, y1=screen.get_height() / 2,
        #                            rho=l, theta_deg=a4)
        # x5, y5 = get_p1_from_polar(x1=screen.get_width() / 2, y1=screen.get_height() / 2,
        #                            rho=l, theta_deg=a5)
        # x6, y6 = get_p1_from_polar(x1=screen.get_width() / 2, y1=screen.get_height() / 2,
        #                            rho=l, theta_deg=a6)
        # x7, y7 = get_p1_from_polar(x1=screen.get_width() / 2, y1=screen.get_height() / 2,
        #                            rho=l, theta_deg=a7)
        points0.append(pygame.Vector2(x0, y0))
        points1.append(pygame.Vector2(x1, y1))
        points2.append(pygame.Vector2(x2, y2))
        points3.append(pygame.Vector2(x3, y3))
        # points4.append(pygame.Vector2(x4, y4))
        # points5.append(pygame.Vector2(x5, y5))
        # points6.append(pygame.Vector2(x6, y6))
        # points7.append(pygame.Vector2(x7, y7))
        l -= 1
        a0 += 1
        a1 -= 1
        a2 -= 1
        a3 += 1
        # a4 += 1
        # a5 -= 1
        # a6 -= 1
        # a7 += 1
    pygame.draw.lines(screen, "grey90", False, points0, 5)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_12.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())