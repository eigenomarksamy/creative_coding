import sys
import pygame
from flowers import draw_nested_flowers

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
    pos_x = width / 2
    pos_y = height - 2 * radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width / 2
    pos_y = 2 * radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width / 4 + radius
    pos_y = 2 * radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width / 2 + width / 4 - radius
    pos_y = 2 * radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width / 2 + width / 4 - radius
    pos_y = height - 2 * radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width / 4 + radius
    pos_y = height - 2 * radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")

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
    pos_x = width / 4 - 1.75 * radius
    pos_y = height / 4 + radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width - width / 4 + 1.75 * radius
    pos_y = height / 4 + radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width / 4 - 1.75 * radius
    pos_y = height - height / 4 - radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width - width / 4 + 1.75 * radius
    pos_y = height - height / 4 - radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")

def draw_center_background_flowers(screen: pygame.SurfaceType, radius: int,
                                   color: pygame.Color) -> None:
    width, height = screen.get_size()
    pos_x = width / 2 + 2.75 * radius
    pos_y = height / 4 + radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width / 2 - 2.75 * radius
    pos_y = height / 4 + radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width / 2 + 2.75 * radius
    pos_y = height - height / 4 - radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width / 2 - 2.75 * radius
    pos_y = height - height / 4 - radius
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        max_radius=radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")

def draw_center_flowers(screen: pygame.SurfaceType, radius: int,
                        color: pygame.Color):
    width, height = screen.get_size()
    pos_x = width / 4 + radius
    pos_y = height / 2
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = 3 * width / 4 - radius
    pos_y = height / 2
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")
    pos_x = width / 2
    pos_y = height / 2
    draw_nested_flowers(screen, pygame.Vector2(pos_x, pos_y),
                        radius, min_radius=15,
                        decrement=5, color1=color,
                        color2="black")

def main() -> int:
    pygame.init()
    res = (720, 720)
    radius = 50
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    draw_real_center_background_flowers(screen, radius, "cornflowerblue")
    draw_background_flowers(screen, radius, "indigo")
    draw_center_background_flowers(screen, radius, "teal")
    draw_vertical_side_flowers(screen, radius, "crimson")
    draw_horizontal_side_flowers(screen, radius, "midnightblue")
    draw_center_flowers(screen, radius, "gray58")
    pygame.image.save(screen, 'cc_pygame/gen/jpger_18.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
