import sys
import pygame
from shapes.pygame_rectangle import draw_quick_rect
from shapes.pygame_triangle import draw_triangle, draw_equilateral_from_center
from utils.randomization import (get_random_int,
                                 generate_random_color,
                                 get_random_pos_on_screen,
                                 get_random_int_list)

def main() -> int:
    pygame.init()
    res = (2880, 1440)
    screen = pygame.display.set_mode(res)
    screen_color = "grey40"
    screen.fill(screen_color)
    tri_points_quads = [
        [
            [pygame.Vector2(0, 0),
            pygame.Vector2(screen.get_width() / 4, screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, 0)],
            [pygame.Vector2(0, 0),
            pygame.Vector2(screen.get_width() / 4, screen.get_height() / 4),
            pygame.Vector2(0, screen.get_height() / 2)],
            [pygame.Vector2(0, screen.get_height() / 2),
            pygame.Vector2(screen.get_width() / 4, screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)],
            [pygame.Vector2(screen.get_width() / 2, 0),
            pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2),
            pygame.Vector2(screen.get_width() / 4, screen.get_height() / 4)]
        ],
        [
            [pygame.Vector2(screen.get_width() / 2, 0),
            pygame.Vector2(3 * screen.get_width() / 4, screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)],
            [pygame.Vector2(screen.get_width(), 0),
            pygame.Vector2(3 * screen.get_width() / 4, screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, 0)],
            [pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2),
            pygame.Vector2(3 * screen.get_width() / 4, screen.get_height() / 4),
            pygame.Vector2(screen.get_width(), screen.get_height() / 2)],
            [pygame.Vector2(screen.get_width(), 0),
            pygame.Vector2(screen.get_width(), screen.get_height() / 2),
            pygame.Vector2(3 * screen.get_width() / 4, screen.get_height() / 4)]
        ],
        [
            [pygame.Vector2(0, screen.get_height() / 2),
            pygame.Vector2(screen.get_width() / 4, 3 * screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)],
            [pygame.Vector2(0, screen.get_height() / 2),
            pygame.Vector2(screen.get_width() / 4, 3 * screen.get_height() / 4),
            pygame.Vector2(0, screen.get_height())],
            [pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2),
            pygame.Vector2(screen.get_width() / 4, 3 * screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, screen.get_height())],
            [pygame.Vector2(0, screen.get_height()),
            pygame.Vector2(screen.get_width() / 2, screen.get_height()),
            pygame.Vector2(screen.get_width() / 4, 3 * screen.get_height() / 4)]
        ],
        [
            [pygame.Vector2(screen.get_width(), screen.get_height() / 2),
            pygame.Vector2(3 * screen.get_width() / 4, 3 * screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)],
            [pygame.Vector2(screen.get_width(), screen.get_height() / 2),
            pygame.Vector2(3 * screen.get_width() / 4, 3 * screen.get_height() / 4),
            pygame.Vector2(screen.get_width(), screen.get_height())],
            [pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2),
            pygame.Vector2(3 * screen.get_width() / 4, 3 * screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, screen.get_height())],
            [pygame.Vector2(screen.get_width(), screen.get_height()),
            pygame.Vector2(screen.get_width() / 2, screen.get_height()),
            pygame.Vector2(3 * screen.get_width() / 4, 3 * screen.get_height() / 4)]
        ]
    ]
    used_colors = [screen_color]
    for tpq in tri_points_quads:
        for tp in tpq:
            color = generate_random_color(not_this_color=used_colors)
            used_colors.append(color)
            # draw_triangle(screen, color, tp)
    tri_points = [
        [
            [pygame.Vector2(0, 0),
            pygame.Vector2(screen.get_width() / 4, screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, 0)],
            [pygame.Vector2(0, screen.get_height() / 2),
            pygame.Vector2(screen.get_width() / 4, screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)]
        ],
        [
            [pygame.Vector2(screen.get_width() / 2, 0),
            pygame.Vector2(3 * screen.get_width() / 4, screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)],
            [pygame.Vector2(screen.get_width(), 0),
            pygame.Vector2(screen.get_width(), screen.get_height() / 2),
            pygame.Vector2(3 * screen.get_width() / 4, screen.get_height() / 4)]
        ],
        [
            [pygame.Vector2(0, screen.get_height() / 2),
            pygame.Vector2(screen.get_width() / 4, 3 * screen.get_height() / 4),
            pygame.Vector2(0, screen.get_height())],
            [pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2),
            pygame.Vector2(screen.get_width() / 4, 3 * screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, screen.get_height())]
        ],
        [
            [pygame.Vector2(screen.get_width(), screen.get_height() / 2),
            pygame.Vector2(3 * screen.get_width() / 4, 3 * screen.get_height() / 4),
            pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)],
            [pygame.Vector2(screen.get_width(), screen.get_height()),
            pygame.Vector2(screen.get_width() / 2, screen.get_height()),
            pygame.Vector2(3 * screen.get_width() / 4, 3 * screen.get_height() / 4)]
        ]
    ]
    for tpq in tri_points:
        for tp in tpq:
            draw_triangle(screen, "grey60", tp)
    # draw_quick_rect(screen, "grey", pygame.Vector2(screen.get_width() / 4,
    #                                                screen.get_height() / 4),
    #                 screen.get_width() / 2, screen.get_height() / 2,
    #                 border_width=10)
    # draw_quick_rect(screen, "grey", pygame.Vector2(screen.get_width() / 4,
    #                                                3 * screen.get_height() / 4),
    #                 screen.get_width() / 2, screen.get_height() / 2,
    #                 border_width=10)
    # draw_quick_rect(screen, "grey", pygame.Vector2(3 * screen.get_width() / 4,
    #                                                screen.get_height() / 4),
    #                 screen.get_width() / 2, screen.get_height() / 2,
    #                 border_width=10)
    # draw_quick_rect(screen, "grey", pygame.Vector2(3 * screen.get_width() / 4,
    #                                                3 * screen.get_height() / 4),
    #                 screen.get_width() / 2, screen.get_height() / 2,
    #                 border_width=10)
    # draw_line_cartesian(screen, pygame.Vector2(0, screen.get_height() / 2),
    #                     pygame.Vector2(screen.get_width() / 2, 0), "grey", 10)
    # draw_line_cartesian(screen, pygame.Vector2(0, screen.get_height() / 2),
    #                     pygame.Vector2(screen.get_width() / 2,
    #                                    screen.get_height()), "grey", 10)
    # draw_line_cartesian(screen, pygame.Vector2(screen.get_width(),
    #                                            screen.get_height() / 2),
    #                     pygame.Vector2(screen.get_width() / 2, 0), "grey", 10)
    # draw_line_cartesian(screen, pygame.Vector2(screen.get_width(),
    #                                            screen.get_height() / 2),
    #                     pygame.Vector2(screen.get_width() / 2,
    #                                    screen.get_height()), "grey", 10)
    # draw_line_cartesian(screen, pygame.Vector2(0, 0),
    #                     pygame.Vector2(screen.get_width(),
    #                                    screen.get_height()), "grey", 10)
    # draw_line_cartesian(screen, pygame.Vector2(0, screen.get_height()),
    #                     pygame.Vector2(screen.get_width(), 0), "grey", 10)
    for _ in range(get_random_int(20, 1000)):
        posx, posy = get_random_pos_on_screen(screen)
        posv = pygame.Vector2(posx, posy)
        draw_quick_rect(screen, f"grey{get_random_int(40, 60)}", posv, get_random_int(40, 60),
                        get_random_int(40, 60), border_width=get_random_int(0, 2))
        posx, posy = get_random_pos_on_screen(screen)
        posv = pygame.Vector2(posx, posy)
        draw_equilateral_from_center(screen, f"grey{get_random_int(40, 60)}", posv,
                                     get_random_int(40, 60), get_random_int(40, 60),
                                     get_random_int(0, 2), get_random_int_list([0, 90, 180, 270]))
        # draw_circle(screen, f"grey{get_random_int(40, 60)}", posv, get_random_int(40, 60),
        #             get_random_int(0, 2))
    pygame.image.save(screen, 'cc_pygame/gen/jpger_41.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
