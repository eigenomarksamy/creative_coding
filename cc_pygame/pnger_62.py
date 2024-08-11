import sys
import pygame
from utils.randomization import generate_random_color_append
from shapes.pygame_line import draw_line_polar
from shapes.pygame_circle import draw_point

def draw_double_lines(surface: pygame.SurfaceType, color: pygame.Color,
                      center: pygame.Vector2, width: int, length: int) -> None:
    draw_line_polar(surface, center, length, 135, color, width)
    draw_line_polar(surface, center, length, 315, color, width)

def main() -> int:
    pygame.init()
    res = (2800, 2800)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    used_colors = [screen_color]
    center_points = []
    act_center_points = []
    for x, y in enumerate(range(screen.get_width())):
        center_points.append(pygame.Vector2(x, y))
    half_diag_max = int((2 ** 0.5) * screen.get_width() / 2)
    x_limits = (int(0.25 * screen.get_width()), int(0.75 * screen.get_width()))
    for point in center_points:
        if point.x > x_limits[0] and point.x < x_limits[1]:
            act_center_points.append(pygame.Vector2(point.x, point.y))
    for point in act_center_points:
        draw_point(screen, "white", point)
    used_colors.append("white")
    len_1 = 0.5 * half_diag_max
    quart_point_idx = int(len(act_center_points) / 4)
    center_point_idx = int(len(act_center_points) / 2)
    quart_3_point_idx = center_point_idx + quart_point_idx
    limits1 = (0, quart_point_idx - 1)
    limits2 = (quart_point_idx + 1, center_point_idx - 1)
    limits3 = (center_point_idx + 1, quart_3_point_idx - 1)
    limits4 = (quart_3_point_idx + 1, len(act_center_points) - 2)
    a1 = (10 - 1.2 * len_1) / ((limits1[1]) ** 2)
    b1 = (0.3 * len_1 - 5) / limits1[1]
    c1 = 0.9 * len_1
    a2 = (0.9 * half_diag_max - 6 - (int(limits2[1] - limits2[0] / 2) * ((0.9 * half_diag_max - 6) / (limits2[1] - limits2[0])))) / ((((limits2[1] - limits2[0]) ** 2) / 4) - (limits2[0] ** 2))
    b2 = (0.9 * half_diag_max - 6 - a2 * ((limits2[1] ** 2) - (limits2[0] ** 2))) / (limits2[1] - limits2[0])
    c2 = 6 - a2 * (limits2[0] ** 2) - b2 * (limits2[0])
    l30 = limits3[0]
    l32 = limits3[1]
    l31 = int((l32 - l30) / 2)
    d = half_diag_max
    numerator_a = -0.65 * d - ((6 - 0.25 * d) / (l32 - l31)) * (l31 - l30)
    denominator_a = (l31**2 - l30**2) - ((l32**2 - l31**2) * (l31 - l30)) / (l32 - l31)
    a3 = numerator_a / denominator_a
    b3 = (6 - 0.25 * d - a3 * (l32**2 - l31**2)) / (l32 - l31)
    c3 = 0.9 * d - a3 * l30**2 - b3 * l30
    l40 = limits4[0]
    l42 = limits4[1]
    l41 = int((l42 - l40) / 2)
    numerator_a = 0.75 * d - 5 - ((-0.25 * d) * (l41 - l40) / (l42 - l41))
    denominator_a = (l41**2 - l40**2) - ((l42**2 - l41**2) * (l41 - l40)) / (l42 - l41)
    a4 = numerator_a / denominator_a
    b4 = (-0.25 * d - a4 * (l42**2 - l41**2)) / (l42 - l41)
    c4 = 5 - a4 * l40**2 - b4 * l40
    for x in range(limits1[0], limits1[1]):
        length = a1 * (x ** 2) + b1 * x + c1
        color, used_colors = generate_random_color_append(used_colors)
        draw_double_lines(screen, color, act_center_points[x], 5, length)
    for x in range(limits2[0], limits2[1]):
        length = a2 * (x ** 2) + b2 * x + c2
        color, used_colors = generate_random_color_append(used_colors)
        draw_double_lines(screen, color, act_center_points[x], 5, length)
    for x in range(limits3[0], limits3[1]):
        length = a3 * (x ** 2) + b3 * x + c3
        color, used_colors = generate_random_color_append(used_colors)
        draw_double_lines(screen, color, act_center_points[x], 5, length)
    for x in range(limits4[0], limits4[1]):
        length = a4 * (x ** 2) + b4 * x + c4
        color, used_colors = generate_random_color_append(used_colors)
        draw_double_lines(screen, color, act_center_points[x], 5, length)
    draw_double_lines(screen, "white", act_center_points[0], 5, len_1 * 0.9)
    draw_double_lines(screen, "white", act_center_points[center_point_idx], 5, 0.9 * half_diag_max)
    draw_double_lines(screen, "white", act_center_points[quart_point_idx], 5, 5)
    draw_double_lines(screen, "white", act_center_points[quart_3_point_idx], 5, 5)
    draw_double_lines(screen, "white", act_center_points[-1], 5, len_1 * 0.9)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_62.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
