import sys
import pygame
from utils.geometric import (check_points_within_bounds,
                             get_equ_tri_vertices_from_center,
                             get_opposite_points_equ_triangle)
from shapes.pygame_triangle import (draw_equilateral_from_center,
                                    draw_triangle)
from utils.randomization import generate_random_color_append

def convert_point_to_vector(point: tuple[float]) -> pygame.Vector2:
    return pygame.Vector2(point[0], point[1])

def convert_points_to_vectors(points: list[tuple[float]]) -> list[pygame.Vector2]:
    ret = []
    for point in points:
        ret.append(convert_point_to_vector(point))
    return ret

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    used_colors = [screen_color]
    draw_equilateral_from_center(screen, "white",
                                 pygame.Vector2(screen.get_width() / 2,
                                                screen.get_height() / 2),
                                50, 50)
    used_colors.append("white")
    tri_center = [(screen.get_width() / 2, screen.get_height() / 2)]
    itr = 0
    while True:
        tri_points = get_equ_tri_vertices_from_center(tri_center[0][0],
                                                      tri_center[0][1],
                                                      50, 0)
        tri_center.pop(0)
        valid = check_points_within_bounds(((0, screen.get_width()),
                                            (0, screen.get_height())),
                                           tri_points)
        if valid:
            points = convert_points_to_vectors(tri_points)
            for i in range(len(points)):
                p2, p3 = get_opposite_points_equ_triangle(points[i].x, points[i].y, 50, i * 120)
                p2_vec = convert_point_to_vector(p2)
                p3_vec = convert_point_to_vector(p3)
                color, used_colors = generate_random_color_append(not_this_color=used_colors)
                draw_triangle(screen, color, [points[i], p2_vec, p3_vec])
                tri_center.append((points[i].x, points[i].y))
                tri_center.append(p2)
                tri_center.append(p3)
        else:
            break
        if itr > 10000:
            break
        itr += 1
    pygame.image.save(screen, 'cc_pygame/gen/jpger_61.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
