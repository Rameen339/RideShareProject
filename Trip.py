# Trip.py
class Trip:
    def __init__(trip_counter, rider, driver, distance_km, fare):
        self.trip_id = trip_id
        self.rider = rider
        self.driver = driver
        self.distance = distance
        self.fare = fare
        self.state = "ASSIGNED"  # REQUESTED -> ASSIGNED -> ONGOING -> COMPLETED
