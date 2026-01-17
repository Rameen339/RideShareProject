# Trip.py
class Trip:
    def __init__(self, trip_id, rider, driver):
        self.trip_id = trip_id
        self.rider = rider
        self.driver = driver
        self.state = "REQUESTED"

    def assign_driver(self):
        self.state = "ASSIGNED"

    def start_trip(self):
        self.state = "ONGOING"

    def complete_trip(self):
        self.state = "COMPLETED"

    def cancel_trip(self):
        self.state = "CANCELLED"
        self.driver.release()

