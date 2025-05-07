import pygame
import math

WIDTH, HEIGHT = 1600, 1600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

for r in range(400):
    for angle in range(0, 360, 5):
        rad = math.radians(angle)
        x = WIDTH // 2 + int(math.cos(rad) * r)
        y = HEIGHT // 2 + int(math.sin(rad) * r)
        hue = int((angle + r) % 360)
        color = pygame.Color(0)
        color.hsva = (hue, 100, 100, 100)
        screen.set_at((x, y), color)

pygame.image.save(screen, "cc_pygame/gen/jpger_74.jpg")
pygame.quit()
