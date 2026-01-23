# main.py
from Driver import Driver
from Rider import Rider
from Trip import Trip
from DispatchEngine import DispatchEngine
from RollbackManager import RollbackManager
from RideShareSystem import RideShareSystem
from city import City
import time, random, threading
from datetime import datetime
from demand_forecast import DemandForecast
from feedback_manager import WalletManager, FeedbackManager, RiderAnalytics, RiderPromotions, simulate_rider_activity, print_rider_summary

from enhancements import (
    TrafficAwareCity, RidePoolManager, SurgePricing, ETACalculator,
    select_best_driver, TripAnalytics, simulate_random_events,
    display_possible_routes, suggest_drivers, RevenueAnalyzer,
    eta_progress_bar, analyze_rider_history, before_trip_start, after_trip_end
)

# ----- Initialize managers here -----
wallet_manager = WalletManager()
feedback_manager = FeedbackManager()
rider_analytics = RiderAnalytics(feedback_manager, wallet_manager)
promotions = RiderPromotions()
trip_analytics = TripAnalytics() 

# ------------------- Initialize City with 27 locations -------------------
city = City()
for i in range(1, 28):
    city.add_location(f"L{i}")

roads = [
    ("L1","L2",4), ("L2","L3",6), ("L3","L4",5), ("L4","L5",7),
    ("L5","L6",3), ("L6","L7",4), ("L7","L8",5), ("L8","L9",6),
    ("L9","L10",4), ("L10","L11",3), ("L11","L12",6), ("L12","L13",5),
    ("L13","L14",4), ("L14","L15",7), ("L15","L16",6), ("L16","L17",5),
    ("L17","L18",4), ("L18","L19",3), ("L19","L20",6), ("L20","L21",5),
    ("L21","L22",4), ("L22","L23",6), ("L23","L24",3), ("L24","L25",5),
    ("L25","L26",4), ("L26","L27",6),
    ("L1","L5",10), ("L3","L10",9), ("L6","L15",12),
    ("L8","L18",11), ("L12","L20",8), ("L14","L25",10)
]
for u,v,d in roads:
    city.add_road(u,v,d)

# ------------------- Initialize Drivers -------------------
drivers = [
    Driver("D1", "L4", "Zone1"),
    Driver("D2", "L9", "Zone2"),
    Driver("D3", "L15", "Zone3")
]

# Initialize Dispatcher and System
dispatcher = DispatchEngine(drivers, city)
rollback_manager = RollbackManager()
system = RideShareSystem(city, dispatcher, rollback_manager)
demand_forecast = DemandForecast()

# Global tracking variables
trip_counter = 1
trip_history = []
riders_list = []
total_revenue = 0
total_trips = 0
promo_codes = {"DISCOUNT10": 0.9, "FLAT50": 50}

# ------------------- Helper Functions -------------------
def print_options():
    print("\nOptions:")
    print("1. Cancel Trip")
    print("2. View History")
    print("3. Request Ride")
    print("4. Rollback Last Operation")
    print("5. Show Driver Status")
    print("6. Show Wallets")
    print("7. Show Statistics & Monthly Report")
    print("8. Rate a Driver")
    print("9. Rate a Rider")
    print("10. Top Up Wallet")
    print("11. Show Wallet History")
    print("12. Show Top Drivers")
    print("13. Show Top Riders")
    print("14. Show Longest Trip Possible")
    print("15. Exit")
    print("16. Show Most Frequent Routes")
    print("17. Show Busiest Hours")
    print("18. Some Other Option")
    print("19. Show Rider Summary")

def simulate_trip(trip, rider):
    global total_revenue, total_trips
    total_distance = trip.distance + random.randint(0,2)
    
    print(f"\nTrip {trip.trip_id} started: {rider.pickup} -> {rider.dropoff} | Distance: {total_distance} mins")
    
    for minute in range(1, total_distance + 1):
        time.sleep(1)
        print(f"[Trip {trip.trip_id}] Minute {minute}/{total_distance} en route...")
    
    trip.state = "COMPLETED"
    print(f"\nTrip {trip.trip_id} COMPLETED! You have reached {rider.dropoff}.")
    print(f"Total Fare Paid: {trip.fare} PKR")
    total_revenue += trip.fare
    total_trips += 1

    # Ask rider to rate driver at the end
    try:
        rating = int(input(f"Rate your driver {trip.driver.driver_id} (1-5 stars): "))
        if not hasattr(trip.driver, "ratings"):
            trip.driver.ratings = []
        trip.driver.ratings.append(rating)
    except:
        print("Rating skipped.")

def apply_promo_code(fare, code):
    if code in promo_codes:
        disc = promo_codes[code]
        return max(fare * disc if disc < 1 else fare - disc, 0)
    return fare

# ------------------- Main Program Logic -------------------
# FIRST: Ask for Rider Name and ID
rider_name_input = input("Enter Rider Name: ")
rider_id_input = input("Enter Rider ID: ")

while True:
    # SECOND: Show all 13+ options
    print_options()
    choice = input("Enter your choice: ").strip()

    if choice == "3":  # Request Ride
        pickup = input("Enter pickup location: ")
        dropoff = input("Enter dropoff location: ")
        promo_code = input("Enter promo code (or Enter to skip): ")

        # Create rider object
        rider = Rider(rider_id_input, pickup, dropoff)
        rider.wallet = 500 
        riders_list.append(rider)

        # Fare estimation
        dist_to_dest, path_to_dest = city.shortest_path_with_route(pickup, dropoff)
        car_fare = apply_promo_code(dist_to_dest * 20, promo_code)
        bike_fare = apply_promo_code(dist_to_dest * 10, promo_code)

        print(f"\nEstimated Fares:\nCar: {car_fare} PKR\nBike: {bike_fare} PKR")
        selected_vehicle = input("Select vehicle (Car/Bike): ").strip().capitalize()
        final_fare = car_fare if selected_vehicle == "Car" else bike_fare

        # Wallet check
        while rider.wallet < final_fare:
            print(f"Insufficient funds! Fare is {final_fare}. Wallet has {rider.wallet}.")
            rider.wallet += float(input("Enter amount to top up: "))

        # THIRD: Find Driver and SHOW ID, DISTANCE, ROUTE
        nearest_driver = None
        min_distance = 999999
        best_route = []

        for d in drivers:
            if d.available:
                dist, route = city.shortest_path_with_route(d.location, pickup)
                if dist != -1 and dist < min_distance:
                    min_distance = dist
                    nearest_driver = d
                    best_route = route

        if nearest_driver:
            print("\n" + "="*20)
            print("DRIVER ASSIGNED")
            print("Driver ID:", nearest_driver.driver_id)
            print("Distance to Pickup:", min_distance)
            print("Route to Pickup:", " -> ".join(best_route))
            print("="*20)

            # Start the trip
            trip = system.create_trip(trip_counter, rider, promo_code, vehicle_type=selected_vehicle, fare=final_fare)
            trip.driver = nearest_driver
            trip.distance = dist_to_dest
            nearest_driver.available = False
            rider.wallet -= final_fare
            
            threading.Thread(target=simulate_trip, args=(trip, rider)).start()
            trip_counter += 1
        else:
            print("No available driver found.")

    elif choice == "15":
        break