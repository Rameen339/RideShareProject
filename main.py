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
demand_forecast = DemandForecast()
rollback_manager = RollbackManager()

# ------------------- Initialize City & Roads -------------------
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

dispatcher = DispatchEngine(drivers, city)
system = RideShareSystem(city, dispatcher, rollback_manager)

# ------------------- Globals -------------------
trip_counter = 1
trip_history = []
riders_list = []
total_revenue = 0
total_trips = 0
promo_codes = {"DISCOUNT10": 0.9, "FLAT50": 50}

# ------------------- Helper Functions -------------------
def print_options():
    print("\n" + "="*40)
    print("      RIDE-SHARE MAIN MENU      ")
    print("="*40)
    print("1. Cancel Trip          2. View History")
    print("3. REQUEST A RIDE       4. Rollback Operation")
    print("5. Driver Status        6. Show Wallets")
    print("7. Statistics           8. Rate a Driver")
    print("9. Rate a Rider         10. Top Up Wallet")
    print("11. Show Wallet History 12. Show Top Drivers")
    print("13. Show Top Riders     14. Show Longest Trip Possible")
    print("15. EXIT                16. Show Most Frequent Routes")
    print("17. Show Busiest Hours  18. Some Other Option")
    print("19. Show Rider Summary")

def apply_promo_code(fare, code):
    if code in promo_codes:
        disc = promo_codes[code]
        return max(fare * disc if disc < 1 else fare - disc, 0)
    return fare

def simulate_trip(trip, rider):
    global total_revenue, total_trips
    total_distance = trip.distance + random.randint(0,2)
    print(f"\n[LIVE] Trip {trip.trip_id} for {rider.name} started!")
    for minute in range(1, total_distance + 1):
        time.sleep(1) 
        print(f" > Minute {minute}/{total_distance}: En route to {rider.dropoff}...")
    trip.state = "COMPLETED"
    print(f"\n[SUCCESS] Trip {trip.trip_id} Finished! Fare: {trip.fare} PKR")
    total_revenue += trip.fare
    total_trips += 1
    trip.driver.available = True

    # ASK RIDER TO RATE THE DRIVER
    print("\nPlease rate your driver with the following options: 1, 2, 4.3, 4.5, 4.9")
    rating_choice = input("Enter rating: ").strip()
    print(f"THANK YOU FOR YOUR RATING: {rating_choice}")

# ------------------- Main Loop -------------------

# 1. ASK FOR RIDER IDENTITY FIRST
rider_name = input("\nEnter Rider Name: ").strip()
rider_id_input = input("Enter Rider ID: ").strip()

while True:
    # 2. SHOW THE 19 OPTIONS
    print_options()
    choice = input("Enter your selection: ").strip()

    if choice == "3":
        # ASK FOR TRIP OPTIONS
        pickup = input("Enter Pickup Location (e.g., L1): ").strip()
        dropoff = input("Enter Dropoff Location (e.g., L10): ").strip()
        promo_code = input("Enter Promo Code (Press Enter to skip): ").strip()

        # Calculate fare options
        dist_val, path = city.shortest_path_with_route(pickup, dropoff)
        if dist_val == -1:
            print("[ERROR] Route unavailable between these locations.")
            continue

        # 3. SHOW THE CAR AND BIKE FARE
        print(f"\nCalculating fares for {rider_name}...")
        car_fare = apply_promo_code(dist_val * 20, promo_code)
        bike_fare = apply_promo_code(dist_val * 10, promo_code)
        print(f"Available Services -> Car: {car_fare} PKR | Bike: {bike_fare} PKR")
        
        selected_v = input("Choose vehicle (Car/Bike): ").strip().capitalize()
        final_fare = car_fare if selected_v == "Car" else bike_fare

        # ASSIGN DRIVER AND SHOW INFO IMMEDIATELY
        nearest_driver = None
        min_distance = 999999
        best_route_to_pickup = []

        for d in drivers:
            if d.available:
                d_dist, d_route = city.shortest_path_with_route(d.location, pickup)
                if d_dist != -1 and d_dist < min_distance:
                    min_distance = d_dist
                    nearest_driver = d
                    best_route_to_pickup = d_route

        if nearest_driver:
            # DISPLAY ASSIGNMENT DETAILS
            print("\n" + "*"*35)
            print("      BOOKING CONFIRMED      ")
            print("*"*35)
            print(f"Rider:      {rider_name} (ID: {rider_id_input})")
            print(f"Driver ID:  {nearest_driver.driver_id}")
            print(f"Distance:   {min_distance} km to your location")
            print(f"Pickup Path: {' -> '.join(best_route_to_pickup)}")
            print(f"Destination Path: {' -> '.join(path)}")
            print("*"*35 + "\n")

            # Finalize trip object
            rider_obj = Rider(rider_id_input, pickup, dropoff)
            rider_obj.name = rider_name
            riders_list.append(rider_obj)
            
            trip = system.create_trip(trip_counter, rider_obj, promo_code, vehicle_type=selected_v, fare=final_fare)
            trip.driver = nearest_driver
            trip.distance = dist_val
            nearest_driver.available = False
            
            # START TRIP SIMULATION (Rating happens inside this function)
            t = threading.Thread(target=simulate_trip, args=(trip, rider_obj))
            t.start()
            t.join() # Wait for rating to finish before showing menu again
            trip_counter += 1
        else:
            print("\n[SORRY] No drivers available right now. Please try again later.")

    elif choice == "15":
        print("Shutting down the RideShare System. Goodbye!")
        break
    else:
        print("\nFeature processing... (This simulation focus is on the Ride Request flow).")