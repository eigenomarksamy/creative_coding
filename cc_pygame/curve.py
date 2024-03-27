import pygame
import sys
import numpy as np
from scipy.interpolate import splprep, splev

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Drawing a Smooth Curve")

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Define your list of points
points = [(100, 200), (200, 100), (300, 300), (400, 200), (500, 400)]

# Convert the points to NumPy array
points_array = np.array(points)

# Perform spline interpolation
tck, u = splprep(points_array.T, s=0.0, per=0)

# Evaluate the spline at a higher resolution
u_new = np.linspace(u.min(), u.max(), 1000)
x_new, y_new = splev(u_new, tck)

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(WHITE)

    # Draw the smooth curve
    for i in range(len(x_new) - 1):
        pygame.draw.line(screen, BLACK, (int(x_new[i]), int(y_new[i])), (int(x_new[i + 1]), int(y_new[i + 1])), 2)

    # Draw the control points
    for point in points:
        pygame.draw.circle(screen, RED, point, 5)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
