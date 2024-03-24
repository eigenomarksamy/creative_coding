import sys
import pygame
from flowers import draw_multi_nested_flowers

def draw_vertical_side_flowers(screen: pygame.SurfaceType, radius: int,
                               color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x, pos_y = width - 2 * radius, height - 2 * radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 2 * radius, 2 * radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width - 2 * radius, 2 * radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 2 * radius, height - 2 * radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width - 2 * radius, height / 2
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 2 * radius, height / 2
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_horizontal_side_flowers(screen: pygame.SurfaceType, radius: int,
                                 color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x, pos_y = width / 2, height - 2 * radius
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width / 2, 2 * radius
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width / 4, 2 * radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 3 * width / 4, 2 * radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 3 * width / 4, height - 2 * radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width / 4, height - 2 * radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_real_center_background_flowers(screen: pygame.SurfaceType, radius: int,
                                        color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x, pos_y = width / 2, height / 4 + radius
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width / 2, height - height / 4 - radius
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_background_flowers(screen: pygame.SurfaceType, radius: int,
                            color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x, pos_y = width / 4 - 2 * radius, height / 4 + radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width - width / 4 + 2 * radius, height / 4 + radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width / 4 - 2 * radius, height - height / 4 - radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width - width / 4 + 2 * radius, height - height / 4 - radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_center_background_flowers(screen: pygame.SurfaceType, radius: int,
                                   color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x, pos_y = width / 2 + 6 * radius, height / 2 + 4 * radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width / 2 - 6 * radius, height / 2 - 4 * radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width / 2 + 6 * radius, height / 2 - 4 * radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width / 2 - 6 * radius, height / 2 + 4 * radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_center_flowers(screen: pygame.SurfaceType, radius: int,
                        color: pygame.Color):
    width, height = screen.get_size()
    pos = []
    pos_x, pos_y = width / 4 + 2 * radius, height / 2
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 3 * width / 4 - 2 * radius, height / 2
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

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

def draw_outcasts(screen: pygame.SurfaceType, radius: int,
                  color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x, pos_y = 8 * radius, 6 * radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width - 8 * radius, height - 6 * radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width - 8 * radius, 6 * radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 8 * radius, height - 6 * radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_outcasts2(screen: pygame.SurfaceType, radius: int,
                   color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x, pos_y = 3 * width / 8, radius * 6
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 5 * width / 8, radius * 6
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 3 * width / 8, height - radius * 6
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 5 * width / 8, height - radius * 6
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_eccentrics(screen: pygame.SurfaceType, radius: int,
                    color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x, pos_y = 3 * width / 16 - 2 * radius, height / 2
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width - 3 * width / 16 + 2 * radius, height / 2
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_extreme_eccentrics(screen: pygame.SurfaceType, radius: int,
                            color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x, pos_y = 4 * radius, height / 4 + 3 * radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width - 4 * radius, height / 4 + 3 * radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 4 * radius, height / 2 + height / 4 - 3 * radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width - 4 * radius, height / 2 + height / 4 - 3 * radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_extreme_eccentrics2(screen: pygame.SurfaceType, radius: int,
                             color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x, pos_y = width / 4 + 4 * radius, height / 4 + 3 * radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 3 * width / 4 - 4 * radius, height / 4 + 3 * radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y + 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = width / 4 + 4 * radius, height / 2 + height / 4 - 3 * radius
    pos.append(pygame.Vector2(pos_x + 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x, pos_y = 3 * width / 4 - 4 * radius, height / 2 + height / 4 - 3 * radius
    pos.append(pygame.Vector2(pos_x - 2 * radius, pos_y))
    pos.append(pygame.Vector2(pos_x, pos_y - 2 * radius))
    pos.append(pygame.Vector2(pos_x, pos_y))
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
    res = (2560, 1440)
    radius = 40
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    draw_filled_screen(screen=screen, radius=radius, color="grey18")
    draw_vertical_side_flowers(screen, radius, "crimson")
    draw_horizontal_side_flowers(screen, radius, "midnightblue")
    draw_outcasts(screen=screen, radius=radius, color="darkgoldenrod")
    draw_extreme_eccentrics(screen=screen, radius=radius, color="mediumseagreen")
    draw_eccentrics(screen=screen, radius=radius, color="lightcoral")
    draw_background_flowers(screen, radius, "indigo")
    draw_outcasts2(screen=screen, radius=radius, color="cadetblue2")
    draw_extreme_eccentrics2(screen=screen, radius=radius, color="peachpuff2")
    draw_center_flowers(screen, radius, "gray58")
    draw_real_center_background_flowers(screen, radius, "cornflowerblue")
    draw_center_background_flowers(screen, radius, "teal")
    draw_center_flower(screen, radius, "white")
    pygame.image.save(screen, 'cc_pygame/gen/jpger_02.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
