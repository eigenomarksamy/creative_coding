import sys
import pygame
from utils.randomization import generate_random_color

def main() -> int:
    pygame.init()
    res = (2880, 2880)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    s = 0
    while s <= screen.get_width():
        pygame.draw.line(screen, generate_random_color(True), pygame.Vector2(s, 0), pygame.Vector2(screen.get_width() - s, screen.get_height()), 30)
        s += 40
    s = 0
    while s <= screen.get_height():
        pygame.draw.line(screen, generate_random_color(True), pygame.Vector2(0, s), pygame.Vector2(screen.get_width(), screen.get_height() - s), 30)
        s += 40
    s = screen.get_height() / 2
    while s >= 0:
        pygame.draw.circle(screen, generate_random_color(True), pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2), s)
        pygame.draw.circle(screen, "black", pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2), s - 30)
        s -= 40
    pygame.image.save(screen, 'cc_pygame/gen/jpger_07.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())