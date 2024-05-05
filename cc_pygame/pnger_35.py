import sys
import random
import pygame
from shapes.pygame_rectangle import draw_quick_square
from shapes.pygame_circle import draw_circle
from shapes.pygame_triangle import draw_equilateral_from_center
from utils.randomization import generate_random_color

def draw_shape_str(surface: pygame.SurfaceType, color: pygame.Color,
                   pos: pygame.Vector2, length: int, shape: str) -> None:
    if shape == "circle":
        draw_circle(surface, color, pos, length / 2)
    elif shape == "triangle":
        draw_equilateral_from_center(surface, color, pos, length, length, angle=random.choice([0, 180]))
    else:
        draw_quick_square(surface, color, pos, length)

def main() -> int:
    pygame.init()
    res = (2080, 2080)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    side_length = 52
    shapes = ["circle", "square", "triangle"]
    screen.fill(screen_color)
    used_colors = [screen_color]
    for posy in range(int(side_length / 2), int(screen.get_height()), side_length):
        for posx in range(int(side_length / 2), int(screen.get_width()), side_length):
            draw = random.choice([True, False, False, True, False])
            color = generate_random_color(not_this_color=used_colors, a=255)
            if draw:
                draw_shape_str(screen, color, pygame.Vector2(posx, posy), side_length, random.choice(shapes))
                used_colors.append(color)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_35.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
