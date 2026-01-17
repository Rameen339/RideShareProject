# DispatchEngine.py
class DispatchEngine:
    def __init__(self, drivers):
        self.drivers = drivers

    def assign_driver(self):
        for driver in self.drivers:
            if driver.available:
                driver.assign("pickup_location")
                return driver
        return None
