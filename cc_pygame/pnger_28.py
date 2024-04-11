import sys
import pygame
from shapes.pygame_triangle import draw_equilateral_from_center
from utils.randomization import generate_random_color

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    used_colors = [screen_color]
    color = generate_random_color(True, used_colors)
    angle_max = 360
    hb_max = 1000
    for angle in range(0, angle_max, 1):
        for s in range(0, hb_max, 10):
            draw_equilateral_from_center(surface=screen, color=color,
                                        center=pygame.Vector2(x=screen.get_width() / 2,
                                                            y=screen.get_height() / 2),
                                        base=s, height=s,
                                        width=2, angle=angle)
            draw_equilateral_from_center(surface=screen, color=color,
                                        center=pygame.Vector2(x=screen.get_width() / 2,
                                                            y=screen.get_height() / 2),
                                        base=(hb_max-s), height=(hb_max-s),
                                        width=2, angle=(angle_max-angle))
            used_colors.append(color)
            color = generate_random_color(True, used_colors)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_28.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
