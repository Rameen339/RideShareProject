class Trip:
    def __init__(self, trip_id, rider, driver):
        self.trip_id = trip_id
        self.rider = rider
        self.driver = driver
        self.state = "REQUESTED"

    def assign(self):
        self.state = "ASSIGNED"

    def complete(self):
        self.state = "COMPLETED"

    def cancel(self):
        self.state = "CANCELLED"
