import sys
import pygame
from typing import Tuple
from utils.randomization import get_random_int
from shapes.pygame_rectangle import draw_quick_square
from shapes.pygame_line import draw_line_cartesian
from shapes.pygame_circle import draw_circle

def draw_cube(screen: pygame.SurfaceType, color: pygame.Color,
              center_pos: pygame.Vector2, side_len: int) -> None:
    co = side_len / 4
    cf = pygame.Vector2(center_pos.x - co, center_pos.y + co)
    cb = pygame.Vector2(center_pos.x + co, center_pos.y - co)
    tlf = pygame.Vector2(cf.x - side_len / 2, cf.y - side_len / 2)
    tlb = pygame.Vector2(cb.x - side_len / 2, cb.y - side_len / 2)
    blf = pygame.Vector2(cf.x - side_len / 2, cf.y + side_len / 2)
    blb = pygame.Vector2(cb.x - side_len / 2, cb.y + side_len / 2)
    brf = pygame.Vector2(cf.x + side_len / 2, cf.y + side_len / 2)
    brb = pygame.Vector2(cb.x + side_len / 2, cb.y + side_len / 2)
    trf = pygame.Vector2(cf.x + side_len / 2, cf.y - side_len / 2)
    trb = pygame.Vector2(cb.x + side_len / 2, cb.y - side_len / 2)
    draw_quick_square(screen, color, cf, side_len, border_width=1)
    draw_quick_square(screen, color, cb, side_len, border_width=1)
    draw_line_cartesian(screen, tlf, tlb, color, 1)
    draw_line_cartesian(screen, blf, blb, color, 1)
    draw_line_cartesian(screen, brf, brb, color, 1)
    draw_line_cartesian(screen, trf, trb, color, 1)

def get_max_area_bounds_of_cube(center_pos: pygame.Vector2,
                                side_len: int) -> Tuple[pygame.Vector2,
                                                        pygame.Vector2,
                                                        pygame.Vector2,
                                                        pygame.Vector2]:
    co = side_len / 4
    cf = pygame.Vector2(center_pos.x - co, center_pos.y + co)
    cb = pygame.Vector2(center_pos.x + co, center_pos.y - co)
    tlb = pygame.Vector2(cb.x - side_len / 2, cb.y - side_len / 2)
    blf = pygame.Vector2(cf.x - side_len / 2, cf.y + side_len / 2)
    brf = pygame.Vector2(cf.x + side_len / 2, cf.y + side_len / 2)
    trb = pygame.Vector2(cb.x + side_len / 2, cb.y - side_len / 2)
    return pygame.Vector2(blf.x, blf.y), pygame.Vector2(blf.x, tlb.y), \
           pygame.Vector2(trb.x, trb.y), pygame.Vector2(trb.x, brf.y)

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    side_len = 100
    rand = get_random_int(1, 65)
    sq_count = 1
    for i in range(100, 1600, 200):
        for j in range(100, 1600, 200):
            if sq_count != rand:
                draw_cube(screen, "white", pygame.Vector2(i, j), side_len)
            else:
                draw_circle(screen, "white", pygame.Vector2(i, j),
                            3 * side_len / 4, 1)
            sq_count += 1
    pygame.image.save(screen, 'cc_pygame/gen/jpger_26.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
