# location.py
from city import City
class City:
    def __init__(self):
        self.graph = {}

    def add_road(self, u, v, w):
        if u not in self.graph:
            self.graph[u] = []
        if v not in self.graph:
            self.graph[v] = []

        self.graph[u].append((v, w))
        self.graph[v].append((u, w))

    def shortest_path_with_route(self, start, end):
        if start not in self.graph or end not in self.graph:
            return -1, []

        visited = []
        distance = {}
        parent = {}

        for node in self.graph:
            distance[node] = 999999
            parent[node] = None

        distance[start] = 0

        while True:
            min_node = None
            min_dist = 999999

            for node in distance:
                if node not in visited and distance[node] < min_dist:
                    min_dist = distance[node]
                    min_node = node

            if min_node is None or min_node == end:
                break

            visited.append(min_node)

            for neigh, w in self.graph[min_node]:
                if distance[min_node] + w < distance[neigh]:
                    distance[neigh] = distance[min_node] + w
                    parent[neigh] = min_node

        if distance[end] == 999999:
            return -1, []

        path = []
        curr = end
        while curr is not None:
            path.insert(0, curr)
            curr = parent[curr]

        return distance[end], path
