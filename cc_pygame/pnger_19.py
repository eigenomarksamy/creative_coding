import sys
import pygame
from squares import draw_nested_angle_alternating_squares


def main() -> int:
    pygame.init()
    res = (1000, 1000)
    side_length = 1000
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    draw_nested_angle_alternating_squares(surface=screen,
                                            center_pos_x=screen.get_width() / 2,
                                            center_pos_y=screen.get_height() / 2,
                                            color="midnightblue",
                                            secondary_color="cornflowerblue",
                                            init_side_len=side_length, num=50,
                                            angle1=45)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_19.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
