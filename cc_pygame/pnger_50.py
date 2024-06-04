import sys
import pygame
from shapes.pygame_rectangle import draw_quick_square
from shapes.pygame_circle import draw_circle
from shapes.pygame_triangle import draw_equilateral_from_center
from shapes.pygame_line import draw_line_polar
from utils.randomization import generate_random_color_append, get_random_angle, get_random_pos_on_screen, generate_random_color, random

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

def main() -> int:
    pygame.init()
    res = (2040, 2040)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    side_length = 52
    min_side_len = 6
    screen.fill(screen_color)
    used_colors = [screen_color]
    for posy in range(int(side_length / 2), int(screen.get_height() / 2), side_length):
        for posx in range(int(side_length / 2), int(screen.get_width() / 2), side_length):
            color, used_colors = generate_random_color_append(not_this_color=used_colors)
            rev_color = pygame.Color(255 - color.r, 255 - color.g, 255 - color.b)
            shades = shade_to_neutral(color, target_color=rev_color)
            for i in range(len(shades)):
                shade = shades[i]
                diff = (min_side_len - side_length) / len(shades)
                s = diff * i + side_length
                draw_quick_square(screen, shade, pygame.Vector2(posx, posy), s)
    for posy in range(int(screen.get_height() / 2 + side_length / 2), int(screen.get_height()), side_length):
        for posx in range(int(0), int(screen.get_width() / 2), side_length):
            color, used_colors = generate_random_color_append(not_this_color=used_colors)
            rev_color = pygame.Color(255 - color.r, 255 - color.g, 255 - color.b)
            shades = shade_to_neutral(color, target_color=rev_color)
            shades_rev = shade_to_neutral(shade, target_color=color)
            for i in range(len(shades)):
                shade = shades[i]
                diff = (min_side_len - side_length) / len(shades)
                s = diff * i + side_length
                draw_equilateral_from_center(screen, shade, pygame.Vector2(posx, posy), s, s)
            for i in range(len(shades_rev)):
                shade_rev = shades_rev[i]
                diff = (min_side_len - side_length) / len(shades_rev)
                s = diff * i + side_length
                draw_equilateral_from_center(screen, shade_rev, pygame.Vector2(posx + side_length / 2, posy), s, s, angle=180)
    for posy in range(int(side_length / 2), int(screen.get_height() / 2), side_length):
        for posx in range(int(screen.get_width() / 2 + side_length / 2), int(screen.get_width()), side_length):
            color, used_colors = generate_random_color_append(not_this_color=used_colors)
            rev_color = pygame.Color(255 - color.r, 255 - color.g, 255 - color.b)
            shades = shade_to_neutral(color, target_color=rev_color)
            shades_rev = shade_to_neutral(shade, target_color=color)
            for i in range(len(shades)):
                shade = shades[i]
                diff = (min_side_len - side_length) / len(shades)
                s = diff * i + side_length
                draw_equilateral_from_center(screen, shade, pygame.Vector2(posx, posy), s, s, angle=90)
            for i in range(len(shades_rev)):
                shade_rev = shades_rev[i]
                diff = (min_side_len - side_length) / len(shades_rev)
                s = diff * i + side_length
                draw_equilateral_from_center(screen, shade_rev, pygame.Vector2(posx, posy - side_length / 2), s, s, angle=270)
    side_length = side_length // 2
    for posy in range(int(screen.get_height() / 2 + side_length), int(screen.get_height()), side_length * 2):
        for posx in range(int(screen.get_width() / 2 + side_length), int(screen.get_width()), side_length * 2):
            color, used_colors = generate_random_color_append(not_this_color=used_colors)
            rev_color = pygame.Color(255 - color.r, 255 - color.g, 255 - color.b)
            shades = shade_to_neutral(color, target_color=rev_color)
            draw_quick_square(screen, color, pygame.Vector2(posx, posy), side_length * 2)
            for i in range(len(shades)):
                shade = shades[i]
                diff = (min_side_len - side_length) / len(shades)
                s = diff * i + side_length
                draw_circle(screen, shade, pygame.Vector2(posx, posy), s)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_50.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
