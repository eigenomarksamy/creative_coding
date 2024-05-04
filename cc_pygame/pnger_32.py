import sys
import pygame
from shapes.pygame_rectangle import draw_quick_square
from utils.randomization import generate_random_color

# def main() -> int:
#     pygame.init()
#     res = (2040, 2040)
#     screen = pygame.display.set_mode(res)
#     screen_color = "black"
#     side_length = 51
#     screen.fill(screen_color)
#     # used_colors = [screen_color]
#     for posy in range(int(side_length / 2), int(screen.get_height()), side_length):
#         r = 0
#         g = 0
#         b = 0
#         for posx in range(int(side_length / 2), int(screen.get_width()), side_length):
#             color = pygame.Color(r, g, b, 100)
#             draw_quick_square(screen, color, pygame.Vector2(posx, posy), side_length)
#             r += 5
#             g += 5
#             b += 5
#             # used_colors.append(color)
#     posx = side_length / 2
#     posy = side_length / 2
#     while posx < screen.get_width() and posy < screen.get_height():
#         # color = generate_random_color(used_colors)
#         color = pygame.Color(r, g, b, 100)
#         draw_quick_square(screen, color, pygame.Vector2(posx, posy), side_length)
#         # used_colors.append(color)
#         posx += (side_length)
#         posy += (side_length)
#         r -= 5
#         g -= 5
#         b -= 5
#     pygame.image.save(screen, 'cc_pygame/gen/jpger_32.jpg')
#     pygame.quit()
#     return 0

def main() -> int:
    pygame.init()
    res = (2040, 2040)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    side_length = 51
    screen.fill(screen_color)
    used_colors = [screen_color]
    for posy in range(int(side_length / 2), int(screen.get_height()), side_length):
        for posx in range(int(side_length / 2), int(screen.get_width()), side_length):
            color = generate_random_color(not_this_color=used_colors, a=255)
            draw_quick_square(screen, color, pygame.Vector2(posx, posy), side_length)
            used_colors.append(color)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_32.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
