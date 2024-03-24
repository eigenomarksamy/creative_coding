import sys
import pygame
from utils.randomization import generate_random_color
from flowers import draw_multi_nested_flowers

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

def draw_outer(screen: pygame.SurfaceType, radius: int) -> None:
    pos = []
    colors = []
    pos_x, pos_y = screen.get_width() / 2, screen.get_height() / 2
    # tmp = []
    # for rad_fac in range(int(screen.get_height() / radius), 1, -1):
    #     tmp.append(pygame.Vector2(rad_fac * radius, 0.5 * rad_fac * radius))
    #     tmp.append(pygame.Vector2(rad_fac * radius, screen.get_height() - 0.5 * rad_fac * radius))
    #     tmp.append(pygame.Vector2(screen.get_width() - rad_fac * radius, screen.get_height() - 0.5 * rad_fac * radius))
    #     tmp.append(pygame.Vector2(screen.get_width() - rad_fac * radius, 0.5 * rad_fac * radius))
    #     tmp.reverse()
    #     pos.append(tmp)
    #     colors.append(generate_random_color(True))
    # pos.reverse()
    # for i in range(len(pos)):
    #     draw_multi_nested_flowers(screen=screen, pos=pos[i],
    #                               max_radius=radius, min_radius=15,
    #                               decrement=5, color1=colors[i], color2="black")
    for rad_fac in range(37, 1, -1):
        pos.clear()
        pos.append(pygame.Vector2(pos_x, pos_y + rad_fac * radius))
        pos.append(pygame.Vector2(pos_x, pos_y - rad_fac * radius))
        pos.append(pygame.Vector2(pos_x - rad_fac * radius, pos_y))
        pos.append(pygame.Vector2(pos_x + rad_fac * radius, pos_y))
        pos.append(pygame.Vector2(pos_x - rad_fac * radius, pos_y - rad_fac * radius))
        pos.append(pygame.Vector2(pos_x - rad_fac * radius, pos_y + rad_fac * radius))
        pos.append(pygame.Vector2(pos_x + rad_fac * radius, pos_y - rad_fac * radius))
        pos.append(pygame.Vector2(pos_x + rad_fac * radius, pos_y + rad_fac * radius))
        pos.reverse()
        color = generate_random_color(True)
        draw_multi_nested_flowers(screen=screen, pos=pos,
                                max_radius=radius, min_radius=15,
                                decrement=5, color1=color, color2="black")

def draw_outer_10(screen: pygame.SurfaceType, radius: int,
                  color: pygame.Color) -> None:
    pos = []
    pos_x, pos_y = screen.get_width() / 2, screen.get_height() / 2
    pos.append(pygame.Vector2(pos_x - 6 * radius, pos_y - 6 * radius))
    pos.append(pygame.Vector2(pos_x - 6 * radius, pos_y + 6 * radius))
    pos.append(pygame.Vector2(pos_x + 6 * radius, pos_y - 6 * radius))
    pos.append(pygame.Vector2(pos_x + 6 * radius, pos_y + 6 * radius))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_outer_9(screen: pygame.SurfaceType, radius: int,
                 color: pygame.Color) -> None:
    pos = []
    pos_x, pos_y = screen.get_width() / 2, screen.get_height() / 2
    pos.append(pygame.Vector2(pos_x, pos_y - 6 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y + 6 * radius))
    pos.append(pygame.Vector2(pos_x - 6 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x + 6 * radius, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_outer_8(screen: pygame.SurfaceType, radius: int,
                 color: pygame.Color) -> None:
    pos = []
    pos_x, pos_y = screen.get_width() / 2, screen.get_height() / 2
    pos.append(pygame.Vector2(pos_x - 5 * radius, pos_y - 5 * radius))
    pos.append(pygame.Vector2(pos_x - 5 * radius, pos_y + 5 * radius))
    pos.append(pygame.Vector2(pos_x + 5 * radius, pos_y - 5 * radius))
    pos.append(pygame.Vector2(pos_x + 5 * radius, pos_y + 5 * radius))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_outer_7(screen: pygame.SurfaceType, radius: int,
                 color: pygame.Color) -> None:
    pos = []
    pos_x, pos_y = screen.get_width() / 2, screen.get_height() / 2
    pos.append(pygame.Vector2(pos_x, pos_y - 5 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y + 5 * radius))
    pos.append(pygame.Vector2(pos_x - 5 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x + 5 * radius, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_outer_6(screen: pygame.SurfaceType, radius: int,
                 color: pygame.Color) -> None:
    pos = []
    pos_x, pos_y = screen.get_width() / 2, screen.get_height() / 2
    pos.append(pygame.Vector2(pos_x - 4 * radius, pos_y - 4 * radius))
    pos.append(pygame.Vector2(pos_x - 4 * radius, pos_y + 4 * radius))
    pos.append(pygame.Vector2(pos_x + 4 * radius, pos_y - 4 * radius))
    pos.append(pygame.Vector2(pos_x + 4 * radius, pos_y + 4 * radius))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_outer_5(screen: pygame.SurfaceType, radius: int,
                 color: pygame.Color) -> None:
    pos = []
    pos_x, pos_y = screen.get_width() / 2, screen.get_height() / 2
    pos.append(pygame.Vector2(pos_x, pos_y - 4 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y + 4 * radius))
    pos.append(pygame.Vector2(pos_x - 4 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x + 4 * radius, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_outer_4(screen: pygame.SurfaceType, radius: int,
                 color: pygame.Color) -> None:
    pos = []
    pos_x, pos_y = screen.get_width() / 2, screen.get_height() / 2
    pos.append(pygame.Vector2(pos_x - 3 * radius, pos_y - 3 * radius))
    pos.append(pygame.Vector2(pos_x + 3 * radius, pos_y + 3 * radius))
    pos.append(pygame.Vector2(pos_x - 3 * radius, pos_y + 3 * radius))
    pos.append(pygame.Vector2(pos_x + 3 * radius, pos_y - 3 * radius))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_outer_3(screen: pygame.SurfaceType, radius: int,
                 color: pygame.Color) -> None:
    pos = []
    pos_x, pos_y = screen.get_width() / 2, screen.get_height() / 2
    pos.append(pygame.Vector2(pos_x - 3 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x + 3 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 3 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y - 3 * radius))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_outer_2(screen: pygame.SurfaceType, radius: int,
                 color: pygame.Color) -> None:
    pos = []
    pos_x, pos_y = screen.get_width() / 2, screen.get_height() / 2
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y - 2 * radius))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_outer_1(screen: pygame.SurfaceType, radius: int,
                 color: pygame.Color) -> None:
    pos = []
    pos_x, pos_y = screen.get_width() / 2, screen.get_height() / 2
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_center_flower(screen: pygame.SurfaceType, radius: int,
                       color: pygame.Color) -> None:
    pos = []
    pos_x, pos_y = screen.get_width() / 2, screen.get_height() / 2
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def main() -> int:
    pygame.init()
    res = (2880, 1440)
    radius = 40
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    draw_filled_screen(screen=screen, radius=radius, color="grey18")
    # draw_outer_10(screen, radius, "palegreen3")
    # draw_outer_9(screen, radius, "olivedrab4")
    # draw_outer_8(screen, radius, "mediumorchid4")
    # draw_outer_7(screen, radius, "indigo")
    # draw_outer_6(screen, radius, "lightcoral")
    # draw_outer_5(screen, radius, "mediumseagreen")
    # draw_outer_4(screen, radius, "cadetblue")
    # draw_outer_3(screen, radius, "peachpuff2")
    # draw_outer_2(screen, radius, "crimson")
    # draw_outer_1(screen, radius, "teal")
    draw_outer(screen, radius)
    draw_center_flower(screen, radius, "white")
    pygame.image.save(screen, 'cc_pygame/gen/jpger_04.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
