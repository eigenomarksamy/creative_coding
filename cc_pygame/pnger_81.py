import sys
import pygame
from shapes.pygame_circle import draw_circle
from utils.geometric import get_p1_from_polar

def main() -> int:
    pygame.init()
    res = (3000, 3000)
    screen = pygame.display.set_mode(res)
    screen_color = "grey50"
    screen.fill(screen_color)
    radius = 1000
    radius_small = 100
    c_vals = 0
    for s in range(0, 360, int(360 / 12)):
        color = pygame.Color(int(c_vals), int(c_vals), int(c_vals))
        x2, y2 = get_p1_from_polar(screen.get_width() // 2, screen.get_height() // 2, radius, s - 90)
        draw_circle(screen, color, pygame.Vector2(x2, y2), radius_small)
        print(f"Draw circle at angle {s}° with color #{color.r:02x}{color.g:02x}{color.b:02x} at position ({x2-125}, {y2-125})")
        draw_circle(screen, pygame.Color(abs(255 - c_vals), abs(255 - c_vals), abs(255 - c_vals)), pygame.Vector2(x2, y2), radius_small, 10)
        c_vals += 21
    pygame.image.save(screen, 'cc_pygame/gen/jpger_81.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
