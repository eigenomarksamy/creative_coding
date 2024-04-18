import pygame
from shapes.pygame_circle import draw_point

class Node:

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.adj_nodes = list[Node]

class Graph:

    def __init__(self, nodes: list[Node], edges: list[list[Node]]) -> None:
        self.nodes = nodes
        self.edges = edges

def draw_nodes(surface: pygame.SurfaceType,
               node_radius: int = 10,
               points: list[pygame.Vector2]=[]) -> None:
    w, h = surface.get_size()
    if len(points) == 0:
        if w % node_radius != 0 or h % node_radius != 0:
            return
        centers = []
        posx = node_radius * 2
        posy = node_radius * 2
        while posx <= w - node_radius * 2:
            posy = node_radius * 2
            while posy <= h - node_radius * 2:
                centers.append(pygame.Vector2(posx, posy))
                posy += node_radius * 4
            posx += node_radius * 4
        for center in centers:
            draw_point(surface, "white", center)
        print(centers)
