import sys
import pygame
from shapes.pygame_circle import draw_point

def draw_sierpinski(screen: pygame.SurfaceType, color: pygame.Color,
                    depth: int, vertices: list[tuple[int]]) -> None:
    if depth == 0:
        draw_point(screen, color, pygame.Vector2(vertices[0][0], vertices[0][1]))
    else:
        midpoints = [
            ((vertices[0][0] + vertices[1][0]) // 2,
             (vertices[0][1] + vertices[1][1]) // 2),
            ((vertices[1][0] + vertices[2][0]) // 2,
             (vertices[1][1] + vertices[2][1]) // 2),
            ((vertices[0][0] + vertices[2][0]) // 2,
             (vertices[0][1] + vertices[2][1]) // 2)
        ]
        draw_sierpinski(screen, color, depth - 1, [vertices[0], midpoints[0], midpoints[2]])
        draw_sierpinski(screen, color, depth - 1, [midpoints[0], vertices[1], midpoints[1]])
        draw_sierpinski(screen, color, depth - 1, [midpoints[2], midpoints[1], vertices[2]])

def main() -> int:
    pygame.init()
    res = (1000, 1000)
    screen = pygame.display.set_mode(res)
    screen_color = "white"
    screen.fill(screen_color)
    vertices = [(screen.get_width() // 2, 100),
                (100, screen.get_height() - 100),
                (screen.get_width() - 100,
                 screen.get_height() - 100)]
    depth = 12
    draw_sierpinski(screen, "black", depth, vertices)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_20.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
