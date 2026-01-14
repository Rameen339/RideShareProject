class City:
    def __init__(self):
        self.roads = {}

    def add_road(self, a, b, distance):
        if a not in self.roads:
            self.roads[a] = []
        self.roads[a].append((b, distance))
