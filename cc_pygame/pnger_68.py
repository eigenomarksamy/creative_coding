import sys
import pygame
from shapes.pygame_line import draw_line_polar
from shapes.pygame_circle import draw_circle
from utils.randomization import generate_random_color_append

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
    width = 2560
    height = 1440
    res = (width, height)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    colors = [screen_color]
    screen.fill(screen_color)
    m = -0.94*height / width
    c = 0.94*height
    for i in range(0, width + 20, 20):
        draw_line_polar(surface=screen, p0=pygame.Vector2(i, 0),
                        length=(m * i + c), angle=90, color="grey80", width=10)
    m *= -1
    c = 0
    for i in range(width, -20, -20):
        draw_line_polar(surface=screen, p0=pygame.Vector2(i, height),
                        length=(m * i + c), angle=-90, color="grey20", width=10)
    r_init = 100
    r_final = 20
    inc = 50
    center = pygame.Vector2(0, height)
    m = -height / width
    c = height
    while True:
        color, colors = generate_random_color_append(colors)
        shades = shade_to_neutral(pygame.Color("gold"), target_color=pygame.Color("black"))
        for i in range(len(shades)):
            shade = shades[i]
            diff = (r_final - r_init) / len(shades)
            r = diff * i + r_init
            draw_circle(screen, shade, pygame.Vector2(center.x, center.y), r)
        center = pygame.Vector2(center.x + inc, m * center.x + c)
        if center.x > screen.get_width() or center.y < 0:
            break
    pygame.image.save(screen, 'cc_pygame/gen/jpger_68.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
