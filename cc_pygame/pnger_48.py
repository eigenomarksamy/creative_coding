import sys
import pygame
from utils.randomization import generate_random_color_append
from shapes.pygame_circle import draw_circle
from shapes.pygame_line import draw_line_cartesian

def shade_to_neutral(color: pygame.Color, min_step: int = 1,
                     target_color: pygame.Color = pygame.Color("white")) -> list[pygame.Color]:
    og_r, og_g, og_b = color.r, color.g, color.b
    target_r, target_g, target_b = target_color.r, target_color.g, target_color.b
    diff_r, diff_g, diff_b = target_r - og_r, target_g - og_g, target_b - og_b
    max_diff = max(abs(diff_r), abs(diff_g), abs(diff_b))
    if max_diff == 0:
        return [color]
    num_steps = max(1, max_diff // min_step)
    colors = []
    for step in range(num_steps + 1):
        t = step / num_steps
        new_r = int(og_r + t * diff_r)
        new_g = int(og_g + t * diff_g)
        new_b = int(og_b + t * diff_b)
        new_color = pygame.Color(new_r, new_g, new_b)
        colors.append(new_color)
    return colors

def draw_shaded_circles(screen, colors, start_pos, spacing, radius):
    x, y = start_pos
    for color in colors:
        pygame.draw.circle(screen, color, (x, y), radius)
        x += spacing

def main() -> int:
    pygame.init()
    res = (7200, 4800)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    used_colors = [screen_color]
    r_init = 800
    r_final = 200
    for x in range(0, screen.get_width() + 400, 800):
        for y in range(0, screen.get_height() + 400, 800):
            color, used_colors = generate_random_color_append(not_this_color=used_colors)
            shades = shade_to_neutral(color)
            for i in range(len(shades)):
                shade = shades[i]
                diff = (r_final - r_init) / len(shades)
                r = diff * i + r_init
                draw_circle(screen, shade, pygame.Vector2(x, y), r)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_48.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
