# RideShareSystem.py
from Trip import Trip
import random
import time

class TripNode:
    def __init__(self, trip):
        self.trip = trip
        self.next = None

class RideShareSystem:
    def __init__(self, city, dispatcher, rollback):
        self.city = city
        self.dispatcher = dispatcher
        self.rollback = rollback
        self.head = None  # linked list of trips

    def add_trip_history(self, trip):
        node = TripNode(trip)
        node.next = self.head
        self.head = node

    def create_trip(self, trip_id, rider):
        driver = self.dispatcher.assign_driver()
        if not driver:
            print("No available drivers.")
            return None

        trip = Trip(trip_id, rider, driver)
        self.add_trip_history(trip)
        self.rollback.save_state(trip)

        trip.assign_driver()
        eta = random.randint(1, 10)
        print(f"Driver {driver.name} assigned, arriving in {eta} minutes...")
        time.sleep(min(eta, 5))
        trip.start_trip()
        print(f"Trip {trip.trip_id} started: From {rider.pickup} → {rider.dropoff}")
        return trip

    def cancel_trip(self, trip):
        trip.cancel_trip()
        print(f"Trip {trip.trip_id} cancelled")

    # ✅ Updated method to show pickup and dropoff locations
    def view_history(self):
        print("----Trip History----")
        current = self.head
        if not current:
            print("No trips yet.")
            return
        while current:
            t = current.trip
            print(f"Trip {t.trip_id}: Rider {t.rider.rider_id}, Driver {t.driver.name}, "
                  f"From {t.rider.pickup} → {t.rider.dropoff}, State: {t.state}")
            current = current.next

