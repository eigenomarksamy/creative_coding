import math
import pygame

class Circle:

    def __init__(self, surface: pygame.SurfaceType,
                 color: pygame.Color, pos: pygame.Vector2,
                 radius: int, width: int = 0,
                 dashed: bool = False, dash_len: int = 5,
                 gap_len: int = 5) -> None:
        self.surface = surface
        self.color = color
        self.pos = pos
        self.radius = radius
        self.width = width
        self.dashed = dashed
        self.dash_len = dash_len
        self.gap_len = gap_len

    def draw(self) -> None:
        if self.dashed:
            x = self.pos.x
            y = self.pos.y
            circumference = 2 * math.pi * self.radius
            num_dashes = int(circumference / (self.dash_len + self.gap_len))

            angle_step = 360 / num_dashes

            for i in range(num_dashes):
                start_angle = math.radians(i * angle_step)
                end_angle = math.radians((i + 1) * angle_step)

                x1 = int(x + self.radius * math.cos(start_angle))
                y1 = int(y + self.radius * math.sin(start_angle))
                x2 = int(x + self.radius * math.cos(end_angle))
                y2 = int(y + self.radius * math.sin(end_angle))

                if i % 2 == 0:
                    pygame.draw.line(self.surface, self.color,
                                     (x1, y1), (x2, y2), self.width)
        else:
            pygame.draw.circle(self.surface, self.color, self.pos, self.radius, self.width)

def draw_circles(circles: list[Circle]) -> None:
    for circle in circles:
        circle.draw()

def draw_circle(surface: pygame.SurfaceType, color: pygame.Color,
                pos: pygame.Vector2, radius: int, width: int = 0) -> None:
    Circle(surface, color, pos, radius, width).draw()

def draw_point(surface: pygame.SurfaceType, color: pygame.Color,
               pos: pygame.Vector2) -> None:
    draw_circle(surface, color, pos, 1)

def draw_dashed_circle(surface: pygame.SurfaceType, color: pygame.Color,
                       center: pygame.Vector2, radius: int,
                       dash_length: int = 5, gap_length: int = 5,
                       width: int = 1) -> None:
    Circle(surface, color, center, radius, width,
           True, dash_length, gap_length).draw()
