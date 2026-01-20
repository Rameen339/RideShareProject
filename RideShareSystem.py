# RideShareSystem.py
from Trip import Trip
import time
import random

class RideShareSystem:
    def __init__(self, city, dispatcher, rollback):
        self.city = city
        self.dispatcher = dispatcher
        self.rollback = rollback
        self.trips = []
        self.wallets = {}  # rider_id -> balance
        self.driver_ratings = {}  # driver_id -> [ratings]

    def create_trip(self, trip_id, rider, promo_code=""):
        distance_km = self.city.shortest_path(rider.pickup, rider.dropoff)
        if distance_km == float('inf'):
            print(f"No route exists from {rider.pickup} to {rider.dropoff}.")
            return None

        base_fare = distance_km * 10
        trip = Trip(trip_id, rider, None, distance_km, base_fare)
        self.trips.append(trip)
        trip.state = "REQUESTED"
        print(f"\nTrip {trip.trip_id} REQUESTED. Searching for nearest driver...")

        try:
            driver, extra_fare, nearest_name = self.dispatcher.assign_nearest_driver(
                self.city, rider.pickup, rider.dropoff
            )
        except ValueError:
            print("No drivers available at the moment!")
            trip.state = "CANCELLED"
            return trip

        # 1-minute simulated wait
        time.sleep(1)
        trip.driver = driver
        trip.state = "ASSIGNED"

        if nearest_name == driver.driver_id:
            print(f"Nearest driver {driver.driver_id} is available. Assigned to you!")
        else:
            print(f"Nearest driver {nearest_name} was busy.")
            print(f"Driver {driver.driver_id} has been assigned instead.")
            if extra_fare > 0:
                trip.fare += extra_fare
                print(f"Extra fare applied due to busy nearest driver: {extra_fare} PKR")

        # Apply promo code discount
        if promo_code == "DISCOUNT50":
            discount = 50
            trip.fare = max(0, trip.fare - discount)
            print(f"Promo code applied! Discount: {discount} PKR")

        print(f"Distance: {trip.distance} km | Total Fare: {trip.fare} PKR")
        print("Driver is on the way to pickup location...")

        self.rollback.save_state(trip)
        return trip

    def simulate_trip(self, trip):
        """Simulate minute-by-minute trip with random traffic events."""
        print(f"\nTrip {trip.trip_id} is ONGOING from {trip.rider.pickup} to {trip.rider.dropoff}")
        minutes = trip.distance
        for m in range(1, minutes + 1):
            traffic_delay = random.choice([0, 1, 2])  # random delay
            print(f"Minute {m}/{minutes} en route...", end="")
            if traffic_delay:
                print(f" Traffic! +{traffic_delay} min delay")
            else:
                print("")
            time.sleep(1)
        trip.state = "COMPLETED"
        trip.driver.available = True
        print(f"Trip {trip.trip_id} COMPLETED! You have reached {trip.rider.dropoff}.")

    def rate_driver(self, driver_id, rating):
        if driver_id not in self.driver_ratings:
            self.driver_ratings[driver_id] = []
        self.driver_ratings[driver_id].append(rating)

    def show_leaderboard(self):
        print("\nDriver Ratings Leaderboard:")
        for driver_id, ratings in self.driver_ratings.items():
            avg = sum(ratings) / len(ratings) if ratings else 0
            print(f"{driver_id}: Average Rating {avg:.1f} ({len(ratings)} trips)")


