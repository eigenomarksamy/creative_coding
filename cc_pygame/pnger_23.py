import sys
import pygame
from utils.randomization import get_random_pos_on_screen, generate_random_color
from shapes.pygame_circle import draw_dashed_circle

def main() -> int:
    pygame.init()
    res = (2440, 2440)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    radius = 160
    centers = []
    colors_used = [screen_color]
    for _ in range(200):
        x, y = get_random_pos_on_screen(screen)
        centers.append(pygame.Vector2(x, y))
    color = generate_random_color(True, colors_used)
    for center in centers:
        draw_dashed_circle(screen, color, center, radius,
                           dash_length=16, gap_length=6, width=6)
        colors_used.append(color)
        color = generate_random_color(True, colors_used)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_23.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
