import math
from typing import Tuple

def get_p1_from_polar(x1: float, y1: float, rho: float,
                      theta_deg: float) -> Tuple[float, float]:
    x2 = x1 + rho * math.cos(math.radians(theta_deg))
    y2 = y1 + rho * math.sin(math.radians(theta_deg))
    return x2, y2
