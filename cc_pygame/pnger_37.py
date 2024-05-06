import sys
import pygame
from utils.randomization import (generate_random_color,
                                 get_random_pos_on_screen,
                                 get_random_int)
from shapes.pygame_circle import draw_dashed_circle
from shapes.pygame_triangle import draw_triangle
from shapes.pygame_rectangle import draw_quick_rect

def main() -> int:
    pygame.init()
    res = (1600, 1600)
    screen = pygame.display.set_mode(res)
    used_clrs = []
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    screen.fill(color)
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    rect_center = pygame.Vector2(2 * screen.get_width() / 3,
                                 screen.get_height() / 2)
    draw_quick_rect(screen, color, rect_center, screen.get_width() / 3,
                    2 * screen.get_height() / 3)
    draw_quick_rect(screen, color, pygame.Vector2(rect_center.x + 120,
                                                  rect_center.y + 700),
                    screen.get_width() / 6,
                    screen.get_height() / 3)
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    nose_pos1 = pygame.Vector2(screen.get_width() / 3 + 100,
                               2 * screen.get_height() / 3)
    nose_pos2 = pygame.Vector2(nose_pos1.x + 200, nose_pos1.y)
    nose_pos3 = pygame.Vector2(nose_pos2.x, nose_pos2.y - 320)
    draw_triangle(screen, color, [nose_pos1, nose_pos2, nose_pos3])
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    mouth_pos1 = pygame.Vector2(rect_center.x - screen.get_width() / 6,
                                nose_pos2.y + 100)
    mouth_pos2 = pygame.Vector2(mouth_pos1.x, mouth_pos1.y + 200)
    mouth_pos3 = pygame.Vector2(mouth_pos1.x + 300, mouth_pos1.y + 50)
    draw_triangle(screen, color, [mouth_pos1, mouth_pos2, mouth_pos3])
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    eye_pos1 = pygame.Vector2(rect_center.x - screen.get_width() / 6,
                              nose_pos3.y - 100)
    eye_pos2 = pygame.Vector2(eye_pos1.x, eye_pos1.y - 100)
    eye_pos3 = pygame.Vector2(eye_pos1.x + 200, eye_pos1.y - 50)
    draw_triangle(screen, color, [eye_pos1, eye_pos2, eye_pos3])
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    ear_pos1 = pygame.Vector2(rect_center.x + 100, rect_center.y + 150)
    ear_pos2 = pygame.Vector2(ear_pos1.x + 200, ear_pos1.y - 100)
    ear_pos3 = pygame.Vector2(rect_center.x + 150, rect_center.y - 100)
    draw_triangle(screen, color, [ear_pos1, ear_pos2, ear_pos3])
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    hair_center = pygame.Vector2(rect_center.x, rect_center.y - 600)
    draw_quick_rect(screen, color, hair_center, 1.2 * screen.get_width() / 3,
                    screen.get_height() / 6)
    draw_quick_rect(screen, color, pygame.Vector2(hair_center.x + 200,
                                                  hair_center.y + 200),
                    screen.get_width() / 6, screen.get_height() / 3)
    for _ in range(7):
        color = generate_random_color(not_this_color=used_clrs)
        used_clrs.append(color)
        posx, posy = get_random_pos_on_screen(screen, width_bounds=(0, int(screen.get_width() // 3)))
        pos = pygame.Vector2(posx, posy)
        draw_dashed_circle(screen, color, pos, get_random_int(10, 200), width=get_random_int(1, 5))
    pygame.image.save(screen, 'cc_pygame/gen/jpger_37.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
