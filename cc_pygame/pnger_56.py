import sys
import pygame
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

def draw_shades(screen: pygame.SurfaceType, shades: list[pygame.Color],
                radius: int, y_pos: float, is_rev: bool) -> None:
    if not is_rev:
        for i in range(len(shades)):
            shade = shades[i]
            pos = pygame.Vector2(100 + (i * 8) / 2, y_pos)
            draw_circle(screen, shade, pos, radius)
    else:
        for i in range(len(shades)):
            shade = shades[i]
            pos = pygame.Vector2(screen.get_width() - 100 - (i * 8) / 2, y_pos)
            draw_circle(screen, shade, pos, radius)

def draw_on_const_y(screen: pygame.SurfaceType, start_color: pygame.Color,
                    radius: int, const_posy: float) -> None:
    shades = shade_to_neutral(start_color, target_color=pygame.Color("black"))
    draw_shades(screen, shades, radius, const_posy, False)
    shades = shade_to_neutral(pygame.Color("black"), target_color=start_color)
    draw_shades(screen, shades, radius, const_posy, True)
    # draw_circle(screen, "black", pygame.Vector2(screen.get_width() / 2, const_posy), radius)

def main() -> int:
    pygame.init()
    res = (2048, 1080)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    radius = 64
    for posy in range(radius // 2, screen.get_height() + 4 * radius, 4 * radius):
        draw_on_const_y(screen, pygame.Color("palegoldenrod"), radius, posy - 1.75 * radius)
        draw_on_const_y(screen, pygame.Color("crimson"), radius, posy - 1.5 * radius)
        draw_on_const_y(screen, pygame.Color("palegoldenrod"), radius, posy - 1.25 * radius)
        draw_on_const_y(screen, pygame.Color("crimson"), radius, posy - radius)
        draw_on_const_y(screen, pygame.Color("palegoldenrod"), radius, posy - 0.75 * radius)
        draw_on_const_y(screen, pygame.Color("crimson"), radius, posy - radius // 2)
        draw_on_const_y(screen, pygame.Color("palegoldenrod"), radius, posy)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_56.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
