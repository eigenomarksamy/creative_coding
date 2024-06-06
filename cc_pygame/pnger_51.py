import sys
import pygame
from utils.randomization import generate_random_color_append
from shapes.pygame_line import draw_line_polar

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

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    color, _ = generate_random_color_append()
    color = pygame.Color("crimson")
    screen.fill(color)
    p_list = []
    for i in range(0, max(screen.get_width(), screen.get_height()), 100):
        p_list.append(pygame.Vector2(i, i))
    shades = shade_to_neutral(get_rev_color(color), max_steps=50, target_color=pygame.Color("black"))
    shades1 = shade_to_neutral(get_rev_color(color), max_steps=50, target_color=pygame.Color("white"))
    for p in p_list:
        for i in range(len(shades)):
            draw_line_polar(screen, pygame.Vector2(p.x + i * 5, p.y + i), 800 - 10 * i, 0, shades[len(shades) - 1 - i], 1)
            draw_line_polar(screen, pygame.Vector2(p.x + i * 5, p.y - i), 800 - 10 * i, 0, shades[len(shades) - 1 - i], 1)
        for i in range(len(shades1)):
            draw_line_polar(screen, pygame.Vector2(p.x + i, p.y + i * 5), 800 - 10 * i, 90, shades1[len(shades1) - 1 - i], 1)
            draw_line_polar(screen, pygame.Vector2(p.x - i, p.y + i * 5), 800 - 10 * i, 90, shades1[len(shades1) - 1 - i], 1)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_51.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
