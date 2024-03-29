import sys
import pygame
from shapes.pygame_line import draw_line_polar, draw_line_cartesian
from shapes.pygame_circle import draw_circle
from shapes.pygame_rectangle import draw_quick_square

def draw_left(screen: pygame.SurfaceType) -> None:
    w = 64
    point0 = pygame.Vector2(w, w)
    point1 = pygame.Vector2(w, screen.get_height() - w)
    point2 = pygame.Vector2(0, 0)
    point3 = pygame.Vector2(0, screen.get_height())
    while w <= screen.get_width() / 2:
        upper_h = w
        lower_h = screen.get_height() - w
        point0 = pygame.Vector2(w, upper_h)
        point1 = pygame.Vector2(w, lower_h)
        pygame.draw.polygon(screen, "white", [point2, point0, point1, point3])
        y = upper_h
        while y <= lower_h:
            draw_line_polar(screen, pygame.Vector2(point2.x, y), 64, 0, "black", 8)
            draw_circle(screen, "black", pygame.Vector2((point2.x + point0.x) / 2, y + 64), 16)
            y += 128
        draw_line_cartesian(screen, point0, point1, "black", 8)
        point2 = point0
        point3 = point1
        w += 64

def draw_right(screen: pygame.SurfaceType) -> None:
    w = screen.get_width()
    while w > screen.get_width() / 2:
        upper_h = screen.get_height() - w
        lower_h = w
        y = upper_h + 64
        while y < lower_h:
            draw_line_polar(screen, pygame.Vector2(w, y), 64, 180, "white", 8)
            draw_circle(screen, "white", pygame.Vector2(w + 32, y), 16)
            y += 128
        draw_line_cartesian(screen, pygame.Vector2(w, upper_h),
                            pygame.Vector2(w, lower_h), "white", 8)
        w -= 64

def draw_up(screen: pygame.SurfaceType) -> None:
    h = 0
    while h < screen.get_height() / 2:
        left_w = h
        right_w = screen.get_width() - h
        x = left_w + 64
        while x < right_w - 32:
            draw_line_polar(screen, pygame.Vector2(x, h), 64, 90, "white", 8)
            draw_circle(screen, "white", pygame.Vector2(x, h - 32), 16)
            x += 128
        draw_line_cartesian(screen, pygame.Vector2(left_w, h),
                            pygame.Vector2(right_w, h), "white", 8)
        h += 64

def draw_down(screen: pygame.SurfaceType) -> None:
    h = screen.get_height()
    point0 = pygame.Vector2(screen.get_width(), 0)
    point1 = pygame.Vector2(screen.get_width() - h, screen.get_height() - h)
    point2 = pygame.Vector2(screen.get_width(), screen.get_width())
    point3 = pygame.Vector2(screen.get_width() - h, h)
    while h >= screen.get_height() / 2:
        left_w = screen.get_width() - h
        right_w = h
        point0 = pygame.Vector2(left_w, h)
        point1 = pygame.Vector2(right_w, h)
        pygame.draw.polygon(screen, "white", [point2, point0, point1, point3])
        x = left_w
        while x <= right_w:
            draw_line_polar(screen, pygame.Vector2(x, point2.y), 64, 270, "black", 8)
            draw_circle(screen, "black", pygame.Vector2(x + 64, (point2.y + point0.y) / 2), 16)
            x += 128
        draw_line_cartesian(screen, point0, point1, "black", 8)
        point2 = point0
        point3 = point1
        h -= 64

def main() -> int:
    pygame.init()
    res = (2048, 2048)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    draw_left(screen)
    draw_right(screen)
    draw_up(screen)
    draw_down(screen)
    ang = 45
    starting_points = [pygame.Vector2(x=0, y=0),
                       pygame.Vector2(x=screen.get_width(), y=0),
                       pygame.Vector2(x=screen.get_width(), y=screen.get_height()),
                       pygame.Vector2(x=0,  y=screen.get_height())]
    for sp in starting_points:
        draw_line_polar(surface=screen, p0=sp,
                        length=screen.get_width() * (2 ** 0.5) / 2,
                        angle=ang, color="white", width=8)
        ang += 90
    draw_line_cartesian(screen, pygame.Vector2(0, screen.get_height()),
                        pygame.Vector2(screen.get_width() / 2,
                                       screen.get_height() / 2),
                        "black", 8)
    # i = 64
    # while i < screen.get_width() / 2:
    #     draw_quick_square(screen, "black", pygame.Vector2(i, screen.get_height() - i), 128)
    #     draw_quick_square(screen, "white", pygame.Vector2(screen.get_width() - i, i), 128)
    #     i += 128
    pygame.image.save(screen, 'cc_pygame/gen/jpger_24.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
