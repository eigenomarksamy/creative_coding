import sys
import pygame
from squares import draw_nested_angle_alternating_squares


def main() -> int:
    pygame.init()
    res = (720, 720)
    side_length = 700
    screen = pygame.display.set_mode(res)
    clock = pygame.time.Clock()
    running = True
    screen_color = "black"
    screen.fill(screen_color)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw_nested_angle_alternating_squares(surface=screen,
                                              center_pos_x=screen.get_width() / 2,
                                              center_pos_y=screen.get_height() / 2,
                                              color="midnightblue",
                                              secondary_color="cornflowerblue",
                                              init_side_len=side_length, num=50,
                                              angle1=45)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())