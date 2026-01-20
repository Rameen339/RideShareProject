# main.py

from Driver import Driver
from Rider import Rider
from Trip import Trip
from DispatchEngine import DispatchEngine
from RollbackManager import RollbackManager
from RideShareSystem import RideShareSystem
from city import City  # using your updated Location.py
import time, random, threading

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
    print("10. Exit")

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

# ------------------- Main Loop -------------------
while True:
    print_options()
    choice = input("Enter your choice: ")

    if choice == "3":  # Request ride
        pickup = input("Enter pickup location: ")
        dropoff = input("Enter dropoff location: ")
        promo_code = input("Enter promo code (or press Enter to skip): ")
        vehicle_type = input("Select Vehicle Type (Car/Bike/Van): ").strip().lower()

        if city.get_node(pickup) is None or city.get_node(dropoff) is None:
            print("Invalid location! Choose from:", [node.name for node in city.locations])
            continue

        rider_wallet = 500
        rider = Rider(trip_counter, pickup, dropoff)
        rider.wallet = rider_wallet
        riders.append(rider)

        # Vehicle type affects fare
        fare_multiplier = 1
        if vehicle_type == "bike":
            fare_multiplier = 0.8
        elif vehicle_type == "van":
            fare_multiplier = 1.5

        # Create trip
        trip = system.create_trip(trip_counter, rider, promo_code)
        if trip is None or trip.state == "CANCELLED":
            continue

        trip.fare *= fare_multiplier
        if rider.wallet < trip.fare:
            print(f"Insufficient wallet balance! Wallet: {rider.wallet} PKR | Fare: {trip.fare} PKR")
            trip.state = "CANCELLED"
            trip.driver.available = True
            continue
        else:
            rider.wallet -= trip.fare

        trip_history.append({
            'trip_id': trip.trip_id,
            'rider': rider.rider_id,
            'driver': trip.driver.driver_id,
            'pickup': pickup,
            'dropoff': dropoff,
            'fare': trip.fare,
            'state': trip.state,
            'promo_code': promo_code,
            'vehicle': vehicle_type
        })

        monthly_report.append({
            'trip_id': trip.trip_id,
            'fare': trip.fare,
            'driver': trip.driver.driver_id,
            'rider': rider.rider_id
        })

        # Start trip simulation in a thread
        threading.Thread(target=simulate_trip, args=(trip, rider)).start()
        trip_counter += 1

    elif choice == "1":  # Cancel Trip
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
                  f"{h['pickup']} -> {h['dropoff']}, Fare: {h['fare']} PKR, State: {h['state']}, Promo: {h.get('promo_code','None')}, Vehicle: {h.get('vehicle','Car')}")

    elif choice == "4":  # Rollback
        k = int(input("Enter number of last operations to rollback: "))
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

    elif choice == "10":  # Exit
        print("Exiting RideShare System.")
        break

    else:
        print("Invalid choice. Try again.")
