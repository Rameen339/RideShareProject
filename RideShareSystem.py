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

        # --- Use new dispatcher method with choice ---
        driver, driver_distance, extra_fare, status = self.dispatcher.assign_driver_with_choice(rider.pickup)

        if driver is None:
            print("No drivers available at the moment!")
            trip.state = "CANCELLED"
            return trip

        if status == "WAIT":
            print(f"Waiting for nearest driver {driver.driver_id} to be free...")
            # Simulate waiting time (1 minute real-time)
            time.sleep(60)
            print(f"Nearest driver {driver.driver_id} is now available!")
            driver.available = False  # mark driver as busy
            trip.driver = driver
            trip.state = "ASSIGNED"
            print(f"Driver {driver.driver_id} assigned after waiting.")
        else:
            trip.driver = driver
            trip.state = "ASSIGNED"
            if extra_fare > 0:
                trip.fare += extra_fare
                print(f"Nearest driver busy. Assigned driver {driver.driver_id} with extra fare {extra_fare} PKR.")
            else:
                print(f"Nearest driver {driver.driver_id} is available. Assigned to you!")

        print(f"Distance: {trip.distance} km | Total Fare: {trip.fare} PKR")
        print("Driver is on the way to pickup location...")

        # Save state for rollback
        self.rollback.save_state(trip)
        return trip


