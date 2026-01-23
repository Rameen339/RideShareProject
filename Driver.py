class Driver:
    def __init__(self, driver_id, location, zone):
        self.driver_id = driver_id
        self.location = location
        self.zone = zone
        self.available = True

        # Driver statistics
        self.total_rides = 0
        self.rating = 5.0
        self.total_ratings = 0

    def assign_driver(self):
        self.available = False

    def complete_ride(self, new_rating):
        self.available = True
        self.total_rides += 1

        # update rating safely
        self.total_ratings += 1
        self.rating = (
            (self.rating * (self.total_ratings - 1)) + new_rating
        ) / self.total_ratings