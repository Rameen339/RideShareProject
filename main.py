# main.py
from Driver import Driver
from Rider import Rider
from Trip import Trip
from DispatchEngine import DispatchEngine
from RollbackManager import RollbackManager
from RideShareSystem import RideShareSystem
from city import City  # using your updated Location.py
import time, random, threading
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

# Your existing lists and counters
riders = []
drivers = []
trip_counter = 1
dispatcher = DispatchEngine(drivers,City)  # pass your drivers list
rollback_manager = RollbackManager()
system = RideShareSystem(City, dispatcher, rollback_manager)  # or whatever your class is
trip_analytics = TripAnalytics()  # if you have analytics



# Add this at the top
from enhancements import (
    TrafficAwareCity, RidePoolManager, SurgePricing, ETACalculator,
    select_best_driver, TripAnalytics, simulate_random_events,
    display_possible_routes, suggest_drivers, RevenueAnalyzer,
    eta_progress_bar, analyze_rider_history, before_trip_start, after_trip_end
)


# ------------------- Initialize City with 27 locations -------------------
city = City()
for i in range(1, 28):
    city.add_location(f"L{i}")

# Add roads (sample realistic connections)
roads = [
    ("L1","L2",4), ("L2","L3",6), ("L3","L4",5), ("L4","L5",7),
    ("L5","L6",3), ("L6","L7",4), ("L7","L8",5), ("L8","L9",6),
    ("L9","L10",4), ("L10","L11",3), ("L11","L12",6), ("L12","L13",5),
    ("L13","L14",4), ("L14","L15",7), ("L15","L16",6), ("L16","L17",5),
    ("L17","L18",4), ("L18","L19",3), ("L19","L20",6), ("L20","L21",5),
    ("L21","L22",4), ("L22","L23",6), ("L23","L24",3), ("L24","L25",5),
    ("L25","L26",4), ("L26","L27",6),  # main connections
    ("L1","L5",10), ("L3","L10",9), ("L6","L15",12),
    ("L8","L18",11), ("L12","L20",8), ("L14","L25",10)  # extra cross connections
]

for u,v,d in roads:
    city.add_road(u,v,d)

drivers = [
    Driver("A", "L1", "Zone1"),
    Driver("B", "L5", "Zone2"),
    Driver("C", "L10", "Zone3"),
    Driver("D", "L15", "Zone4")
]

dispatcher = DispatchEngine(drivers, city)

# 4️⃣ Initialize Rollback Manager
rollback_manager = RollbackManager()

# 5️⃣ Initialize RideShareSystem (needs city, dispatcher, rollback)
system = RideShareSystem(city, dispatcher, rollback_manager)

# 6️⃣ Initialize Trip Analytics / Demand Forecast
trip_analytics = TripAnalytics()
demand_forecast = DemandForecast()

# ------------------- Pre-calculate Shortest Paths -------------------
shortest_paths_table = {}

def calculate_all_shortest_paths():
    for start_node in city.locations:
        for end_node in city.locations:
            distance, path = city.shortest_path_with_route(start_node.name, end_node.name)
            shortest_paths_table[(start_node.name, end_node.name)] = (distance, path)

calculate_all_shortest_paths()

def show_distance_between_locations(start, end):
    if (start, end) in shortest_paths_table:
        distance, path = shortest_paths_table[(start, end)]
        if distance == -1:
            print(f"No path found from {start} to {end}")
        else:
            print(f"Shortest distance from {start} to {end}: {distance}")
            print("Path:", " -> ".join(path))
    else:
        print("Invalid locations.")

# ------------------- Initialize Drivers -------------------
drivers = [
    Driver("A", "L1", "Zone1"),
    Driver("B", "L5", "Zone2"),
    Driver("C", "L10", "Zone3"),
    Driver("D", "L15", "Zone4")
]

# ------------------- Dispatcher & Rollback Manager -------------------
dispatcher = DispatchEngine(drivers, city)
rollback = RollbackManager()
system = RideShareSystem(city, dispatcher, rollback)

demand_forecast = DemandForecast()

trip_counter = 1
trip_history = []
riders = []
monthly_report = []
total_revenue = 0
total_trips = 0




# ------------------- Enhancements Initialization -------------------
traffic_city = TrafficAwareCity(city)
pool_manager = RidePoolManager()
surge_pricing = SurgePricing()
eta_calc = ETACalculator(city)
trip_analytics = TripAnalytics()
revenue_analyzer = RevenueAnalyzer()




# ------------------- Additional Globals -------------------
driver_ratings_history = {}    # {driver_id: [ratings]}
rider_ratings_history = {}     # {rider_id: [ratings]}
trip_cancellation_reasons = {} # {trip_id: reason}
promo_codes = {"DISCOUNT10": 0.9, "FLAT50": 50}
wallet_transactions = {}       # {rider_id: [{"type":"topup"/"deduct", "amount":, "trip":}]}


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
    print("18. Some Other Option")  # replace with actual description
    print("19. Show Rider Summary")


def print_city_map(pickup, dropoff, driver, other_drivers=None):
    print("\nCity Map:")
    for loc in city.locations:
        marker = ""
        if loc.name == pickup:
            marker += "<- Pickup"
        if loc.name == dropoff:
            marker += "<- Dropoff"
        if driver and loc.name == driver.location:
            marker += "<- Assigned Driver"
        if other_drivers:
            for od in other_drivers:
                if loc.name == od.location and od != driver:
                    marker += f"<- Driver {od.driver_id}"
        print(f"[{loc.name}]{marker}")
    print("-" * 30)

def simulate_traffic(distance):
    delay = random.randint(0,2)
    return distance + delay

def show_driver_status():
    print("\nDriver Status:")
    for d in drivers:
        status = "Available" if d.available else "Busy"
        avg_rating = round(sum(d.ratings)/len(d.ratings),1) if hasattr(d,"ratings") and d.ratings else "N/A"
        print(f"Driver {d.driver_id} | Location: {d.location} | Zone: {d.zone} | Status: {status} | Rating: {avg_rating}")

def show_wallets():
    print("\nRider Wallets:")
    for r in riders:
        print(f"Rider {r.rider_id} | Wallet: {getattr(r,'wallet',0)} PKR")

def show_statistics():
    print("\nStatistics:")
    print(f"Total trips completed: {total_trips}")
    print(f"Total revenue: {total_revenue} PKR")
    print("\nAverage fare per driver:")
    for d in drivers:
        driver_trips = [t for t in trip_history if t['driver']==d.driver_id and t['state']=="COMPLETED"]
        avg_fare = sum(t['fare'] for t in driver_trips)/len(driver_trips) if driver_trips else 0
        avg_rating = round(sum(d.ratings)/len(d.ratings),1) if hasattr(d,"ratings") and d.ratings else "N/A"
        print(f"Driver {d.driver_id}: Avg Fare: {avg_fare:.1f} PKR | Avg Rating: {avg_rating}")

# ------------------- Trip Simulation -------------------
# ------------------- Trip Simulation -------------------
def simulate_trip(trip, rider):
    global total_revenue, total_trips
    total_distance = simulate_traffic(trip.distance)
    
    print(f"\nTrip {trip.trip_id} started: {rider.pickup} -> {rider.dropoff} | Distance: {total_distance} mins")
    
    for minute in range(1, total_distance + 1):
        time.sleep(1)  # slower: 1 second per simulated minute
        print(f"\n[Trip {trip.trip_id}] Minute {minute}/{total_distance} en route...")
        print_city_map(rider.pickup, rider.dropoff, trip.driver, drivers)
        
        # Random events
        event_chance = random.random()
        if event_chance < 0.2:
            print(f"[Notification] Driver {trip.driver.driver_id} stuck in traffic! +1 min delay")
            total_distance += 1
        elif 0.2 <= event_chance < 0.3:
            print(f"[Notification] Heavy rain affecting trip speed! +2 min delay")
            total_distance += 2
        elif minute == total_distance // 2:
            print(f"[Notification] Driver {trip.driver.driver_id} is halfway to destination.")
        elif minute == total_distance - 1:
            print(f"[Notification] Driver {trip.driver.driver_id} is 1 minute away!")

    # Trip complete
    trip.state = "COMPLETED"
    print(f"\nTrip {trip.trip_id} COMPLETED! You have reached {rider.dropoff}.")
    print(f"Total Fare Paid: {trip.fare} PKR")
    total_revenue += trip.fare
    total_trips += 1

    # Ask rider to rate driver
    try:
        rating = int(input(f"Rate your driver {trip.driver.driver_id} (1-5 stars): "))
        if not hasattr(trip.driver, "ratings"):
            trip.driver.ratings = []
        trip.driver.ratings.append(rating)
    except:
        print("Rating skipped.")

    # Update history
    for h in trip_history:
        if h['trip_id'] == trip.trip_id:
            h['state'] = "COMPLETED"



# ------------------- Rating Functions -------------------
def rate_driver():
    print("\nAvailable Drivers to Rate:")
    for d in drivers:
        print(f"{d.driver_id} | Location: {d.location}")
    driver_id = input("Enter Driver ID to rate: ").strip()
    driver = next((d for d in drivers if d.driver_id == driver_id), None)
    if not driver:
        print("Invalid driver ID.")
        return
    try:
        rating = int(input(f"Rate driver {driver.driver_id} (1-5 stars): "))
        if rating < 1 or rating > 5:
            print("Rating must be between 1 and 5.")
            return
        if not hasattr(driver, "ratings"):
            driver.ratings = []
        driver.ratings.append(rating)
        print(f"Thank you! You rated driver {driver.driver_id} {rating} stars.")
    except:
        print("Invalid input. Rating skipped.")

def rate_rider():
    print("\nAvailable Riders to Rate:")
    for r in riders:
        print(f"Rider {r.rider_id} | Pickup: {r.pickup} | Dropoff: {r.dropoff}")
    rider_id = input("Enter Rider ID to rate: ").strip()
    rider = next((r for r in riders if str(r.rider_id) == rider_id), None)
    if not rider:
        print("Invalid rider ID.")
        return
    try:
        rating = int(input(f"Rate rider {rider.rider_id} (1-5 stars): "))
        if rating < 1 or rating > 5:
            print("Rating must be between 1 and 5.")
            return
        rider.ratings.append(rating)
        print(f"Thank you! You rated rider {rider.rider_id} {rating} stars.")
    except:
        print("Invalid input. Rating skipped.")






def top_up_wallet(rider):
    try:
        amount = float(input(f"Enter amount to top-up for Rider {rider.rider_id}: "))
        rider.wallet += amount
        wallet_transactions.setdefault(rider.rider_id, []).append({"type":"topup","amount":amount,"trip":None})
        print(f"Wallet updated. New balance: {rider.wallet}")
    except:
        print("Invalid input.")

def show_wallet_history(rider):
    print(f"\nWallet Transactions for Rider {rider.rider_id}:")
    for t in wallet_transactions.get(rider.rider_id, []):
        print(t)

def cancel_trip_with_reason(trip):
    reason = input("Enter reason for cancellation: ")
    trip.state = "CANCELLED"
    trip_cancellation_reasons[trip.trip_id] = reason
    if trip.driver:
        trip.driver.available = True
    # Refund logic
    refund_amount = trip.fare * 0.8  # refund 80% if cancelled
    trip.rider.wallet += refund_amount
    wallet_transactions.setdefault(trip.rider.rider_id, []).append({"type":"refund","amount":refund_amount,"trip":trip.trip_id})
    print(f"Trip {trip.trip_id} cancelled. Refund: {refund_amount} PKR")

def show_top_drivers():
    print("\nTop Drivers by Rating:")
    driver_avg = [(d.driver_id, sum(d.ratings)/len(d.ratings)) for d in drivers if hasattr(d,"ratings") and d.ratings]
    driver_avg.sort(key=lambda x: x[1], reverse=True)
    for driver_id, avg in driver_avg[:5]:
        print(f"{driver_id}: {avg:.1f} stars")

def show_top_riders():
    print("\nTop Riders by Rating:")
    rider_avg = [(r.rider_id, sum(r.ratings)/len(r.ratings)) for r in riders if hasattr(r,"ratings") and r.ratings]
    rider_avg.sort(key=lambda x: x[1], reverse=True)
    for rider_id, avg in rider_avg[:5]:
        print(f"{rider_id}: {avg:.1f} stars")

def show_longest_trip():
    longest = 0
    longest_path = None
    for start in city.locations:
        for end in city.locations:
            distance, path = city.shortest_path_with_route(start.name, end.name)
            if distance > longest:
                longest = distance
                longest_path = path
    print(f"\nLongest possible trip: {longest} km")
    print(" -> ".join(longest_path))

def suggest_nearby_drivers(pickup):
    distances = []
    for d in drivers:
        dist = city.shortest_path_with_route(d.location, pickup)[0]
        distances.append((dist,d))
    distances.sort(key=lambda x: x[0])
    print("\nNearest 3 Drivers:")
    for i,(dist,d) in enumerate(distances[:3],1):
        status = "Available" if d.available else "Busy"
        print(f"{i}. Driver {d.driver_id} | Location: {d.location} | Distance: {dist} | Status: {status}")
    return [d for _,d in distances[:3]]

def apply_promo_code(fare, code):
    if code in promo_codes:
        disc = promo_codes[code]
        if disc < 1:
            fare *= disc
        else:
            fare -= disc
        return max(fare,0)
    return fare


# --

# ------------------- Initialize City with 27 locations -------------------
city = City()
for i in range(1, 28):
    city.add_location(f"L{i}")

# Add roads (sample realistic connections)
roads = [
    ("L1","L2",4), ("L2","L3",6), ("L3","L4",5), ("L4","L5",7),
    ("L5","L6",3), ("L6","L7",4), ("L7","L8",5), ("L8","L9",6),
    ("L9","L10",4), ("L10","L11",3), ("L11","L12",6), ("L12","L13",5),
    ("L13","L14",4), ("L14","L15",7), ("L15","L16",6), ("L16","L17",5),
    ("L17","L18",4), ("L18","L19",3), ("L19","L20",6), ("L20","L21",5),
    ("L21","L22",4), ("L22","L23",6), ("L23","L24",3), ("L24","L25",5),
    ("L25","L26",4), ("L26","L27",6),  # main connections
    ("L1","L5",10), ("L3","L10",9), ("L6","L15",12),
    ("L8","L18",11), ("L12","L20",8), ("L14","L25",10)  # extra cross connections
]

for u,v,d in roads:
    city.add_road(u,v,d)

# ------------------- Pre-calculate Shortest Paths -------------------
shortest_paths_table = {}

def calculate_all_shortest_paths():
    for start_node in city.locations:
        for end_node in city.locations:
            distance, path = city.shortest_path_with_route(start_node.name, end_node.name)
            shortest_paths_table[(start_node.name, end_node.name)] = (distance, path)

calculate_all_shortest_paths()

def show_distance_between_locations(start, end):
    if (start, end) in shortest_paths_table:
        distance, path = shortest_paths_table[(start, end)]
        if distance == -1:
            print(f"No path found from {start} to {end}")
        else:
            print(f"Shortest distance from {start} to {end}: {distance}")
            print("Path:", " -> ".join(path))
    else:
        print("Invalid locations.")

# ------------------- Initialize Drivers -------------------
drivers = [
    Driver("A", "L1", "Zone1"),
    Driver("B", "L5", "Zone2"),
    Driver("C", "L10", "Zone3"),
    Driver("D", "L15", "Zone4")
]

# ------------------- Dispatcher & Rollback Manager -------------------
dispatcher = DispatchEngine(drivers, city)
rollback = RollbackManager()
system = RideShareSystem(city, dispatcher, rollback)

trip_counter = 1
trip_history = []
riders = []
monthly_report = []
total_revenue = 0
total_trips = 0



# ------------------- Additional Globals -------------------
driver_ratings_history = {}    # {driver_id: [ratings]}
rider_ratings_history = {}     # {rider_id: [ratings]}
trip_cancellation_reasons = {} # {trip_id: reason}
promo_codes = {"DISCOUNT10": 0.9, "FLAT50": 50}
wallet_transactions = {}       # {rider_id: [{"type":"topup"/"deduct", "amount":, "trip":}]}


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
    print("18. Some Other Option")  # replace with actual description



def print_city_map(pickup, dropoff, driver, other_drivers=None):
    print("\nCity Map:")
    for loc in city.locations:
        marker = ""
        if loc.name == pickup:
            marker += "<- Pickup"
        if loc.name == dropoff:
            marker += "<- Dropoff"
        if driver and loc.name == driver.location:
            marker += "<- Assigned Driver"
        if other_drivers:
            for od in other_drivers:
                if loc.name == od.location and od != driver:
                    marker += f"<- Driver {od.driver_id}"
        print(f"[{loc.name}]{marker}")
    print("-" * 30)

def simulate_traffic(distance):
    delay = random.randint(0,2)
    return distance + delay

def show_driver_status():
    print("\nDriver Status:")
    for d in drivers:
        status = "Available" if d.available else "Busy"
        avg_rating = round(sum(d.ratings)/len(d.ratings),1) if hasattr(d,"ratings") and d.ratings else "N/A"
        print(f"Driver {d.driver_id} | Location: {d.location} | Zone: {d.zone} | Status: {status} | Rating: {avg_rating}")

def show_wallets():
    print("\nRider Wallets:")
    for r in riders:
        print(f"Rider {r.rider_id} | Wallet: {getattr(r,'wallet',0)} PKR")

def show_statistics():
    print("\nStatistics:")
    print(f"Total trips completed: {total_trips}")
    print(f"Total revenue: {total_revenue} PKR")
    print("\nAverage fare per driver:")
    for d in drivers:
        driver_trips = [t for t in trip_history if t['driver']==d.driver_id and t['state']=="COMPLETED"]
        avg_fare = sum(t['fare'] for t in driver_trips)/len(driver_trips) if driver_trips else 0
        avg_rating = round(sum(d.ratings)/len(d.ratings),1) if hasattr(d,"ratings") and d.ratings else "N/A"
        print(f"Driver {d.driver_id}: Avg Fare: {avg_fare:.1f} PKR | Avg Rating: {avg_rating}")

# ------------------- Trip Simulation -------------------
# ------------------- Trip Simulation -------------------
def simulate_trip(trip, rider):
    global total_revenue, total_trips
    total_distance = simulate_traffic(trip.distance)
    
    print(f"\nTrip {trip.trip_id} started: {rider.pickup} -> {rider.dropoff} | Distance: {total_distance} mins")
    
    for minute in range(1, total_distance + 1):
        time.sleep(1)  # slower: 1 second per simulated minute
        print(f"\n[Trip {trip.trip_id}] Minute {minute}/{total_distance} en route...")
        print_city_map(rider.pickup, rider.dropoff, trip.driver, drivers)
        
        # Random events
        event_chance = random.random()
        if event_chance < 0.2:
            print(f"[Notification] Driver {trip.driver.driver_id} stuck in traffic! +1 min delay")
            total_distance += 1
        elif 0.2 <= event_chance < 0.3:
            print(f"[Notification] Heavy rain affecting trip speed! +2 min delay")
            total_distance += 2
        elif minute == total_distance // 2:
            print(f"[Notification] Driver {trip.driver.driver_id} is halfway to destination.")
        elif minute == total_distance - 1:
            print(f"[Notification] Driver {trip.driver.driver_id} is 1 minute away!")

    # Trip complete
    trip.state = "COMPLETED"
    print(f"\nTrip {trip.trip_id} COMPLETED! You have reached {rider.dropoff}.")
    print(f"Total Fare Paid: {trip.fare} PKR")
    total_revenue += trip.fare
    total_trips += 1

    # Ask rider to rate driver
    try:
        rating = int(input(f"Rate your driver {trip.driver.driver_id} (1-5 stars): "))
        if not hasattr(trip.driver, "ratings"):
            trip.driver.ratings = []
        trip.driver.ratings.append(rating)
    except:
        print("Rating skipped.")

    # Update history
    for h in trip_history:
        if h['trip_id'] == trip.trip_id:
            h['state'] = "COMPLETED"



# ------------------- Rating Functions -------------------
def rate_driver():
    print("\nAvailable Drivers to Rate:")
    for d in drivers:
        print(f"{d.driver_id} | Location: {d.location}")
    driver_id = input("Enter Driver ID to rate: ").strip()
    driver = next((d for d in drivers if d.driver_id == driver_id), None)
    if not driver:
        print("Invalid driver ID.")
        return
    try:
        rating = int(input(f"Rate driver {driver.driver_id} (1-5 stars): "))
        if rating < 1 or rating > 5:
            print("Rating must be between 1 and 5.")
            return
        if not hasattr(driver, "ratings"):
            driver.ratings = []
        driver.ratings.append(rating)
        print(f"Thank you! You rated driver {driver.driver_id} {rating} stars.")
    except:
        print("Invalid input. Rating skipped.")

def rate_rider():
    print("\nAvailable Riders to Rate:")
    for r in riders:
        print(f"Rider {r.rider_id} | Pickup: {r.pickup} | Dropoff: {r.dropoff}")
    rider_id = input("Enter Rider ID to rate: ").strip()
    rider = next((r for r in riders if str(r.rider_id) == rider_id), None)
    if not rider:
        print("Invalid rider ID.")
        return
    try:
        rating = int(input(f"Rate rider {rider.rider_id} (1-5 stars): "))
        if rating < 1 or rating > 5:
            print("Rating must be between 1 and 5.")
            return
        rider.ratings.append(rating)
        print(f"Thank you! You rated rider {rider.rider_id} {rating} stars.")
    except:
        print("Invalid input. Rating skipped.")






def top_up_wallet(rider):
    try:
        amount = float(input(f"Enter amount to top-up for Rider {rider.rider_id}: "))
        rider.wallet += amount
        wallet_transactions.setdefault(rider.rider_id, []).append({"type":"topup","amount":amount,"trip":None})
        print(f"Wallet updated. New balance: {rider.wallet}")
    except:
        print("Invalid input.")

def show_wallet_history(rider):
    print(f"\nWallet Transactions for Rider {rider.rider_id}:")
    for t in wallet_transactions.get(rider.rider_id, []):
        print(t)

def cancel_trip_with_reason(trip):
    reason = input("Enter reason for cancellation: ")
    trip.state = "CANCELLED"
    trip_cancellation_reasons[trip.trip_id] = reason
    if trip.driver:
        trip.driver.available = True
    # Refund logic
    refund_amount = trip.fare * 0.8  # refund 80% if cancelled
    trip.rider.wallet += refund_amount
    wallet_transactions.setdefault(trip.rider.rider_id, []).append({"type":"refund","amount":refund_amount,"trip":trip.trip_id})
    print(f"Trip {trip.trip_id} cancelled. Refund: {refund_amount} PKR")

def show_top_drivers():
    print("\nTop Drivers by Rating:")
    driver_avg = [(d.driver_id, sum(d.ratings)/len(d.ratings)) for d in drivers if hasattr(d,"ratings") and d.ratings]
    driver_avg.sort(key=lambda x: x[1], reverse=True)
    for driver_id, avg in driver_avg[:5]:
        print(f"{driver_id}: {avg:.1f} stars")

def show_top_riders():
    print("\nTop Riders by Rating:")
    rider_avg = [(r.rider_id, sum(r.ratings)/len(r.ratings)) for r in riders if hasattr(r,"ratings") and r.ratings]
    rider_avg.sort(key=lambda x: x[1], reverse=True)
    for rider_id, avg in rider_avg[:5]:
        print(f"{rider_id}: {avg:.1f} stars")

def show_longest_trip():
    longest = 0
    longest_path = None
    for start in city.locations:
        for end in city.locations:
            distance, path = city.shortest_path_with_route(start.name, end.name)
            if distance > longest:
                longest = distance
                longest_path = path
    print(f"\nLongest possible trip: {longest} km")
    print(" -> ".join(longest_path))

def suggest_nearby_drivers(pickup):
    distances = []
    for d in drivers:
        dist = city.shortest_path_with_route(d.location, pickup)[0]
        distances.append((dist,d))
    distances.sort(key=lambda x: x[0])
    print("\nNearest 3 Drivers:")
    for i,(dist,d) in enumerate(distances[:3],1):
        status = "Available" if d.available else "Busy"
        print(f"{i}. Driver {d.driver_id} | Location: {d.location} | Distance: {dist} | Status: {status}")
    return [d for _,d in distances[:3]]

def apply_promo_code(fare, code):
    if code in promo_codes:
        disc = promo_codes[code]
        if disc < 1:
            fare *= disc
        else:
            fare -= disc
        return max(fare,0)
    return fare


# ------------------- Main Loop -------------------
while True:
    print_options()
    choice = input("Enter your choice: ").strip()

    if choice == "1":  # Cancel Trip
        if not system.trips:
            print("No trips to cancel.")
            continue
        t_id = int(input("Enter trip ID to cancel: "))
        trip = next((t for t in system.trips if t.trip_id == t_id), None)
        if not trip:
            print("Trip not found.")
            continue
        if trip.state in ["COMPLETED", "CANCELLED"]:
            print(f"Trip {t_id} cannot be cancelled (already {trip.state})")
            continue
        trip.state = "CANCELLED"
        if trip.driver:
            trip.driver.available = True
        for h in trip_history:
            if h['trip_id'] == t_id:
                h['state'] = "CANCELLED"
        print(f"Trip {t_id} CANCELLED. Driver is now available.")

    elif choice == "2":  # View History
        if not trip_history:
            print("No trips in history.")
            continue
        print("\nTrip History:")
        for h in trip_history:
            print(f"Trip {h['trip_id']}: Rider {h['rider']} with Driver {h['driver']}, "
                  f"{h['pickup']} -> {h['dropoff']}, Fare: {h['fare']} PKR, State: {h['state']}, "
                  f"Promo: {h.get('promo_code','None')}, Vehicle: {h.get('vehicle','Car')}")

    elif choice == "3":  # Request Ride
        pickup = input("Enter pickup location: ")
        dropoff = input("Enter dropoff location: ")

        promo_code = input("Enter promo code (or press Enter to skip): ")


        rider = Rider(trip_counter, pickup, dropoff)
        rider.wallet = 500
        riders.append(rider)



        vehicle_types = ["Car", "Bike"]  # you can add more
        vehicle_fares = {}
        distance = city.shortest_path_with_route(pickup, dropoff)[0]
        base_fare_per_km = {"Car": 20, "Bike": 10}  # example rates

        for v in vehicle_types:
            fare = distance * base_fare_per_km[v]
            fare = apply_promo_code(fare, promo_code)
            vehicle_fares[v] = fare

    # Display fares to user
        print("\nEstimated fares for available vehicles:")
        for v, f in vehicle_fares.items():
            print(f"{v}: {f} PKR")

    # Ask user to select vehicle
        while True:
            selected_vehicle = input("Select vehicle type (Car/Bike): ").strip().capitalize()
            if selected_vehicle in vehicle_fares:
               break
            print("Invalid choice. Please select a valid vehicle.")

        trip_fare = vehicle_fares[selected_vehicle]
        trip = system.create_trip(trip_counter, rider, promo_code, vehicle_type=selected_vehicle, fare=trip_fare)

        if trip is None or trip.state == "CANCELLED":
           continue

        

        # Check if rider has enough wallet balance
        while rider.wallet < trip.fare:
           print(f"Insufficient wallet balance! Trip fare is {trip.fare}, but your wallet has {rider.wallet} PKR.")
        try:
           topup_amount = float(input("Enter additional amount to top up your wallet: "))
           rider.wallet += topup_amount
           print(f"Wallet updated. New balance: {rider.wallet} PKR")
        except:
           print("Invalid amount. Please enter a number.")

# Deduct fare after sufficient funds
        rider.wallet -= trip.fare
        print(f"Payment successful! {trip.fare} PKR deducted from wallet. Remaining balance: {rider.wallet} PKR")

# Start trip
        from datetime import datetime
        trip.start_time = datetime.now()
        demand_forecast.record_trip(trip)
        trip_analytics.record_trip(trip)
        threading.Thread(target=simulate_trip, args=(trip, rider)).start()
        trip_counter += 1



    elif choice == "4":  # Rollback
        while True:
            k_input = input("Enter number of last operations to rollback: ").strip()
            if not k_input.isdigit() or int(k_input) <= 0:
               print("Please enter a valid positive number.")
               continue
            k = int(k_input)
            break
        rollback.rollback_last_k(system, k)
        print(f"Rolled back last {k} operation(s).")


    elif choice == "5":  # Show Driver Status
        show_driver_status()

    elif choice == "6":  # Show Wallets
        show_wallets()

    elif choice == "7":  # Show Statistics & Monthly Report
        show_statistics()
        print("\nMonthly Report Summary:")
        total_revenue_report = sum(t['fare'] for t in monthly_report)
        total_trips_report = len(monthly_report)
        print(f"Total trips this month: {total_trips_report}")
        print(f"Total revenue this month: {total_revenue_report} PKR")
        driver_count = {}
        for t in monthly_report:
            driver_count[t['driver']] = driver_count.get(t['driver'], 0) + 1
        busiest_driver = max(driver_count, key=driver_count.get) if driver_count else "N/A"
        print(f"Busiest driver this month: {busiest_driver} with {driver_count.get(busiest_driver,0)} trips")

    elif choice == "8":  # Rate a driver
        rate_driver()

    elif choice == "9":  # Rate a rider
        rate_rider()

    elif choice == "10":  # Top Up Wallet
        rider_id = int(input("Enter Rider ID to top-up: ")).stripe()
        rider = next((r for r in riders if r.rider_id == rider_id), None)
        if rider:
            top_up_wallet(rider)
        else:
            print("Invalid Rider ID.")

    elif choice == "11":  # Show Wallet History
        rider_id = int(input("Enter Rider ID to view wallet history: ")).stripe()
        rider = next((r for r in riders if r.rider_id == rider_id), None)
        if rider:
            show_wallet_history(rider)
        else:
            print("Invalid Rider ID.")

    elif choice == "12":  # Show Top Drivers
        show_top_drivers()

    elif choice == "13":  # Show Top Riders
        show_top_riders()

    elif choice == "14":  # Show Longest Trip Possible
        show_longest_trip()

    elif choice == "15":  # Exit
        print("Exiting RideShare System.")
        break

    elif choice == "16":  # Show Most Frequent Routes
        top_routes = trip_analytics.most_frequent_routes()
        print("\nTop 5 Most Frequent Routes:")
        for (pickup, dropoff), count in top_routes:
            print(f"{pickup} -> {dropoff}: {count} trips")

    elif choice == "17":
        busy = demand_forecast.busiest_hours()
        if not busy:
           print("No trip data available yet.")
        else:
           print("\nBusiest Hours:")
           for hour, count in busy:
            print(f"{hour}:00 - {count} trips")


    elif choice == "18":  # Placeholder / Future Option
        print("Option 18 selected. Feature not implemented yet.")

    
    
    elif choice == "19":
       print_rider_summary(rider_analytics, feedback_manager, wallet_manager)

    else:
        print("Invalid choice. Please enter a number between 1 and 19.")
