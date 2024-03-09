import pygame

class Circle:

    def __init__(self, surface: pygame.SurfaceType, color: pygame.Color,
                 pos: pygame.Vector2, radius: int, width: int = 0) -> None:
        self.surface = surface
        self.color = color
        self.pos = pos
        self.radius = radius
        self.width = width

    def draw(self) -> None:
        pygame.draw.circle(self.surface, self.color, self.pos, self.radius, self.width)

def draw_circles(circles: list[Circle]) -> None:
    for circle in circles:
        circle.draw()