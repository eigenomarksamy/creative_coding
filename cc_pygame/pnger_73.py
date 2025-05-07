import pygame
import math

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill((0, 0, 0))

def draw_branch(x, y, angle, length, depth):
    if depth == 0:
        return
    x2 = x + math.cos(angle) * length
    y2 = y - math.sin(angle) * length
    pygame.draw.line(screen, (150 + depth * 10, 255 - depth * 15, 100), (x, y), (x2, y2), 1)
    draw_branch(x2, y2, angle - 0.3, length * 0.7, depth - 1)
    draw_branch(x2, y2, angle + 0.3, length * 0.7, depth - 1)

draw_branch(WIDTH // 2, HEIGHT - 50, math.pi / 2, 100, 8)
pygame.image.save(screen, "cc_pygame/gen/jpger_73.jpg")
pygame.quit()
