import pygame
import math

# Setup
WIDTH, HEIGHT = 800, 800
BG_COLOR = (10, 10, 10)
CIRCLE_COLOR = (200, 200, 255)

def draw_recursive_circles(surface, x, y, radius, depth):
    if depth == 0 or radius < 2:
        return
    pygame.draw.circle(surface, CIRCLE_COLOR, (int(x), int(y)), int(radius), 1)
    # Draw four smaller circles around this one
    for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
        dx = math.cos(angle) * radius
        dy = math.sin(angle) * radius
        draw_recursive_circles(surface, x + dx, y + dy, radius / 2, depth - 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(BG_COLOR)

    draw_recursive_circles(screen, WIDTH // 2, HEIGHT // 2, 200, 5)

    pygame.image.save(screen, "cc_pygame/gen/jpger_71.jpg")

    pygame.quit()

if __name__ == "__main__":
    main()
