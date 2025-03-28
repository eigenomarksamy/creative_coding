import sys
import pygame
from utils.randomization import generate_random_color_append
from shapes.pygame_rectangle import draw_quick_square

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    edge_width = 2
    spacing = edge_width * 2
    pos = pygame.Vector2(0, 0)
    colors_used = [screen_color]
    while pos.x < screen.get_width() / 2 and pos.y < screen.get_height() / 2:
        color, colors_used = generate_random_color_append(colors_used)
        draw_quick_square(screen, color, pos, pos.x + edge_width, border_width=edge_width)
        pos = pygame.Vector2(pos.x + spacing, pos.y + spacing)
    pos = pygame.Vector2(screen.get_width(), 0)
    while pos.x > screen.get_width() / 2:
        color, colors_used = generate_random_color_append(colors_used)
        draw_quick_square(screen, color, pos, pos.x - edge_width, border_width=edge_width)
        pos = pygame.Vector2(pos.x - spacing, pos.y)
    pos = pygame.Vector2(screen.get_width(), screen.get_height())
    while pos.x > screen.get_width() / 2 and pos.y > screen.get_height() / 2:
        color, colors_used = generate_random_color_append(colors_used)
        draw_quick_square(screen, color, pos, pos.x - edge_width, border_width=edge_width)
        pos = pygame.Vector2(pos.x - spacing, pos.y - spacing)
    pos = pygame.Vector2(0, screen.get_height())
    while pos.y > screen.get_height() / 2:
        color, colors_used = generate_random_color_append(colors_used)
        draw_quick_square(screen, color, pos, pos.y - edge_width, border_width=edge_width)
        pos = pygame.Vector2(pos.x, pos.y - spacing)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_64.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
