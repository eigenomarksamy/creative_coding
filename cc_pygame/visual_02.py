import sys
import random
import pygame
from flowers import draw_flower
from utils.randomization import get_random_color_list, get_random_pos_on_screen

def main() -> int:
    pygame.init()
    res = (1280, 720)
    max_iterations = 35
    iterations = 0
    radius = 50
    colors = ["white", "crimson", "teal", "cyan", "violet", "indigo",
              "orange", "red", "yellow", "green", "grey", "black"]
    circles = []
    screen = pygame.display.set_mode(res)
    clock = pygame.time.Clock()
    running = True
    screen_color = colors[random.randint(0, len(colors) - 1)]
    screen.fill(screen_color)
    colors.remove(screen_color)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if iterations < max_iterations:
            random_x, random_y = get_random_pos_on_screen(screen,
                                                          (2 * radius, 2 * radius),
                                                          (2 * radius, 2 * radius))
            random_color = get_random_color_list(colors)
            draw_flower(screen=screen, circles=circles, center_pos_w=random_x,
                        center_pos_h=random_y, radius=radius,
                        color=random_color)
            iterations += 1
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
