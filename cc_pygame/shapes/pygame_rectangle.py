import math
import pygame

class Square:
    def __init__(self, surface: pygame.SurfaceType, color: pygame.Color,
                 pos: pygame.Vector2, side_length: int,
                 angle: float = 0, width: int = 0) -> None:
        self.surface = surface
        self.color = color
        self.pos = pos
        self.side_length = side_length
        self.angle = angle
        self.width = width

    def draw(self) -> None:
        rotated_square = pygame.Surface((self.side_length, self.side_length), pygame.SRCALPHA)
        pygame.draw.rect(rotated_square, self.color, (0, 0, self.side_length, self.side_length), self.width)
        rotated_square = pygame.transform.rotate(rotated_square, self.angle)
        rotated_rect = rotated_square.get_rect(center=self.pos)
        self.surface.blit(rotated_square, rotated_rect.topleft)
