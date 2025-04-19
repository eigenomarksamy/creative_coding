import sys
import pygame
from utils.randomization import generate_random_color_append, get_random_pos_on_screen, get_random_angle, get_random_int
from arrow import draw_quick_arrow

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    colors = [screen_color]
    for i in range(1000):
        x, y = get_random_pos_on_screen(screen)
        color, colors = generate_random_color_append(colors)
        angle = get_random_angle([0, 360, 1])
        draw_quick_arrow(surface=screen, head_pos=pygame.Vector2(x, y),
                         color=color, angle=angle, tail_length=get_random_int(10, 500),
                         head_angle=angle, head_length=get_random_int(10, 100),
                         head_width=get_random_int(1, 20), tail_width=get_random_int(1, 20),
                         hollow_width=get_random_int(0, 20))
    pygame.image.save(screen, 'cc_pygame/gen/jpger_67.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
