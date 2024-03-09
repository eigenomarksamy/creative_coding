import random
import pygame

class Circle:

    def __init__(self, surface: pygame.SurfaceType, color: str,
                 pos: pygame.Vector2, radius: int) -> None:
        self.surface = surface
        self.color = color
        self.pos = pos
        self.radius = radius

def draw(circles: list[Circle]) -> None:
    for circle in circles:
        pygame.draw.circle(circle.surface, circle.color, circle.pos, circle.radius)

def draw_simple_flower(circles: list[Circle], center_pos_w: int, center_pos_h: int, radius: int, color: str) -> None:
    circles.append(Circle(screen, color, pygame.Vector2(center_pos_w, center_pos_h), radius))
    circles.append(Circle(screen, color, pygame.Vector2(center_pos_w - radius, center_pos_h - radius), radius))
    circles.append(Circle(screen, color, pygame.Vector2(center_pos_w + radius, center_pos_h + radius), radius))
    circles.append(Circle(screen, color, pygame.Vector2(center_pos_w + radius, center_pos_h - radius), radius))
    circles.append(Circle(screen, color, pygame.Vector2(center_pos_w - radius, center_pos_h + radius), radius))
    draw(circles)

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
circles = []
iterations = 0
max_iterations = 35
colors = ["white", "crimson", "teal", "cyan", "violet", "indigo", "orange", "red", "yellow", "green", "grey"]
screen.fill("black")
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if iterations < max_iterations:
        random_width = random.randint(75, screen.get_width() - 75)
        random_height = random.randint(75, screen.get_height() - 75)
        random_color = colors[random.randint(0, len(colors) - 1)]
        draw_simple_flower(circles, random_width, random_height, 50, random_color)
        iterations += 1
    pygame.display.flip()
    clock.tick(60)
pygame.quit()