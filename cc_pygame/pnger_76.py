import sys
import pygame
from shapes.pygame_line import draw_line_polar
from utils.randomization import generate_random_color_append

def main() -> int:
    pygame.init()
    res = (3000, 375)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    colors = [pygame.Color(screen_color)]
    screen.fill(screen_color)
    for y in range(0, screen.get_height(), 2):
        pos = pygame.Vector2(0, y)
        color, colors = generate_random_color_append(colors)
        draw_line_polar(surface=screen, p0=pos, color=color, length=screen.get_width(), width=1, angle=0)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_76.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
