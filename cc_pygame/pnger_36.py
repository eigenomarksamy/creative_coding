import sys
import pygame
from collections import deque
from utils.randomization import generate_random_color
from utils.geometric import get_p1_from_polar
from shapes.pygame_line import draw_line_polar
from shapes.pygame_circle import draw_circle

def draw_from_init_14(surface: pygame.SurfaceType,
                      init_point: pygame.Vector2) -> None:
    q = deque()
    q.append(init_point)
    rho = 80
    max_itr = 1e4
    itr = 0
    while len(q) > 0 and itr < max_itr:
        for a in [45, -45]:
            draw_line_polar(surface, q[0], rho, a, "white", 5)
            q.append(pygame.Vector2(get_p1_from_polar(q[0].x, q[0].y, rho, a)))
        q.popleft()
        itr += 1

def draw_from_init_12(surface: pygame.SurfaceType,
                     init_point: pygame.Vector2) -> None:
    q = deque()
    q.append(init_point)
    rho = 80
    max_itr = 1e4
    itr = 0
    while len(q) > 0 and itr < max_itr:
        for a in [270 - 45, 270 + 45]:
            draw_line_polar(surface, q[0], rho, a, "white", 5)
            q.append(pygame.Vector2(get_p1_from_polar(q[0].x, q[0].y, rho, a)))
        q.popleft()
        itr += 1

def draw_from_init_34(surface: pygame.SurfaceType,
                     init_point: pygame.Vector2) -> None:
    q = deque()
    q.append(init_point)
    rho = 80
    max_itr = 1e4
    itr = 0
    while len(q) > 0 and itr < max_itr:
        for a in [45, 90 + 45]:
            draw_line_polar(surface, q[0], rho, a, "white", 5)
            q.append(pygame.Vector2(get_p1_from_polar(q[0].x, q[0].y, rho, a)))
        q.popleft()
        itr += 1

def draw_from_init_23(surface: pygame.SurfaceType,
                     init_point: pygame.Vector2) -> None:
    q = deque()
    q.append(init_point)
    rho = 80
    max_itr = 1e4
    itr = 0
    while len(q) > 0 and itr < max_itr:
        for a in [180 + 45, 180 - 45]:
            draw_line_polar(surface, q[0], rho, a, "white", 5)
            q.append(pygame.Vector2(get_p1_from_polar(q[0].x, q[0].y, rho, a)))
        q.popleft()
        itr += 1

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(pygame.Color(screen_color))
    init_point14 = pygame.Vector2(0, screen.get_height() / 2)
    init_point23 = pygame.Vector2(screen.get_width(), screen.get_height() / 2)
    init_point12 = pygame.Vector2(screen.get_width() / 2, screen.get_height())
    init_point34 = pygame.Vector2(screen.get_width() / 2, 0)
    draw_from_init_14(screen, init_point14)
    draw_from_init_23(screen, init_point23)
    draw_from_init_12(screen, init_point12)
    draw_from_init_34(screen, init_point34)
    # init_point2 = pygame.Vector2(screen.get_width(), 0)
    # init_point1 = pygame.Vector2(0, 0)
    # init_point3 = pygame.Vector2(0, screen.get_height())
    # init_point4 = pygame.Vector2(screen.get_width(), screen.get_height())
    # center = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    # init_points = [init_point34, init_point23, init_point14, init_point12,
    #                init_point1, init_point2, init_point3, init_point4, center]
    # used_colors = [screen_color]
    # for ini in init_points:
    #     for r in range(0, int(screen.get_width() / 2) + 1, 80):
    #         color = generate_random_color(not_this_color=used_colors)
    #         used_colors.append(color)
    #         draw_circle(screen, color, ini, r, 5)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_36.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
