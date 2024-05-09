import sys
import pygame
from utils.randomization import (generate_random_color,
                                 get_random_pos_on_screen,
                                 get_random_int)
from shapes.pygame_circle import draw_circle
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
    def_width = 8
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    rect_center = pygame.Vector2(3 * screen.get_width() / 4 + 20,
                                 screen.get_height() / 2)
    draw_quick_rect(screen, color, rect_center, screen.get_width() / 3,
                    2 * screen.get_height() / 3)
    inv_rect = pygame.Vector2(screen.get_width() - rect_center.x, rect_center.y)
    draw_quick_rect(screen, color, inv_rect, screen.get_width() / 3,
                    2 * screen.get_height() / 3, border_width=def_width)
    draw_quick_rect(screen, color, pygame.Vector2(rect_center.x + 120,
                                                  rect_center.y + 700),
                    screen.get_width() / 6,
                    screen.get_height() / 3)
    draw_quick_rect(screen, color, pygame.Vector2(inv_rect.x - 120,
                                                  inv_rect.y + 700),
                    screen.get_width() / 6,
                    screen.get_height() / 3, border_width=def_width)
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    nose_pos1 = pygame.Vector2(rect_center.x - 400, rect_center.y + 100)
    nose_pos2 = pygame.Vector2(nose_pos1.x + 200, nose_pos1.y)
    nose_pos3 = pygame.Vector2(nose_pos2.x, nose_pos2.y - 320)
    inv_nose_pos1 = pygame.Vector2(screen.get_width() - nose_pos1.x, nose_pos1.y)
    inv_nose_pos2 = pygame.Vector2(screen.get_width() - nose_pos2.x, nose_pos2.y)
    inv_nose_pos3 = pygame.Vector2(screen.get_width() - nose_pos3.x, nose_pos3.y)
    draw_triangle(screen, color, [nose_pos1, nose_pos2, nose_pos3])
    draw_triangle(screen, color, [inv_nose_pos1, inv_nose_pos2, inv_nose_pos3], def_width)
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    mouth_pos1 = pygame.Vector2(rect_center.x - screen.get_width() / 6,
                                nose_pos2.y + 100)
    mouth_pos2 = pygame.Vector2(mouth_pos1.x, mouth_pos1.y + 200)
    mouth_pos3 = pygame.Vector2(mouth_pos1.x + 300, mouth_pos1.y + 50)
    inv_mouth_pos1 = pygame.Vector2(screen.get_width() - mouth_pos1.x, mouth_pos1.y)
    inv_mouth_pos2 = pygame.Vector2(screen.get_width() - mouth_pos2.x, mouth_pos2.y)
    inv_mouth_pos3 = pygame.Vector2(screen.get_width() - mouth_pos3.x, mouth_pos3.y)
    draw_triangle(screen, color, [mouth_pos1, mouth_pos2, mouth_pos3])
    draw_triangle(screen, color, [inv_mouth_pos1, inv_mouth_pos2, inv_mouth_pos3], def_width)
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    eye_pos1 = pygame.Vector2(rect_center.x - screen.get_width() / 6,
                              nose_pos3.y - 65)
    eye_pos2 = pygame.Vector2(eye_pos1.x, eye_pos1.y - 100)
    eye_pos3 = pygame.Vector2(eye_pos1.x + 200, eye_pos1.y - 50)
    inv_eye_pos1 = pygame.Vector2(screen.get_width() - eye_pos1.x, eye_pos1.y)
    inv_eye_pos2 = pygame.Vector2(screen.get_width() - eye_pos2.x, eye_pos2.y)
    inv_eye_pos3 = pygame.Vector2(screen.get_width() - eye_pos3.x, eye_pos3.y)
    draw_triangle(screen, color, [eye_pos1, eye_pos2, eye_pos3])
    draw_triangle(screen, color, [inv_eye_pos1, inv_eye_pos2, inv_eye_pos3], def_width)
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    ear_pos1 = pygame.Vector2(rect_center.x + 100, rect_center.y + 150)
    ear_pos2 = pygame.Vector2(ear_pos1.x + 200, ear_pos1.y - 100)
    ear_pos3 = pygame.Vector2(rect_center.x + 150, rect_center.y - 100)
    inv_ear_pos1 = pygame.Vector2(screen.get_width() - ear_pos1.x, ear_pos1.y)
    inv_ear_pos2 = pygame.Vector2(screen.get_width() - ear_pos2.x, ear_pos2.y)
    inv_ear_pos3 = pygame.Vector2(screen.get_width() - ear_pos3.x, ear_pos3.y)
    draw_triangle(screen, color, [ear_pos1, ear_pos2, ear_pos3])
    draw_triangle(screen, color, [inv_ear_pos1, inv_ear_pos2, inv_ear_pos3], def_width)
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    hair_center = pygame.Vector2(rect_center.x, rect_center.y - 600)
    inv_hair_center = pygame.Vector2(screen.get_width() - hair_center.x, hair_center.y)
    draw_quick_rect(screen, color, hair_center, 1.2 * screen.get_width() / 3,
                    screen.get_height() / 6)
    draw_quick_rect(screen, color, inv_hair_center, 1.2 * screen.get_width() / 3,
                    screen.get_height() / 6, border_width=def_width)
    draw_quick_rect(screen, color, pygame.Vector2(hair_center.x + 200,
                                                  hair_center.y + 200),
                    screen.get_width() / 6, screen.get_height() / 3)
    draw_quick_rect(screen, color, pygame.Vector2(inv_hair_center.x - 200,
                                                  inv_hair_center.y + 200),
                    screen.get_width() / 6, screen.get_height() / 3, border_width=def_width)
    color = generate_random_color(not_this_color=used_clrs)
    used_clrs.append(color)
    pearls_centers = [pygame.Vector2(rect_center.x + 120, rect_center.y + 750),
                      pygame.Vector2(rect_center.x + 190, rect_center.y + 750),
                      pygame.Vector2(rect_center.x + 50, rect_center.y + 750),
                      pygame.Vector2(rect_center.x + 260, rect_center.y + 750),
                      pygame.Vector2(rect_center.x - 20, rect_center.y + 750)]
    for pc in pearls_centers:
        draw_circle(screen, color, pc, 30)
        draw_circle(screen, color, pygame.Vector2(screen.get_width() - pc.x, pc.y), 30, def_width)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_38.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
