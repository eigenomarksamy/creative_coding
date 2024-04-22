import sys
import pygame
from shapes.pygame_circle import draw_circle
from shapes.pygame_triangle import draw_equilateral_from_center
from arrow import draw_quick_arrow

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    draw_quick_arrow(screen, pygame.Vector2(screen.get_width() / 2 - 25,
                                            screen.get_height() / 2),
                     "white", 0, 0, 45, 50, 5, 5)
    draw_circle(screen, "white", pygame.Vector2(screen.get_width() / 2,
                                                screen.get_height() / 2),
                 50, 5)
    draw_equilateral_from_center(screen, "white",
                                 pygame.Vector2(screen.get_width() / 2,
                                            screen.get_height() / 2), 50,
                                            50, angle=90)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_31.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
