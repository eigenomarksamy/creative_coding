import pygame
from shapes.pygame_circle import Circle, draw_circles

def draw_flower(screen: pygame.SurfaceType, circles: list[Circle],
                center_pos_w: int, center_pos_h: int, radius: int,
                color: pygame.Color, color_extra: pygame.Color = None,
                center_on_top: bool = True, angle: float = 0,
                width_center: int = 0, width_corners: int = 0) -> None:
    if not center_on_top:
        if color_extra != None:
            circles.append(Circle(screen, color_extra,
                                pygame.Vector2(center_pos_w, center_pos_h),
                                radius, width_center))
        else:
            circles.append(Circle(screen, color,
                                pygame.Vector2(center_pos_w, center_pos_h),
                                radius, width_center))
    pos_x = center_pos_w - radius
    pos_y = center_pos_h - radius
    position = pygame.Vector2(pos_x, pos_y) - pygame.Vector2(center_pos_w, center_pos_h)
    position = position.rotate(angle) + pygame.Vector2(center_pos_w, center_pos_h)
    circles.append(Circle(screen, color, position,
                          radius, width_corners))
    pos_x = center_pos_w + radius
    pos_y = center_pos_h + radius
    position = pygame.Vector2(pos_x, pos_y) - pygame.Vector2(center_pos_w, center_pos_h)
    position = position.rotate(angle) + pygame.Vector2(center_pos_w, center_pos_h)
    circles.append(Circle(screen, color, position,
                          radius, width_corners))
    pos_x = center_pos_w + radius
    pos_y = center_pos_h - radius
    position = pygame.Vector2(pos_x, pos_y) - pygame.Vector2(center_pos_w, center_pos_h)
    position = position.rotate(angle) + pygame.Vector2(center_pos_w, center_pos_h)
    circles.append(Circle(screen, color, position,
                          radius, width_corners))
    pos_x = center_pos_w - radius
    pos_y = center_pos_h + radius
    position = pygame.Vector2(pos_x, pos_y) - pygame.Vector2(center_pos_w, center_pos_h)
    position = position.rotate(angle) + pygame.Vector2(center_pos_w, center_pos_h)
    circles.append(Circle(screen, color, position,
                          radius, width_corners))
    if center_on_top:
        if color_extra != None:
            circles.append(Circle(screen, color_extra,
                                pygame.Vector2(center_pos_w, center_pos_h),
                                radius, width_center))
        else:
            circles.append(Circle(screen, color,
                                pygame.Vector2(center_pos_w, center_pos_h),
                                radius, width_center))
    draw_circles(circles)

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
        draw_flower(screen, circles, pos.x, pos.y, r,
                    color, width_center, width_corners)

def draw_multi_nested_flowers(screen: pygame.SurfaceType, pos: list[pygame.Vector2],
                              max_radius: int, min_radius: int, decrement: int,
                              color1: pygame.Color, color2: pygame.Color,
                              width_center: int = 0, width_corners: int = 0) -> None:
    for p in pos:
        draw_nested_flowers(screen=screen, pos=p, max_radius=max_radius,
                            min_radius=min_radius, decrement=decrement,
                            color1=color1, color2=color2,
                            width_center=width_center,
                            width_corners=width_corners)
