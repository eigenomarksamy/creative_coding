import sys
import pygame

def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def main() -> int:
    pygame.init()
    res = (3000, 3000)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    for x in range(0, screen.get_width()):
        for y in range(0, screen.get_height()):
            if is_prime(x) and is_prime(y):
                color = pygame.Color("white")
            else:
                color = pygame.Color(screen_color)
            screen.set_at((x, y), color)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_78.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
