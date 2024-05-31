import sys
import math
import pygame
from utils.randomization import get_random_int
from shapes.pygame_line import draw_line_cartesian

def main() -> int:
    pygame.init()
    res = (2400, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    for x in range(0, screen.get_width(), 200):
        for y in range(0, screen.get_height(), 200):
            for i in range(10, 101, 1):
                start_angle = get_random_int(0, 360)
                difference = get_random_int(20, 60)
                pygame.draw.arc(screen, f"grey{i}", (x + i, y + i, 200 - 2 * i, 200 - 2 * i), math.radians(180 + 345), math.radians(180 + 285), 2)
                # pygame.draw.arc(screen, f"grey{i}", (x + i, y + i, 200 - 2 * i, 200 - 2 * i), math.radians(start_angle), math.radians(start_angle + difference), 2)
                draw_line_cartesian(screen, pygame.Vector2(0, y + i), pygame.Vector2(screen.get_width(), y + i), f"grey{i}", 1)
                draw_line_cartesian(screen, pygame.Vector2(x + i, 0), pygame.Vector2(x + i, screen.get_height()), f"grey{i}", 1)
    # pygame.draw.arc(screen, "grey90", (800, 250, 800, 800), math.radians(10), math.radians(340), 5)
    # pygame.draw.arc(screen, "grey80", (850, 300, 700, 700), math.radians(70), math.radians(50), 5)
    # pygame.draw.arc(screen, "grey70", (900, 350, 600, 600), math.radians(20), math.radians(340), 5)
    # pygame.draw.arc(screen, "grey60", (950, 400, 500, 500), math.radians(110), math.radians(100), 5)
    # pygame.draw.arc(screen, "grey50", (1000, 450, 400, 400), math.radians(150), math.radians(120), 5)
    # pygame.draw.arc(screen, "grey40", (1050, 500, 300, 300), math.radians(190), math.radians(150), 5)
    # pygame.draw.arc(screen, "grey30", (1100, 550, 200, 200), math.radians(90), math.radians(70), 5)
    # pygame.draw.arc(screen, "grey20", (1150, 600, 100, 100), math.radians(270), math.radians(250), 5)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_43.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
