class DispatchEngine:
    def __init__(self, drivers):
        self.drivers = drivers

    def find_driver(self, zone):
        for d in self.drivers:
            if d.available and d.zone == zone:
                d.available = False
                return d
        return None