import sys
import pygame
from curve import draw_spiral

# init_angles = [{"ang_deg": 0, "ang_change": 1},
#                {"ang_deg": 0, "ang_change": -1},
#                {"ang_deg": 45, "ang_change": 1},
#                {"ang_deg": 45, "ang_change": -1},
#                {"ang_deg": 90, "ang_change": 1},
#                {"ang_deg": 90, "ang_change": -1},
#                {"ang_deg": 135, "ang_change": 1},
#                {"ang_deg": 135, "ang_change": -1},
#                {"ang_deg": 180, "ang_change": 1},
#                {"ang_deg": 180, "ang_change": -1},
#                {"ang_deg": 225, "ang_change": 1},
#                {"ang_deg": 225, "ang_change": -1},
#                {"ang_deg": 270, "ang_change": 1},
#                {"ang_deg": 270, "ang_change": -1},
#                {"ang_deg": 315, "ang_change": 1},
#                {"ang_deg": 315, "ang_change": -1}]

def main() -> int:
    pygame.init()
    res = (2880, 2880)
    screen = pygame.display.set_mode(res)
    screen_color = "black"
    screen.fill(screen_color)
    len_const = screen.get_width() / 2
    init_pos_const = pygame.Vector2(screen.get_width() / 2,
                                    screen.get_height() / 2)
    init_angles = []
    iang = 0
    dang = 1
    count = 1
    while iang < 360:
        init_angles.append({"ang_deg": iang, "ang_change": dang})
        if count == 2:
            iang += 45
            count = 0
        count += 1
        dang = -dang
    for ang in init_angles:
        draw_spiral(surface=screen, color="white", init_len=len_const,
                    init_pos=init_pos_const, init_angle_deg=ang["ang_deg"],
                    angle_change=ang["ang_change"], width=5)
    pygame.image.save(screen, 'cc_pygame/gen/jpger_11.jpg')
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
