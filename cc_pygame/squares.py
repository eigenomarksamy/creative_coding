import pygame

class Square:
    def __init__(self, surface: pygame.SurfaceType, color: str, pos: pygame.Vector2, side_length: int, angle: float = 0) -> None:
        self.surface = surface
        self.color = color
        self.pos = pos
        self.side_length = side_length
        self.angle = angle

    def rotate(self, angle: float) -> None:
        self.angle += angle
        rotated_surface = pygame.transform.rotate(self.surface, self.angle)
        self.surface = pygame.Surface((self.side_length, self.side_length), pygame.SRCALPHA)
        self.surface.blit(rotated_surface, (0, 0))

def draw(squares: list[Square]) -> None:
    for square in squares:
        rotated_square = pygame.transform.rotate(square.surface, square.angle)
        rotated_rect = rotated_square.get_rect(center=square.pos)
        screen.blit(rotated_square, rotated_rect.topleft)

def draw_square_in_center(squares: list[Square], screen_width: int, screen_height: int, side_length: int) -> None:
    center_x = screen_width // 2
    center_y = screen_height // 2
    square_surface = pygame.Surface((side_length, side_length), pygame.SRCALPHA)
    pygame.draw.rect(square_surface, (255, 255, 255, 128), (0, 0, side_length, side_length))  # Fills the square with semi-transparent white color
    squares.append(Square(square_surface, "white", pygame.Vector2(center_x, center_y), side_length))
    draw(squares)

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
running = True

squares = []  # Create the list of squares
screen.fill("black")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw a rotating square in the center of the screen with side length 50
    draw_square_in_center(squares, screen.get_width(), screen.get_height(), 50)
    squares[0].rotate(1)  # Rotate the square by 1 degree on each iteration

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
