import sys
import pygame
from utils.randomization import generate_random_color
from shapes.pygame_line import draw_line_polar
from shapes.pygame_circle import draw_circle
from shapes.pygame_line import draw_line_cartesian

def main() -> int:
    pygame.init()
    res = (2880, 2880)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    s = 0
    while s <= screen.get_width():
        draw_line_cartesian(screen, pygame.Vector2(s, 0), pygame.Vector2(screen.get_width() - s, screen.get_height()), "white", 5)
        s += 40
    s = 0
    while s <= screen.get_height():
        draw_line_cartesian(screen, pygame.Vector2(0, s), pygame.Vector2(screen.get_width(), screen.get_height() - s), "white", 5)
        s += 40
    s = screen.get_height() / 2
    while s >= 0:
        draw_circle(screen, "white", pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2), s, 5)
        s -= 40
    pygame.image.save(screen, 'cc_pygame/gen/jpger_09.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
