# Trip.py
class Trip:
    def __init__(self, trip_id, rider, driver, distance_km, fare):
        self.trip_id = trip_id
        self.rider = rider
        self.driver = driver
        self.distance = distance_km  # in minutes (simulated)
        self.fare = fare
        self.state = "REQUESTED"  # REQUESTED -> ASSIGNED -> ONGOING -> COMPLETED
