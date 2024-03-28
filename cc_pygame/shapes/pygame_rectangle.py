import pygame

class Rectangle:
    def __init__(self, surface: pygame.SurfaceType, color: pygame.Color,
                 pos: pygame.Vector2, width: int, height: int,
                 angle: float = 0, border_width: int = 0) -> None:
        self.surface = surface
        self.color = color
        self.pos = pos
        self.width = width
        self.height = height
        self.angle = angle
        self.border_width = border_width

    def draw(self) -> None:
        rotated_rect = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(rotated_rect, self.color, (0, 0, self.width, self.height),
                         self.border_width)
        rotated_rect = pygame.transform.rotate(rotated_rect, self.angle)
        rotated_rect_rect = rotated_rect.get_rect(center=self.pos)
        self.surface.blit(rotated_rect, rotated_rect_rect.topleft)

class Square(Rectangle):
    def __init__(self, surface: pygame.SurfaceType, color: pygame.Color,
                 pos: pygame.Vector2, side_length: int,
                 angle: float = 0, border_width: int = 0) -> None:
        super().__init__(surface, color, pos, side_length, side_length,
                         angle, border_width)

def draw_quick_rect(surface: pygame.SurfaceType, color: pygame.Color,
                    pos: pygame.Vector2, width: int, height: int,
                    angle: float = 0, border_width: int = 0) -> None:
    Rectangle(surface, color, pos, width, height, angle, border_width).draw()
