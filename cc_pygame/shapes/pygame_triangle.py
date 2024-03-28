import pygame

class Triangle:
    def __init__(self, surface: pygame.Surface, color: pygame.Color,
                 points: list[pygame.Vector2], width: int = 0) -> None:
        self.surface = surface
        self.color = color
        self.points = points
        self.width = width

    def draw(self) -> None:
        pygame.draw.polygon(self.surface, self.color, self.points, self.width)

def draw_triangle(surface: pygame.SurfaceType, color: pygame.Color,
                  points: list[pygame.Vector2], width: int = 0) -> None:
    Triangle(surface, color, points, width).draw()
