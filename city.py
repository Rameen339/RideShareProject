# Location.py
import heapq
from itertools import count

class Node:
    def __init__(self, name):
        self.name = name
        self.neighbors = []  # list of tuples (neighbor_node, distance)

    def __repr__(self):
        return f"Node({self.name})"

class City:
    def __init__(self):
        self.locations = []

    def add_location(self, name):
        self.locations.append(Node(name))

    def add_road(self, from_name, to_name, distance):
        from_node = self.get_node(from_name)
        to_node = self.get_node(to_name)
        if from_node and to_node:
            from_node.neighbors.append((to_node, distance))
            to_node.neighbors.append((from_node, distance))

    def get_node(self, name):
        for node in self.locations:
            if node.name == name:
                return node
        return None

    # Distance only
    def shortest_path(self, start_name, end_name):
        start = self.get_node(start_name)
        end = self.get_node(end_name)
        if not start or not end:
            return float('inf')

        distances = {node: float('inf') for node in self.locations}
        distances[start] = 0
        counter = count()
        heap = [(0, next(counter), start)]

        while heap:
            dist, _, node = heapq.heappop(heap)
            if node == end:
                return dist
            for neighbor, d in node.neighbors:
                if dist + d < distances[neighbor]:
                    distances[neighbor] = dist + d
                    heapq.heappush(heap, (distances[neighbor], next(counter), neighbor))
        return distances[end]

    # Distance + Path
    def shortest_path_with_route(self, start_name, end_name):
        start = self.get_node(start_name)
        end = self.get_node(end_name)
        if not start or not end:
            return -1, []

        distances = {node: float('inf') for node in self.locations}
        parent = {node: None for node in self.locations}
        distances[start] = 0
        counter = count()
        heap = [(0, next(counter), start)]

        while heap:
            dist, _, node = heapq.heappop(heap)
            if node == end:
                break
            for neighbor, d in node.neighbors:
                if dist + d < distances[neighbor]:
                    distances[neighbor] = dist + d
                    parent[neighbor] = node
                    heapq.heappush(heap, (distances[neighbor], next(counter), neighbor))

        if distances[end] == float('inf'):
            return -1, []

        path = []
        curr = end
        while curr:
            path.insert(0, curr.name)
            curr = parent[curr]

        return distances[end], path

