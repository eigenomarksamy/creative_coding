import random
import pygame
from shapes.pygame_circle import draw_point, draw_circle
from shapes.pygame_line import draw_line_cartesian
from shapes.pygame_rectangle import draw_quick_square

class Node:

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def draw(self, surface: pygame.SurfaceType, color: pygame.Color,
             radius: int=2, width: int=0) -> None:
        draw_circle(surface=surface, color=color,
                    pos=pygame.Vector2(self.x, self.y), radius= radius,
                    width=width)

class Edge:

    def __init__(self, node1: Node, node2: Node) -> None:
        self.node1 = node1
        self.node2 = node2

    def draw(self, surface: pygame.SurfaceType, color: pygame.Color,
             width: int=1) -> None:
        draw_line_cartesian(surface=surface, p0=pygame.Vector2(self.node1.x,
                                                               self.node1.y),
                            p1=pygame.Vector2(self.node2.x, self.node2.y),
                            color=color, width=width)

class Graph:

    def __init__(self, nodes: list[Node], edges: list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges

    def add_node(self, node: Node) -> None:
        self.nodes.append(node)

    def add_edge(self, edge: Edge) -> None:
        self.edges.append(edge)

    def draw(self, surface: pygame.SurfaceType, node_color: pygame.Color,
             edge_color: pygame.Color) -> None:
        for node in self.nodes:
            node.draw(surface=surface, color=node_color)
        for edge in self.edges:
            edge.draw(surface=surface, color=edge_color, width=2)

class Grid:

    def __init__(self, spacing: int, width: int, height: int) -> None:
        self.nodes = []
        self.edges = []
        for y in range(0, height, spacing):
            for x in range(0, width, spacing):
                self.nodes.append(Node(x, y))
        for node in self.nodes:
            self._connect_neighbors(node, spacing)

    def _connect_neighbors(self, node: Node, spacing: int) -> None:
        x, y = node.x, node.y
        self._add_edge_if_valid(node, x, y - spacing)
        self._add_edge_if_valid(node, x, y + spacing)
        self._add_edge_if_valid(node, x + spacing, y)
        self._add_edge_if_valid(node, x - spacing, y)
        self._add_edge_if_valid(node, x + spacing, y + spacing)
        self._add_edge_if_valid(node, x - spacing, y - spacing)
        self._add_edge_if_valid(node, x + spacing, y - spacing)
        self._add_edge_if_valid(node, x - spacing, y + spacing)

    def _add_edge_if_valid(self, node: Node, x: int, y: int) -> None:
        for neighbor in self.nodes:
            if neighbor.x == x and neighbor.y == y:
                self.edges.append(Edge(node, neighbor))

    def draw(self, surface: pygame.SurfaceType, node_color: pygame.Color,
             edge_color: pygame.Color) -> None:
        for edge in self.edges:
            edge.draw(surface, edge_color)
        for node in self.nodes:
            node.draw(surface, node_color)

def draw_test_graph(surface: pygame.Surface) -> None:
    node1 = Node(100, 100)
    node2 = Node(200, 200)
    edge = Edge(node1, node2)
    graph = Graph([], [])
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge(edge)
    graph.draw(surface, "white", "white")

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

def draw_initial_graph(surface: pygame.SurfaceType, color: pygame.Color,
                       spacing: int) -> None:
    Grid(spacing=spacing, width=surface.get_width(),
         height=surface.get_height()).draw(surface=surface, node_color=color,
                                           edge_color=color)

def get_random_neighbor(node: Node, edges: list[Edge],
                        node_spacing: int, visited: list[Node],
                        max_width: int, max_height: int) -> Node:
    x, y = node.x, node.y
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    random.shuffle(directions)
    for dx, dy in directions:
        neighbor_x, neighbor_y = x + dx * node_spacing, y + dy * node_spacing
        if 0 <= neighbor_x < max_width and 0 <= neighbor_y < max_height:
            potential_neighbor = Node(neighbor_x, neighbor_y)
            if potential_neighbor not in [edge.node1 for edge in edges] \
                and potential_neighbor not in visited:
                return potential_neighbor
    return None

def generate_random_graph(node_spacing: int, width: int, height: int) -> Graph:
    nodes = []
    edges = []
    for y in range(0, height, node_spacing):
        for x in range(0, width, node_spacing):
            nodes.append(Node(x, y))
    connected_nodes = set()
    connected_nodes.add(nodes[0])
    while len(connected_nodes) < len(nodes):
        node = random.choice(list(connected_nodes))
        neighbor = get_random_neighbor(node, edges, node_spacing,
                                       list(connected_nodes), width, height)
        if neighbor:
            edges.append(Edge(node, neighbor))
            connected_nodes.add(neighbor)
        else:
            break
    return Graph(nodes, edges)

def draw_chess_board(surface: pygame.SurfaceType, size: int) -> None:
    start_color = "white"
    for posx in range(int(size / 2), surface.get_width(), size):
        for posy in range(int(size / 2), surface.get_height(), size):
            draw_quick_square(surface, start_color, pygame.Vector2(posx, posy), size)
            if start_color == "white":
                start_color = "black"
            else:
                start_color = "white"
        if start_color == "white":
            start_color = "black"
        else:
            start_color = "white"

def gamify_life(surface: pygame.SurfaceType, base_color: pygame.Color,
                overlay_color: pygame.Color, spacing: int) -> None:
    draw_initial_graph(surface, base_color, spacing)
    generate_random_graph(spacing, surface.get_width(),
                          surface.get_height()).draw(surface, overlay_color,
                                                     overlay_color)
