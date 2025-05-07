import pygame
import random
import noise
import math

WIDTH, HEIGHT = 800, 800
NUM_PARTICLES = 1000
BG_COLOR = (10, 10, 10)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(BG_COLOR)

class Particle:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.color = (255, 255, 255)

    def update(self):
        angle = noise.pnoise2(self.x * 0.002, self.y * 0.002) * 10
        self.x += math.cos(angle)
        self.y += math.sin(angle)
        if 0 < self.x < WIDTH and 0 < self.y < HEIGHT:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 1)

particles = [Particle() for _ in range(NUM_PARTICLES)]
for _ in range(200):
    for p in particles:
        p.update()

pygame.image.save(screen, "cc_pygame/gen/jpger_72.jpg")
pygame.quit()
