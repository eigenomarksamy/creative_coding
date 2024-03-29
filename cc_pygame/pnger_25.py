import sys
import pygame
import numpy as np

def mandelbrot(c, max_iter):
    z = c
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return max_iter

def render_mandelbrot(xmin, xmax, ymin, ymax, width, height, max_iter):
    pixels = np.zeros((width, height))
    for x in range(width):
        for y in range(height):
            zx, zy = x * (xmax - xmin) / (width - 1) + xmin, y * (ymax - ymin) / (height - 1) + ymin
            c = zx + zy * 1j
            pixels[x, y] = mandelbrot(c, max_iter)
    return pixels

def main() -> int:
    pygame.init()
    res = (800, 800)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    pixels = render_mandelbrot(-2, 1, -1.5, 1.5, screen.get_width(),
                               screen.get_height(), 256)
    pixel_array = np.array(pixels, dtype=np.uint8)
    surface = pygame.surfarray.make_surface(pixel_array)
    pygame.image.save(surface, 'cc_pygame/gen/jpger_25.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
