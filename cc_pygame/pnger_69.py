import sys
import pygame
from flowers import draw_multi_nested_flowers, draw_nested_flowers
from utils.randomization import generate_random_color_append, get_random_pos_on_screen

def draw_filled_screen(screen: pygame.SurfaceType, radius: int,
                       color: pygame.Color) -> None:
    width, height = screen.get_size()
    if width % radius != 0 or height % radius != 0:
        return
    centers = []
    posx = radius * 2
    posy = radius * 2
    while posx <= width - radius * 2:
        posy = radius * 2
        while posy <= height - radius * 2:
            centers.append(pygame.Vector2(posx, posy))
            posy += radius * 4
        posx += radius * 4
    draw_multi_nested_flowers(screen=screen, pos=centers,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_randomized_filled_screen(screen: pygame.SurfaceType, radius: int,
                                  colors: list) -> None:
    width, height = screen.get_size()
    if width % radius != 0 or height % radius != 0:
        return
    posx = radius * 2
    posy = radius * 2
    while posx <= width - radius * 2:
        posy = radius * 2
        while posy <= height - radius * 2:
            color, colors = generate_random_color_append(not_this_color=colors, pre_set_a=True, max_color=100, min_color=50)
            colors.append(color)
            draw_nested_flowers(screen=screen,
                                pos=pygame.Vector2(posx, posy),
                                max_radius=radius,
                                min_radius=15,
                                decrement=5,
                                color1=color,
                                color2="black")
            posy += radius * 4
        posx += radius * 4
    # draw_multi_nested_flowers(screen=screen, pos=centers,
    #                           max_radius=radius, min_radius=15,
    #                           decrement=5, color1=color, color2="black")

def main() -> int:
    pygame.init()
    res = (2560, 1440)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    colors = [screen_color, "grey18"]
    radius = 40
    # draw_filled_screen(screen=screen, radius=radius, color="grey18")
    draw_randomized_filled_screen(screen=screen, radius=radius, colors=colors)
    # for _ in range(200):
    #     color, colors = generate_random_color_append(not_this_color=colors)
    #     colors.append(color)
    #     pos_x, pos_y = get_random_pos_on_screen(surface=screen)
    #     draw_multi_nested_flowers(screen=screen,
    #                               pos=[pygame.Vector2(pos_x, pos_y)],
    #                               max_radius=radius,
    #                               min_radius=15,
    #                               decrement=5,
    #                               color1=color,
    #                               color2="black")
    pygame.image.save(screen, 'cc_pygame/gen/jpger_69.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
