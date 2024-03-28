import sys
import pygame
import math
from shapes.pygame_circle import draw_circle

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    for x in range(screen.get_width()):
        y = screen.get_height() * math.sin(0 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = screen.get_height()
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = screen.get_height() / 8 + 5 * math.sin(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = 7 * screen.get_height() / 8 + 5 * math.sin(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = 3 * screen.get_height() / 8 + 5 * math.sin(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = 5 * screen.get_height() / 8 + 5 * math.sin(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = screen.get_height() / 4 + 10 * math.sin(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = 3 * screen.get_height() / 4 + 10 * math.sin(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = screen.get_height() / 2 + 50 * math.sin(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = screen.get_height() / 8 + 5 * math.cos(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = 7 * screen.get_height() / 8 + 5 * math.cos(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = 3 * screen.get_height() / 8 + 5 * math.cos(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = 5 * screen.get_height() / 8 + 5 * math.cos(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = screen.get_height() / 4 + 10 * math.cos(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = 3 * screen.get_height() / 4 + 10 * math.cos(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = screen.get_height() / 2 + 50 * math.cos(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    for x in range(screen.get_width()):
        y = screen.get_height() / 2 + 50 * math.cos(0.1 * x)
        draw_circle(screen, "white", pygame.Vector2(x, y), 2)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_21.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
