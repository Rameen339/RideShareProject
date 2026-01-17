# City.py
class Node:
    def __init__(self, name):
        self.name = name
        self.neighbors = []  # list of tuples (neighbor_node, distance)

class City:
    def __init__(self):
        self.locations = []  # list of Node objects

    def add_location(self, name):
        node = Node(name)
        self.locations.append(node)

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

    def shortest_path(self, start_name, end_name):
        import heapq
        start = self.get_node(start_name)
        end = self.get_node(end_name)
        if not start or not end:
            return float('inf')

        distances = {node: float('inf') for node in self.locations}
        distances[start] = 0
        heap = [(0, start)]
        while heap:
            dist, node = heapq.heappop(heap)
            if node == end:
                return dist
            for neighbor, d in node.neighbors:
                if dist + d < distances[neighbor]:
                    distances[neighbor] = dist + d
                    heapq.heappush(heap, (distances[neighbor], neighbor))
        return distances[end]


