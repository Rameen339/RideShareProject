# RideShareSystem.py
from Trip import Trip

class RideShareSystem:
    def __init__(self, city, dispatcher, rollback):
        self.city = city
        self.dispatcher = dispatcher
        self.rollback = rollback
        self.trips = []

    def create_trip(self, trip_id, rider):
        print("\nRide Requested")
        driver, distance, extra_fare = self.dispatcher.assign_driver(rider.pickup)

        if not driver:
            print("No driver available at the moment.")
            return None

        fare = distance * 10 + extra_fare
        trip = Trip(trip_id, rider, driver, distance, fare)
        self.trips.append(trip)
        self.rollback.save_state(trip)

        if extra_fare > 0:
            print(f"Nearest driver was busy")
            print(f"Driver {driver.driver_id} has been assigned")
            print(f"Shortest path distance: {distance} km")
            print(f"Extra fare applied: {extra_fare} PKR")
        else:
            print(f"Driver {driver.driver_id} assigned successfully")
            print(f"Shortest path distance: {distance} km")
            print(f"No extra fare applied")

        print(f"Total fare: {fare} PKR\n")
        return trip
