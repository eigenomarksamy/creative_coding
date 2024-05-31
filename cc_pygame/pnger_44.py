import sys
import pygame
from shapes.pygame_circle import draw_circle
from shapes.pygame_line import draw_line_cartesian

def main() -> int:
    pygame.init()
    res = (7200, 4800)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    for x in range(0, screen.get_width(), 800):
        for y in range(0, screen.get_height(), 800):
            for i in range(10, 101, 1):
                draw_line_cartesian(screen, pygame.Vector2(0, y + i), pygame.Vector2(screen.get_width(), y + i), pygame.Color(i, i, i), 1)
                draw_line_cartesian(screen, pygame.Vector2(x + i, 0), pygame.Vector2(x + i, screen.get_height()), pygame.Color(i, i, i), 1)
    for i in range(1, 101):
        draw_circle(screen, f"grey{i}", pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2), 900 - i * 10)
    for y in range(200, screen.get_height(), 800):
        for x in range(200, screen.get_width(), 800):
            for i in range(0, 255, 1):
                draw_line_cartesian(screen, pygame.Vector2(0, y + i), pygame.Vector2(screen.get_width(), y + i), pygame.Color(i, i, i), 1)
                draw_line_cartesian(screen, pygame.Vector2(x + i, 0), pygame.Vector2(x + i, 3 * screen.get_height()), pygame.Color(i, i, i), 1)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_44.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
