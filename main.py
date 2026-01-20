# main.py
from city import City
from Driver import Driver
from Rider import Rider
from Trip import Trip
from DispatchEngine import DispatchEngine
from RollbackManager import RollbackManager
from RideShareSystem import RideShareSystem
import time, random

# ----- Initialize City -----
city = City()
for loc in ["A","B","C","D","E","F","G","H"]:
    city.add_location(loc)

city.add_road("A", "B", 5)
city.add_road("B", "C", 7)
city.add_road("A", "C", 10)
city.add_road("C", "D", 4)
city.add_road("B", "D", 6)
city.add_road("D", "E", 8)
city.add_road("E", "F", 3)
city.add_road("F", "G", 5)
city.add_road("G", "H", 4)
city.add_road("A", "H", 15)
city.add_road("B", "F", 10)
city.add_road("C", "G", 12)

# ----- Initialize Drivers -----
drivers = [
    Driver("A", "A", "Zone1"),
    Driver("B", "B", "Zone2"),
    Driver("C", "C", "Zone3"),
    Driver("D", "D", "Zone4")
]

# ----- Dispatcher and Rollback Manager -----
dispatcher = DispatchEngine(drivers, city)
rollback = RollbackManager()
system = RideShareSystem(city, dispatcher, rollback)

trip_counter = 1
trip_history = []

# ----- Statistics -----
total_revenue = 0
total_trips = 0

# ----- Helper Functions -----
def print_options():
    print("\nOptions:")
    print("1. Cancel Trip")
    print("2. View History")
    print("3. Request Ride")
    print("4. Rollback Last Operation")
    print("5. Show Driver Status")
    print("6. Show Wallets")
    print("7. Show Statistics")
    print("8. Exit")

def print_city_map(pickup, dropoff, driver):
    print("\nCity Map:")
    for loc in city.locations:
        marker = ""
        if loc.name == pickup:
            marker += "<- Pickup"
        if loc.name == dropoff:
            marker += "<- Dropoff"
        if driver and loc.name == driver.location:
            marker += "<- Driver"
        print(f"[{loc.name}]{marker}")
    print("-" * 30)

def simulate_traffic_delay(distance):
    delay = random.randint(0, 2)  # Random 0-2 min delay
    return distance + delay

def show_driver_status():
    print("\nDriver Status:")
    for d in drivers:
        status = "Available" if d.available else "Busy"
        avg_rating = round(sum(d.ratings)/len(d.ratings),1) if hasattr(d,"ratings") and d.ratings else "N/A"
        print(f"Driver {d.driver_id} | Location: {d.location} | Zone: {d.zone} | Status: {status} | Rating: {avg_rating}")

def show_wallets(riders):
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

# ----- Main Loop -----
riders = []
while True:
    print_options()
    choice = input("Enter your choice: ")

    if choice == "3":  # Request ride
        pickup = input("Enter pickup location: ")
        dropoff = input("Enter dropoff location: ")

        if city.get_node(pickup) is None or city.get_node(dropoff) is None:
            print("Invalid location! Choose from:", [node.name for node in city.locations])
            continue

        rider_wallet = 500
        rider = Rider(trip_counter, pickup, dropoff)
        rider.wallet = rider_wallet
        riders.append(rider)

        trip = system.create_trip(trip_counter, rider)
        if trip is None or trip.state == "CANCELLED":
            continue

        # Wallet check
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
            'state': trip.state
        })

        # Trip ONGOING
        trip.state = "ONGOING"
        print(f"\nTrip {trip.trip_id} is ONGOING. Driver {trip.driver.driver_id} is en route to {pickup}...")
        print_city_map(pickup, dropoff, trip.driver)
        total_distance = simulate_traffic_delay(trip.distance)
        for minute in range(1, total_distance + 1):
            time.sleep(0.5)
            print(f"Minute {minute}/{total_distance} en route...")
            print_city_map(pickup, dropoff, trip.driver)
            # Notification system
            if random.random() < 0.3:
                print(f"Notification: Driver {trip.driver.driver_id} delayed due to traffic!")
            elif minute == total_distance // 2:
                print(f"Notification: Driver {trip.driver.driver_id} is halfway to {dropoff}")
            elif minute == total_distance - 1:
                print(f"Notification: Driver {trip.driver.driver_id} is 1 minute away!")

        trip.state = "COMPLETED"
        print(f"\nTrip {trip.trip_id} COMPLETED! You have reached {dropoff}.")
        print(f"Total Fare Paid: {trip.fare} PKR")
        total_revenue += trip.fare
        total_trips += 1

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
                  f"{h['pickup']} -> {h['dropoff']}, Fare: {h['fare']} PKR, State: {h['state']}")

    elif choice == "4":  # Rollback
        k = int(input("Enter number of last operations to rollback: "))
        rollback.rollback_last_k(system, k)
        print(f"Rolled back last {k} operation(s).")

    elif choice == "5":  # Show Driver Status
        show_driver_status()

    elif choice == "6":  # Show Wallets
        show_wallets(riders)

    elif choice == "7":  # Show Statistics
        show_statistics()

    elif choice == "8":  # Exit
        print("Exiting RideShare System.")
        break

    else:
        print("Invalid choice. Try again.")




