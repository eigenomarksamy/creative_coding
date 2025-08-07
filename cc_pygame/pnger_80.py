import sys
import pygame
from shapes.pygame_rectangle import draw_quick_rect
from utils.randomization import get_random_dimensions, get_random_int, get_random_pos_on_screen, generate_random_color

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    color1 = pygame.Color(85, 0, 0)
    color2 = pygame.Color(0, 85, 0)
    color3 = pygame.Color(0, 0, 85)
    color4 = pygame.Color(85, 85, 0)
    color5 = pygame.Color(0, 85, 85)
    color6 = pygame.Color(85, 0, 85)
    color7 = pygame.Color(85, 85, 85)
    screen_color = generate_random_color(not_this_color=[color1, color2, color3,
                                                         color4, color5, color6, color7])
    screen.fill(screen_color)
    r_val = 255 - pygame.Color(screen_color).r
    g_val = 255 - pygame.Color(screen_color).g
    b_val = 255 - pygame.Color(screen_color).b
    color0 = pygame.Color(r_val, g_val, b_val)
    max_rects = get_random_int(100, 200)
    for _ in range(max_rects):
        rect = get_random_dimensions(max_height=150, max_width=150, min_width=1, min_height=1)
        pos = get_random_pos_on_screen(screen)
        draw_quick_rect(screen, color0,
                        pos=pygame.Vector2(x=pos[0], y=pos[1]),
                        width=rect[0], height=rect[1])
    max_rects = get_random_int(100, 200)
    for _ in range(max_rects):
        rect = get_random_dimensions(max_height=100, max_width=100, min_width=10, min_height=10)
        pos = get_random_pos_on_screen(screen)
        draw_quick_rect(screen, "black",
                        pos=pygame.Vector2(x=pos[0], y=pos[1]),
                        width=rect[0], height=rect[1])
    max_rects = get_random_int(50, 100)
    for _ in range(max_rects):
        rect = get_random_dimensions(max_height=50, max_width=50, min_width=25, min_height=25)
        pos = get_random_pos_on_screen(screen)
        draw_quick_rect(screen, color1,
                        pos=pygame.Vector2(x=pos[0], y=pos[1]),
                        width=rect[0], height=rect[1])
    for _ in range(max_rects):
        rect = get_random_dimensions(max_height=50, max_width=50, min_width=25, min_height=25)
        pos = get_random_pos_on_screen(screen)
        draw_quick_rect(screen, color2,
                        pos=pygame.Vector2(x=pos[0], y=pos[1]),
                        width=rect[0], height=rect[1])
    for _ in range(max_rects):
        rect = get_random_dimensions(max_height=50, max_width=50, min_width=25, min_height=25)
        pos = get_random_pos_on_screen(screen)
        draw_quick_rect(screen, color3,
                        pos=pygame.Vector2(x=pos[0], y=pos[1]),
                        width=rect[0], height=rect[1])
    max_rects = get_random_int(25, 50)
    for _ in range(max_rects):
        rect = get_random_dimensions(max_height=35, max_width=35, min_width=25, min_height=25)
        pos = get_random_pos_on_screen(screen)
        draw_quick_rect(screen, color4,
                        pos=pygame.Vector2(x=pos[0], y=pos[1]),
                        width=rect[0], height=rect[1])
    for _ in range(max_rects):
        rect = get_random_dimensions(max_height=35, max_width=35, min_width=25, min_height=25)
        pos = get_random_pos_on_screen(screen)
        draw_quick_rect(screen, color5,
                        pos=pygame.Vector2(x=pos[0], y=pos[1]),
                        width=rect[0], height=rect[1])
    for _ in range(max_rects):
        rect = get_random_dimensions(max_height=35, max_width=35, min_width=25, min_height=25)
        pos = get_random_pos_on_screen(screen)
        draw_quick_rect(screen, color6,
                        pos=pygame.Vector2(x=pos[0], y=pos[1]),
                        width=rect[0], height=rect[1])
    for _ in range(max_rects):
        rect = get_random_dimensions(max_height=35, max_width=35, min_width=25, min_height=25)
        pos = get_random_pos_on_screen(screen)
        draw_quick_rect(screen, color7,
                        pos=pygame.Vector2(x=pos[0], y=pos[1]),
                        width=rect[0], height=rect[1])
    pygame.image.save(screen, 'cc_pygame/gen/jpger_80.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
