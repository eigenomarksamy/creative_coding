import sys
import math
import pygame
from shapes.pygame_shape import draw_object
from utils.randomization import generate_random_color_append

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
    used_colors = [screen_color]
    for xpos in range(int(screen.get_width() / 4),
                      int(screen.get_width()),
                      int(screen.get_width() / 4)):
        for ypos in range(int(screen.get_height() / 4),
                          int(screen.get_height()),
                          int(screen.get_height() / 4)):
            for i in range(200, 0, -10):
                color, used_colors = generate_random_color_append(used_colors)
                draw_octagon(screen, color, pygame.Vector2(xpos, ypos), i,
                             angle=0, width=2)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_59.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
