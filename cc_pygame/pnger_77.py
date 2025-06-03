import sys
import pygame
from shapes.pygame_line import draw_line_polar
from utils.randomization import generate_random_color_append

def main() -> int:
    pygame.init()
    res = (375, 3000)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    colors = [pygame.Color(screen_color)]
    for x in range(0, screen.get_width(), 2):
        pos = pygame.Vector2(x, 0)
        color, colors = generate_random_color_append(colors)
        draw_line_polar(surface=screen, p0=pos, color=color, length=screen.get_height(), width=1, angle=90)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_77.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
