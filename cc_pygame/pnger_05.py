import sys
import pygame
from flowers import draw_multi_nested_flowers

def draw_frame(screen: pygame.SurfaceType,
               top_left_corner: pygame.Vector2,
               bottom_right_corner: pygame.Vector2,
               radius: int, color: pygame.Color) -> None:
    pos = []
    posx, posy = top_left_corner.x, top_left_corner.y
    while posy < bottom_right_corner.y:
        posy += 4 * radius
        pos.append(pygame.Vector2(posx, posy))
    posx, posy = top_left_corner.x, top_left_corner.y
    while posx <= bottom_right_corner.x:
        pos.append(pygame.Vector2(posx, posy))
        posx += 4 * radius
    posx, posy = bottom_right_corner.x, bottom_right_corner.y
    while posx > top_left_corner.x:
        pos.append(pygame.Vector2(posx, posy))
        posx -= 4 * radius
    posx, posy = bottom_right_corner.x, bottom_right_corner.y
    while posy > top_left_corner.x:
        pos.append(pygame.Vector2(posx, posy))
        posy -= 4 * radius
    draw_multi_nested_flowers(screen=screen, pos=pos,
                              max_radius=radius, min_radius=15,
                              decrement=5, color1=color, color2="black")

def draw_frames(screen: pygame.SurfaceType, radius: int,
                 colors: list[pygame.Color]) -> None:
    width, height = screen.get_size()
    multi = 2
    for color in colors:
        draw_frame(screen, pygame.Vector2(radius * multi, radius * multi),
                   pygame.Vector2(width - multi * radius,
                                  height - multi * radius),
                   radius, color)
        multi += 2

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
    res = (1440, 2880)
    radius = 40
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    colors = []
    for i in range(10, 100, 10):
        colors.append(f"grey{i}")
    draw_frames(screen, radius, colors)
    draw_center_flower(screen, radius, "white")
    pygame.image.save(screen, 'cc_pygame/gen/jpger_05.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
