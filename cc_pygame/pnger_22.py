import sys
import pygame
from shapes.pygame_rectangle import draw_quick_rect
from shapes.pygame_triangle import draw_triangle

def main() -> int:
    pygame.init()
    res = (2400, 1200)
    screen = pygame.display.set_mode(res)
    screen_color = "white"
    screen.fill(screen_color)
    draw_quick_rect(screen, "black", pygame.Vector2(screen.get_width() / 2, screen.get_height() / 6), screen.get_width(), screen.get_height() / 3)
    draw_quick_rect(screen, "darkgreen", pygame.Vector2(screen.get_width() / 2, 5 * screen.get_height() / 6), screen.get_width(), screen.get_height() / 3)
    draw_triangle(screen, "red", [(0, 0), (screen.get_width() / 3, screen.get_height() / 2), (0, screen.get_height())])
    pygame.image.save(screen, 'cc_pygame/gen/jpger_22.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
