import sys
import pygame
from shapes.pygame_triangle import draw_equilateral_from_center
from utils.randomization import generate_random_color

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    base = height = 1000
    for angle in range(0, 360):
        draw_equilateral_from_center(surface=screen, color="white",
                                    center=pygame.Vector2(x=screen.get_width() / 2,
                                                        y=screen.get_height() / 2),
                                    base=base, height=height,
                                    width=2, angle=angle)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_27.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
