import math
import pygame
from shapes.pygame_rectangle import Square

def draw_nested_squares(surface: pygame.SurfaceType,
                        center_pos_x: int, center_pos_y: int,
                        color: pygame.Color, secondary_color: pygame.Color,
                        max_side_len: int, min_side_len: int,
                        decrement: int, angle: int = 0,
                        width: int = 0) -> None:
    color_to_draw = secondary_color
    for side_length in range(max_side_len, min_side_len, -decrement):
        if color_to_draw == secondary_color:
            color_to_draw = color
        else:
            color_to_draw = secondary_color
        Square(surface, color_to_draw,
               pygame.Vector2(center_pos_x, center_pos_y),
               side_length, angle, width).draw()

def draw_nested_angle_alternating_squares(surface: pygame.SurfaceType,
                                          center_pos_x: int,
                                          center_pos_y: int,
                                          color: pygame.Color,
                                          secondary_color: pygame.Color,
                                          init_side_len: int,
                                          num: int,
                                          angle1: int,
                                          angle2: int = 0,
                                          width: int = 0) -> None:
    color_to_draw = secondary_color
    angle = angle1
    side = init_side_len
    iteration = 0
    while init_side_len >= 0 and iteration < num:
        if color_to_draw == secondary_color:
            color_to_draw = color
        else:
            color_to_draw = secondary_color
        if angle == angle2:
            angle = angle1
        else:
            angle = angle2
        Square(surface, color_to_draw,
               pygame.Vector2(center_pos_x, center_pos_y),
               side, angle, width).draw()
        side /= math.sqrt(2)
        iteration += 1

def draw_frame(surface: pygame.SurfaceType,
               center_pos_x: int,
               center_pos_y: int,
               color: pygame.Color,
               side_len: int,
               angle: int = 0,
               width: int = 0) -> None:
    Square(surface=surface, color=color,
           pos=pygame.Vector2(center_pos_x, center_pos_y),
           side_length=side_len, angle=angle, width=width).draw()
