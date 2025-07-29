import sys
import pygame
from utils.randomization import generate_random_color_append

def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def main() -> int:
    pygame.init()
    res = (1200, 1200)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    colors = [screen_color]
    li = []
    for x in range(0, screen.get_width()):
        for y in range(0, screen.get_height()):
            if is_prime(x) and is_prime(y):
                li.append((x, y))
    for i in range(len(li)):
        if is_prime(i):
            color, colors = generate_random_color_append(not_this_color=colors, pre_set_a=True, a=255)
            screen.set_at(li[i], color)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_79.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
