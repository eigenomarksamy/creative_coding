import sys
import math
import random
import pygame
from utils.randomization import (get_random_pos, generate_random_color,
                                 get_random_int)
from utils.geometric import (get_coordinates_top_point_iso_triangle,
                             get_p1_from_polar)
from shapes.pygame_shape import draw_object, mirror_4_quads, mirror_on_horizontal, mirror_on_vertical
from shapes.pygame_rectangle import draw_quick_square
from shapes.pygame_circle import draw_circle
from shapes.pygame_triangle import draw_equilateral_from_center, draw_triangle
from shapes.pygame_line import draw_line_cartesian

def draw_shape_str(surface: pygame.SurfaceType, color: pygame.Color,
                   pos: pygame.Vector2, length: int, shape: str) -> None:
    if shape == "circle":
        draw_circle(surface, color, pos, length / 2)
    elif shape == "triangle":
        draw_equilateral_from_center(surface, color, pos, length, length, angle=random.choice([0, 180]))
    else:
        draw_quick_square(surface, color, pos, length)

def do_generation(surface: pygame.SurfaceType, color: pygame.Color) -> None:
    pos_limits = (pygame.Vector2(surface.get_width() / 2, surface.get_height() / 2),
                  pygame.Vector2(surface.get_width(), surface.get_height()))
    num_points = get_random_int(3, 6)
    pos_1 = [get_random_pos(pos_limits) for _ in range(num_points)]
    poses = mirror_4_quads(surface, pos_1)
    for i in poses:
        draw_object(surface, i, color)

def main() -> int:
    pygame.init()
    res = (2080, 2080)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    used_colors = [screen_color]
    side_length = 52
    shapes = ["circle", "square", "triangle"]
    screen.fill(screen_color)
    used_colors = [screen_color]
    for posy in range(int(side_length / 2), int(screen.get_height() / 2), side_length):
        for posx in range(int(side_length / 2), int(screen.get_width() / 2), side_length):
            draw = random.choice([True, False, False, True, False])
            color = generate_random_color(not_this_color=used_colors, a=255)
            if draw:
                shape = random.choice(shapes)
                draw_shape_str(screen, color, pygame.Vector2(posx, posy), side_length, shape)
                draw_shape_str(screen, color, pygame.Vector2(screen.get_width() - posx, posy), side_length, shape)
                draw_shape_str(screen, color, pygame.Vector2(posx, screen.get_height() - posy), side_length, shape)
                draw_shape_str(screen, color, pygame.Vector2(screen.get_width() - posx, screen.get_height() - posy), side_length, shape)
                used_colors.append(color)
    draw_circle(screen, "black", pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2), 600)
    draw_line_cartesian(screen, pygame.Vector2(0, screen.get_height() / 2),
                        pygame.Vector2(screen.get_width(), screen.get_height() / 2),
                        "black", 40)
    draw_line_cartesian(screen, pygame.Vector2(screen.get_width() / 2, 0),
                        pygame.Vector2(screen.get_width() / 2, screen.get_height()),
                        "black", 40)
    color = generate_random_color(not_this_color=used_colors)
    used_colors.append(color)
    tri_base_11 = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2 - 100)
    tri_base_12_x, tri_base_12_y = get_p1_from_polar(tri_base_11.x, tri_base_11.y, 150, 45)
    tri_base_12 = pygame.Vector2(tri_base_12_x, tri_base_12_y)
    tup1 = get_coordinates_top_point_iso_triangle(tri_base_11.x, tri_base_11.y, tri_base_12.x, tri_base_12.y, 500)
    draw_triangle(screen, color, [tri_base_11, tri_base_12, pygame.Vector2(tup1[0], tup1[1])], 5)
    tri_base_21 = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2 - 100)
    tri_base_22_x, tri_base_22_y = get_p1_from_polar(tri_base_21.x, tri_base_21.y, 150, 135)
    tri_base_22 = pygame.Vector2(tri_base_22_x, tri_base_22_y)
    tup1 = get_coordinates_top_point_iso_triangle(tri_base_21.x, tri_base_21.y, tri_base_22.x, tri_base_22.y, -500)
    draw_triangle(screen, color, [tri_base_21, tri_base_22, pygame.Vector2(tup1[0], tup1[1])], 5)
    tri_base_31 = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2 + 100)
    tri_base_32_x, tri_base_32_y = get_p1_from_polar(tri_base_31.x, tri_base_31.y, 150, 225)
    tri_base_32 = pygame.Vector2(tri_base_32_x, tri_base_32_y)
    tup1 = get_coordinates_top_point_iso_triangle(tri_base_31.x, tri_base_31.y, tri_base_32.x, tri_base_32.y, 500)
    draw_triangle(screen, color, [tri_base_31, tri_base_32, pygame.Vector2(tup1[0], tup1[1])], 5)
    tri_base_41 = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2 + 100)
    tri_base_42_x, tri_base_42_y = get_p1_from_polar(tri_base_41.x, tri_base_41.y, 150, 315)
    tri_base_42 = pygame.Vector2(tri_base_42_x, tri_base_42_y)
    tup1 = get_coordinates_top_point_iso_triangle(tri_base_41.x, tri_base_41.y, tri_base_42.x, tri_base_42.y, -500)
    draw_triangle(screen, color, [tri_base_41, tri_base_42, pygame.Vector2(tup1[0], tup1[1])], 5)
    color = generate_random_color(not_this_color=used_colors)
    used_colors.append(color)
    triang_points = [pygame.Vector2(screen.get_width() / 2 - 100, screen.get_height() / 2 - 100),
                     pygame.Vector2(screen.get_width() / 2 + 100, screen.get_height() / 2 - 100),
                     pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2 - 500)]
    triang_points2 = [pygame.Vector2(screen.get_width() / 2 - 100, screen.get_height() / 2 - 100),
                      pygame.Vector2(screen.get_width() / 2 - 100, screen.get_height() / 2 + 100),
                      pygame.Vector2(screen.get_width() / 2 - 500, screen.get_height() / 2)]
    t2 = mirror_on_horizontal(screen, triang_points)
    t3 = mirror_on_vertical(screen, triang_points2)
    draw_triangle(screen, color, triang_points, 5)
    draw_triangle(screen, color, t2, 5)
    draw_triangle(screen, color, triang_points2, 5)
    draw_triangle(screen, color, t3, 5)
    octa_points = []
    octa_side_length = 300
    octa_angle = 45
    for _ in range(8):
        x_i = screen.get_width() / 2 + octa_side_length * math.cos(math.radians(octa_angle))
        y_i = screen.get_width() / 2 - octa_side_length * math.sin(math.radians(octa_angle))
        octa_points.append(pygame.Vector2(x_i, y_i))
        octa_angle += 45
    color = generate_random_color(not_this_color=used_colors)
    used_colors.append(color)
    draw_object(screen, octa_points, color, 150)
    draw_circle(screen, "black", pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2), 200)
    color = generate_random_color(not_this_color=used_colors)
    used_colors.append(color)
    octa_points = []
    octa_side_length = 100
    octa_angle = 45
    for _ in range(8):
        x_i = screen.get_width() / 2 + octa_side_length * math.cos(math.radians(octa_angle))
        y_i = screen.get_width() / 2 - octa_side_length * math.sin(math.radians(octa_angle))
        octa_points.append(pygame.Vector2(x_i, y_i))
        octa_angle += 45
    draw_object(screen, octa_points, color, 15)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_40.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
