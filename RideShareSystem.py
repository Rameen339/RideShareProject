# RideShareSystem.py
from Trip import Trip
import time

class RideShareSystem:
    def __init__(self, city, dispatcher, rollback):
        self.city = city
        self.dispatcher = dispatcher
        self.rollback = rollback
        self.trips = []

    def create_trip(self, trip_id, rider):
        distance_km = self.city.shortest_path(rider.pickup, rider.dropoff)
        if distance_km == float('inf'):
            print(f"No route exists from {rider.pickup} to {rider.dropoff}.")
            return None

        base_fare = distance_km * 10
        trip = Trip(trip_id, rider, None, distance_km, base_fare)
        self.trips.append(trip)

        print(f"\nTrip {trip.trip_id} REQUESTED. Searching for nearest driver...")

        try:
            driver, extra_fare, nearest_name = self.dispatcher.assign_nearest_driver(
                self.city, rider.pickup, rider.dropoff
            )
        except ValueError:
            print("No drivers available at the moment!")
            trip.state = "CANCELLED"
            return trip

        # Simulate 1-minute delay for driver assignment
        time.sleep(1)
        trip.driver = driver
        trip.state = "ASSIGNED"

        # Show realistic driver assignment messages
        if nearest_name == driver.driver_id:
            print(f"Nearest driver {driver.driver_id} is available. Assigned to you!")
        else:
            print(f"Nearest driver {nearest_name} was busy.")
            print(f"Driver {driver.driver_id} has been assigned instead.")
            if extra_fare > 0:
                trip.fare += extra_fare
                print(f"Extra fare applied due to busy nearest driver: {extra_fare} PKR")

        print(f"Distance: {trip.distance} km | Total Fare: {trip.fare} PKR")
        print("Driver is on the way to pickup location...")

        # Save state for rollback
        self.rollback.save_state(trip)
        return trip


