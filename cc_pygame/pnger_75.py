import pygame
import random

WIDTH, HEIGHT = 1020, 1020
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Create a base pattern
for y in range(HEIGHT):
    for x in range(WIDTH):
        c = (x * y) % 255
        screen.set_at((x, y), (c, 255 - c, c))

# Apply glitch effect
for _ in range(200):
    x = random.randint(0, WIDTH - 100)
    y = random.randint(0, HEIGHT - 10)
    width = random.randint(10, 100)
    height = random.randint(1, 10)
    offset = random.randint(-30, 30)
    part = screen.subsurface((x, y, width, height)).copy()
    screen.blit(part, (x + offset, y))

pygame.image.save(screen, "cc_pygame/gen/jpger_75.jpg")
pygame.quit()
