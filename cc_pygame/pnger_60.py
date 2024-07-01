import sys
import math
import pygame
from shapes.pygame_shape import draw_object
from utils.randomization import generate_random_color_append

def shade_to_neutral(color: pygame.Color,
                     target_color: pygame.Color,
                     max_steps: int = 0) -> list[pygame.Color]:
    og_r, og_g, og_b = color.r, color.g, color.b
    target_r, target_g, target_b = target_color.r, target_color.g, target_color.b
    diff_r, diff_g, diff_b = target_r - og_r, target_g - og_g, target_b - og_b
    max_diff = max(abs(diff_r), abs(diff_g), abs(diff_b))
    if max_diff == 0:
        return [color]
    num_steps = max_diff
    if max_steps != 0:
        num_steps = min(max_steps, num_steps)
    colors = []
    for step in range(num_steps + 1):
        t = step / num_steps
        new_r = int(og_r + t * diff_r)
        new_g = int(og_g + t * diff_g)
        new_b = int(og_b + t * diff_b)
        new_color = pygame.Color(new_r, new_g, new_b)
        colors.append(new_color)
    return colors

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
    colors_list = [pygame.Color("cornflowerblue"),
                   pygame.Color("crimson"),
                   pygame.Color("teal")]
    color_idx = 0
    for xpos in range(int(screen.get_width() / 4),
                      int(screen.get_width()),
                      int(screen.get_width() / 4)):
        for ypos in range(int(screen.get_height() / 4),
                          int(screen.get_height()),
                          int(screen.get_height() / 4)):
            shades = shade_to_neutral(colors_list[color_idx],
                                      pygame.Color("black"), 20)
            for i in range(200, 0, -10):
                color, used_colors = generate_random_color_append(used_colors)
                draw_octagon(screen, shades[i // 10],
                             pygame.Vector2(xpos, ypos),
                             i, angle=i, width=2)
        if color_idx < 3:
            color_idx += 1
        else:
            color_idx = 0
    pygame.image.save(screen, 'cc_pygame/gen/jpger_60.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
