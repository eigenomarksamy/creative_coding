import sys
import pygame
from flowers import draw_nested_flowers, draw_multi_nested_flowers

def draw_vertical_side_flowers(screen: pygame.SurfaceType, radius: int,
                               color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos_x = width - 2 * radius
    pos_y = height - 2 * radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = 2 * radius
    pos_y = 2 * radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width - 2 * radius
    pos_y = 2 * radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = 2 * radius
    pos_y = height - 2 * radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width - 2 * radius
    pos_y = height / 2
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = 2 * radius
    pos_y = height / 2
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")

def draw_horizontal_side_flowers(screen: pygame.SurfaceType, radius: int,
                                 color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x = width / 2
    pos_y = height - 2 * radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x = width / 2
    pos_y = 2 * radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x = width / 4
    pos_y = 2 * radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x = 3 * width / 4
    pos_y = 2 * radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x = 3 * width / 4
    pos_y = height - 2 * radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x = width / 4
    pos_y = height - 2 * radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_real_center_background_flowers(screen: pygame.SurfaceType, radius: int,
                                        color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos_x = width / 2
    pos_y = height / 4 + radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width / 2
    pos_y = height - height / 4 - radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")

def draw_background_flowers(screen: pygame.SurfaceType, radius: int,
                            color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x = width / 4 - 2 * radius
    pos_y = height / 4 + radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x = width - width / 4 + 2 * radius
    pos_y = height / 4 + radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x = width / 4 - 2 * radius
    pos_y = height - height / 4 - radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x = width - width / 4 + 2 * radius
    pos_y = height - height / 4 - radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_center_background_flowers(screen: pygame.SurfaceType, radius: int,
                                   color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos_x = width / 2 + 6 * radius
    pos_y = height / 2 + 4 * radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x = width / 2 - 6 * radius
    pos_y = height / 2 - 4 * radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x = width / 2 + 6 * radius
    pos_y = height / 2 - 4 * radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    pos_x = width / 2 - 6 * radius
    pos_y = height / 2 + 4 * radius
    pos.append(pygame.Vector2(pos_x, pos_y))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_center_flowers(screen: pygame.SurfaceType, radius: int,
                        color: pygame.Color):
    width, height = screen.get_size()
    pos = []
    pos.append(pygame.Vector2(width / 4 + 2 * radius, height / 2))
    pos.append(pygame.Vector2(3 * width / 4 - 2 * radius, height / 2))
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
    pos.append(pygame.Vector2(8 * radius, 6 * radius))
    pos.append(pygame.Vector2(width - 8 * radius, height - 6 * radius))
    pos.append(pygame.Vector2(width - 8 * radius, 6 * radius))
    pos.append(pygame.Vector2(8 * radius, height - 6 * radius))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_outcasts2(screen: pygame.SurfaceType, radius: int,
                   color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos.append(pygame.Vector2(3 * width / 8, radius * 6))
    pos.append(pygame.Vector2(5 * width / 8, radius * 6))
    pos.append(pygame.Vector2(3 * width / 8, height - radius * 6))
    pos.append(pygame.Vector2(5 * width / 8, height - radius * 6))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_eccentrics(screen: pygame.SurfaceType, radius: int,
                    color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos.append(pygame.Vector2(3 * width / 16 - 2 * radius, height / 2))
    pos.append(pygame.Vector2(width - 3 * width / 16 + 2 * radius, height / 2))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_extreme_eccentrics(screen: pygame.SurfaceType, radius: int,
                            color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos.append(pygame.Vector2(4 * radius, height / 4 + 3 * radius))
    pos.append(pygame.Vector2(width - 4 * radius, height / 4 + 3 * radius))
    pos.append(pygame.Vector2(4 * radius, height / 2 + height / 4 - 3 * radius))
    pos.append(pygame.Vector2(width - 4 * radius, height / 2 + height / 4 - 3 * radius))
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_extreme_eccentrics2(screen: pygame.SurfaceType, radius: int,
                             color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos = []
    pos.append(pygame.Vector2(width / 4 + 4 * radius, height / 4 + 3 * radius))
    pos.append(pygame.Vector2(3 * width / 4 - 4 * radius, height / 4 + 3 * radius))
    pos.append(pygame.Vector2(width / 4 + 4 * radius, height / 2 + height / 4 - 3 * radius))
    pos.append(pygame.Vector2(3 * width / 4 - 4 * radius, height / 2 + height / 4 - 3 * radius))
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
    draw_outcasts(screen=screen, radius=radius, color="darkgoldenrod")
    draw_outcasts2(screen=screen, radius=radius, color="lightcoral")
    draw_eccentrics(screen=screen, radius=radius, color="lightcoral")
    draw_extreme_eccentrics(screen=screen, radius=radius, color="mediumseagreen")
    draw_extreme_eccentrics2(screen=screen, radius=radius, color="peachpuff2")
    draw_real_center_background_flowers(screen, radius, "cornflowerblue")
    draw_background_flowers(screen, radius, "indigo")
    draw_center_background_flowers(screen, radius, "teal")
    draw_vertical_side_flowers(screen, radius, "crimson")
    draw_horizontal_side_flowers(screen, radius, "midnightblue")
    draw_center_flowers(screen, radius, "gray58")
    draw_nested_flowers(screen,
                        pygame.Vector2(screen.get_width() / 2,
                                       screen.get_height() / 2),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1="white",
                        color2="black")
    pygame.image.save(screen, 'cc_pygame/gen/jpger_01.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
