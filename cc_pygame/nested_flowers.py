import sys
import pygame
from shapes.pygame_circle import Circle, draw_circles

def draw_simple_flower(screen: pygame.SurfaceType, circles: list[Circle],
                       center_pos_w: int, center_pos_h: int,
                       radius: int, color: pygame.Color,
                       width_center: int = 0, width_corners: int = 0) -> None:
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w - radius,
                                         center_pos_h - radius),
                          radius, width_corners))
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w + radius,
                                         center_pos_h + radius),
                          radius, width_corners))
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w + radius,
                                         center_pos_h - radius),
                          radius, width_corners))
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w - radius,
                                         center_pos_h + radius),
                          radius, width_corners))
    circles.append(Circle(screen, color,
                          pygame.Vector2(center_pos_w, center_pos_h),
                          radius, width_center))
    draw_circles(circles)

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

def draw_nested_flowers(screen: pygame.SurfaceType, pos: pygame.Vector2,
                        max_radius: int, min_radius: int, decrement: int,
                        color1: pygame.Color, color2: pygame.Color,
                        width_center: int = 0, width_corners: int = 0) -> None:
    circles = []
    color = color2
    for r in range(max_radius, min_radius - decrement, -decrement):
        if color == color2:
            color = color1
        else:
            color = color2
        draw_simple_flower(screen, circles, pos.x, pos.y, r,
                           color, width_center, width_corners)

def main() -> int:
    pygame.init()
    res = (720, 720)
    radius = 50
    min_radius = 15
    radius_decrement = 5
    colors = ["white", "crimson", "teal", "cyan", "violet", "indigo",
              "orange", "red", "yellow", "green", "grey", "black"]
    screen = pygame.display.set_mode(res)
    clock = pygame.time.Clock()
    running = True
    screen_color = colors[-1]
    screen.fill(screen_color)
    colors.remove(screen_color)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw_real_center_background_flowers(screen, radius, "cornflowerblue")
        draw_background_flowers(screen, radius, "indigo")
        draw_center_background_flowers(screen, radius, "teal")
        draw_vertical_side_flowers(screen, radius, "crimson")
        draw_horizontal_side_flowers(screen, radius, "midnightblue")
        draw_nested_flowers(screen,
                            pygame.Vector2(screen.get_width() / 4 + radius, screen.get_height() / 2),
                            radius, min_radius, radius_decrement, "gray58", "black")
        draw_nested_flowers(screen,
                            pygame.Vector2(3 * screen.get_width() / 4 - radius, screen.get_height() / 2),
                            radius, min_radius, radius_decrement, "gray58", "black")
        draw_nested_flowers(screen,
                            pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2),
                            radius, min_radius, radius_decrement, "gray58", "black")
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())

