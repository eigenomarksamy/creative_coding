import sys
import math
import pygame
from shapes.pygame_line import draw_line_cartesian

def main() -> int:
    pygame.init()
    res = (2400, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    line1_point0 = pygame.Vector2(300, 0)
    line1_point1 = pygame.Vector2(line1_point0.x, screen.get_height())
    line2_point0 = pygame.Vector2(0, 200)
    line2_point1 = pygame.Vector2(screen.get_width(), line2_point0.y)
    line3_point0 = pygame.Vector2(0, 1100)
    line3_point1 = pygame.Vector2(screen.get_width(), line3_point0.y)
    line4_point0 = pygame.Vector2(1900, 0)
    line4_point1 = pygame.Vector2(line4_point0.x, screen.get_height())
    draw_line_cartesian(screen, line1_point0, line1_point1, "white", 5)
    draw_line_cartesian(screen, line2_point0, line2_point1, "white", 5)
    draw_line_cartesian(screen, line3_point0, line3_point1, "white", 5)
    draw_line_cartesian(screen, line4_point0, line4_point1, "white", 5)
    # pygame.draw.arc(screen, "grey90", (700, 200, 900, 900), math.radians(-10), math.radians(340), 5)
    # pygame.draw.arc(screen, "grey80", (800, 300, 800, 800), math.radians(20), math.radians(340), 5)
    # pygame.draw.arc(screen, "grey70", (900, 400, 700, 700), math.radians(50), math.radians(340), 5)
    # pygame.draw.arc(screen, "grey60", (1000, 500, 600, 600), math.radians(80), math.radians(340), 5)
    # pygame.draw.arc(screen, "grey50", (1100, 600, 500, 500), math.radians(110), math.radians(340), 5)
    # pygame.draw.arc(screen, "grey40", (1200, 700, 400, 400), math.radians(130), math.radians(340), 5)
    # pygame.draw.arc(screen, "grey30", (1300, 800, 300, 300), math.radians(160), math.radians(340), 5)
    # pygame.draw.arc(screen, "grey20", (1400, 900, 200, 200), math.radians(190), math.radians(340), 5)
    # pygame.draw.arc(screen, "grey10", (1500, 1000, 100, 100), math.radians(220), math.radians(340), 5)
    pygame.draw.arc(screen, "grey90", (800, 250, 800, 800), math.radians(10), math.radians(340), 5)
    pygame.draw.arc(screen, "grey80", (850, 300, 700, 700), math.radians(70), math.radians(50), 5)
    pygame.draw.arc(screen, "grey70", (900, 350, 600, 600), math.radians(20), math.radians(340), 5)
    pygame.draw.arc(screen, "grey60", (950, 400, 500, 500), math.radians(110), math.radians(100), 5)
    pygame.draw.arc(screen, "grey50", (1000, 450, 400, 400), math.radians(150), math.radians(120), 5)
    pygame.draw.arc(screen, "grey40", (1050, 500, 300, 300), math.radians(190), math.radians(150), 5)
    pygame.draw.arc(screen, "grey30", (1100, 550, 200, 200), math.radians(90), math.radians(70), 5)
    pygame.draw.arc(screen, "grey20", (1150, 600, 100, 100), math.radians(270), math.radians(250), 5)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_42.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
