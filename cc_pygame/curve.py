import pygame
from utils.geometric import get_p1_from_polar

def draw_spiral(surface: pygame.SurfaceType, color: pygame.Color,
                init_pos: pygame.Vector2, init_len: float,
                init_angle_deg: float,
                width: int = 1,
                angle_change: float = -1,
                len_change: float = -1,
                stop_len: float = 0) -> None:
    if init_len > stop_len:
        l = init_len
        a = init_angle_deg
        points = []
        while l > stop_len:
            x, y = get_p1_from_polar(x1=init_pos.x, y1=init_pos.y,
                                     rho=l, theta_deg=a)
            points.append(pygame.Vector2(x, y))
            l += len_change
            a += angle_change
        pygame.draw.lines(surface=surface, color=color, closed=False,
                          points=points, width=width)
    elif init_len < stop_len:
        l = init_len
        a = init_angle_deg
        points = []
        while l < stop_len:
            x, y = get_p1_from_polar(x1=init_pos.x, y1=init_pos.y,
                                     rho=l, theta_deg=a)
            points.append(pygame.Vector2(x, y))
            l += len_change
            a += angle_change
        pygame.draw.lines(surface=surface, color=color, closed=False,
                          points=points, width=width)
    else:
        return

def draw_curve(surface: pygame.SurfaceType, color: pygame.Color,
               points: list[pygame.Vector2], width: int = 1,
               is_connected: bool = False) -> None:
    pygame.draw.lines(surface=surface, color=color, closed=is_connected,
                      points=points, width=width)
