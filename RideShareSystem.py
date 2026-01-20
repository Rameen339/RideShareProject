# RideShareSystem.py
from Trip import Trip
import time, random

class RideShareSystem:
    def __init__(self, city, dispatcher, rollback):
        self.city = city
        self.dispatcher = dispatcher
        self.rollback = rollback
        self.trips = []
        self.promo_codes = {"DISCOUNT50": 50, "SAVE30": 30}  # discount PKR
        self.surge_zones = ["B", "D", "F"]  # zones with surge pricing
        self.surge_multiplier = 1.5  # 50% extra fare during surge

    def create_trip(self, trip_id, rider, promo_code=None):
        distance_km = self.city.shortest_path(rider.pickup, rider.dropoff)
        if distance_km == float('inf'):
            print(f"No route exists from {rider.pickup} to {rider.dropoff}.")
            return None

        base_fare = distance_km * 10

        # Apply surge pricing
        extra_surge = 0
        if rider.pickup in self.surge_zones:
            base_fare = int(base_fare * self.surge_multiplier)
            extra_surge = base_fare - distance_km*10
            print(f"Surge pricing applied in {rider.pickup} zone! Extra fare: {extra_surge} PKR")

        trip = Trip(trip_id, rider, None, distance_km, base_fare)
        self.trips.append(trip)
        print(f"\nTrip {trip.trip_id} REQUESTED. Searching for nearest driver...")

        # Assign nearest driver
        try:
            driver, extra_fare, nearest_name = self.dispatcher.assign_nearest_driver(
                self.city, rider.pickup, rider.dropoff
            )
        except ValueError:
            print("No drivers available at the moment!")
            trip.state = "CANCELLED"
            return trip

        # Simulate 1-minute delay
        time.sleep(1)
        trip.driver = driver
        trip.state = "ASSIGNED"

        # Show assignment messages
        if nearest_name == driver.driver_id:
            print(f"Nearest driver {driver.driver_id} is available. Assigned to you!")
        else:
            print(f"Nearest driver {nearest_name} was busy.")
            print(f"Driver {driver.driver_id} has been assigned instead.")
            if extra_fare > 0:
                trip.fare += extra_fare
                print(f"Extra fare applied due to busy nearest driver: {extra_fare} PKR")

        # Apply promo if valid
        promo_discount = 0
        if promo_code and promo_code in self.promo_codes:
            promo_discount = self.promo_codes[promo_code]
            trip.fare -= promo_discount
            print(f"Promo code applied: {promo_code} - Discount: {promo_discount} PKR")

        print(f"Distance: {trip.distance} km | Total Fare: {trip.fare} PKR")
        print("Driver is on the way to pickup location...")

        self.rollback.save_state(trip)
        return trip


