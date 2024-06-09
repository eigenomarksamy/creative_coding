import sys
import pygame
from utils.randomization import generate_random_color_append, get_random_int
from shapes.pygame_circle import draw_circle

def shade_to_neutral(color: pygame.Color, max_steps: int = 0,
                     target_color: pygame.Color = pygame.Color("white")) -> list[pygame.Color]:
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

def get_rev_color(color: pygame.Color) -> pygame.Color:
    return pygame.Color(255 - color.r, 255 - color.g, 255 - color.b)

def get_shades_combinations(color1: pygame.Color) -> list[pygame.Color]:
    return [[pygame.Color(f'grey{x}') for x in range(101)],
            shade_to_neutral(pygame.Color("black"), 100, color1),
            shade_to_neutral(pygame.Color("black"), 100, get_rev_color(color1))]

def main() -> int:
    pygame.init()
    res = (2160, 1080)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    radius = 36
    pos = []
    for x in range(radius, screen.get_width(), radius * 2):
        for y in range(radius, screen.get_height(), radius * 2):
            pos.append(pygame.Vector2(x, y))
    color1 = pygame.Color("cornflowerblue")
    color2 = pygame.Color("crimson")
    color3 = pygame.Color("teal")
    colors = [color1, color2, color3]
    shades_list = []
    for color in colors:
        shades_list += get_shades_combinations(color)
    for p in pos:
        selection = get_random_int(0, len(shades_list) - 1)
        for r in range(1, 101, 1):
            draw_circle(screen, shades_list[selection][r], p, radius - r * radius / 100)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_53.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
