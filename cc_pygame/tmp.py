import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the screen
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Drawing Lines")

# Set up colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Main loop
running = True
points = []
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if len(points) < 2:  # Allow drawing lines between two points
                points.append(event.pos)

    # Clear the screen
    screen.fill(WHITE)

    # Draw lines between points
    if len(points) == 2:
        pygame.draw.line(screen, BLACK, points[0], points[1], 5)  # Draw a line between the two points

    # Draw points
    for point in points:
        pygame.draw.circle(screen, BLACK, point, 5)  # Draw a small circle at each point

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
