from Trip import Trip

class RideShareSystem:
    def __init__(self, city, dispatcher, rollback):
        self.city = city
        self.dispatcher = dispatcher
        self.rollback = rollback
        self.trips = []

    def create_trip(self, tid, rider, zone):
        trip = Trip(tid, rider)
        self.trips.append(trip)

        driver = self.dispatcher.find_driver(zone)
        if driver:
            trip.assign(driver)
            self.rollback.save(trip, driver)

        return trip

    def cancel_trip(self, trip):
        if trip.driver:
            trip.driver.available = True
        trip.cancel()

        #share ride