# Driver.py
class Driver:
    def __init__(self, driver_id, location, zone):
        self.driver_id = driver_id        # Unique ID or name of driver
        self.location = location          # Current location (Node name)
        self.zone = zone                  # Zone the driver primarily serves
        self.available = True             # True if driver can take a trip
        self.current_trip = None          # Track assigned trip

    def assign_trip(self, trip):
        if self.available:
            self.current_trip = trip
            self.available = False
            return True
        return False

    def complete_trip(self):
        if self.current_trip:
            self.current_trip = None
            self.available = True

    def __str__(self):
        status = "Available" if self.available else "Busy"
        return f"Driver {self.driver_id} | Location: {self.location} | Zone: {self.zone} | Status: {status}"
