import sys
import math
import pygame
from shapes.pygame_shape import draw_object
from utils.randomization import generate_random_color

def draw_octagon(surface: pygame.SurfaceType, color: pygame.Color,
                 center: pygame.Vector2, side_length: int, width: int = 0,
                 angle: float = 0) -> None:
    points = []
    for _ in range(8):
        x_i = center.x + side_length * math.cos(math.radians(angle))
        y_i = center.y - side_length * math.sin(math.radians(angle))
        points.append(pygame.Vector2(x_i, y_i))
        angle += 45
    draw_object(surface, points, color, width)

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    for i in range(800, 0, -100):
        draw_octagon(screen, f"grey{100 - i//10}", pygame.Vector2(screen.get_width() / 2,
                                                screen.get_height() / 2), i,
                                                angle=0, width=10)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_57.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
