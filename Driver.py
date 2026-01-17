# Driver.py
class Driver:
    def __init__(self, driver_id, name, zone):
        self.driver_id = driver_id
        self.name = name
        self.zone = zone
        self.available = True
        self.current_location = None

    def assign(self, location):
        self.available = False
        self.current_location = location

    def release(self):
        self.available = True

