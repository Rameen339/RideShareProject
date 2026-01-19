from city import City
from Driver import Driver
from Rider import Rider
from Trip import Trip
from DispatchEngine import DispatchEngine
from RollbackManager import RollbackManager
from RideShareSystem import RideShareSystem
import time

# ----- Initialize City -----
city = City()
city.add_location("A")
city.add_location("B")
city.add_location("C")
city.add_road("A", "B", 5)
city.add_road("B", "C", 7)
city.add_road("A", "C", 10)

# ----- Initialize Drivers -----
driver1 = Driver("A", "A", "Zone1")
driver2 = Driver("B", "B", "Zone2")
drivers = [driver1, driver2]

# ----- Dispatcher and Rollback Manager -----
dispatcher = DispatchEngine(drivers, city)
rollback = RollbackManager()
system = RideShareSystem(city, dispatcher, rollback)

trip_counter = 1
trip_history = []

# ----- Helper: show city map with driver -----
def display_city_map(driver_location, pickup=None, dropoff=None):
    print("\nCity Map:")
    for node in city.locations:
        line = f"[{node.name}]"
        if node.name == driver_location:
            line += " <- Driver"
        if pickup and node.name == pickup:
            line += " <- Pickup"
        if dropoff and node.name == dropoff:
            line += " <- Dropoff"
        print(line)
    print("-" * 30)

# ----- Menu Loop -----
def print_options():
    print("\nOptions:")
    print("1. Cancel Trip")
    print("2. View History")
    print("3. Request Ride")
    print("4. Rollback Last Operation")
    print("5. Exit")

while True:
    print_options()
    choice = input("Enter your choice: ")

    if choice == "3":  # Request ride
        pickup = input("Enter pickup location: ")
        dropoff = input("Enter dropoff location: ")

        if city.get_node(pickup) is None or city.get_node(dropoff) is None:
            print("Invalid location! Choose from:", [node.name for node in city.locations])
            continue

        rider = Rider(trip_counter, pickup, dropoff)
        trip = system.create_trip(trip_counter, rider)

        if trip is None or trip.state == "CANCELLED":
            print("Trip could not be created.")
            continue

        # Add trip to history
        trip_history.append({
            'trip_id': trip.trip_id,
            'rider': rider.rider_id,
            'driver': trip.driver.driver_id,
            'pickup': pickup,
            'dropoff': dropoff,
            'fare': trip.fare,
            'state': trip.state
        })

        # --- Real-Time Simulation with Map ---
        # 1️⃣ Driver approaching pickup
        print(f"\nDriver {trip.driver.driver_id} is on the way to pickup location...")
        driver_node = trip.driver.location
        distance_to_pickup = city.shortest_path(driver_node, pickup)
        for minute in range(distance_to_pickup, 0, -1):
            display_city_map(driver_node, pickup, dropoff)
            print(f"Driver arriving in {minute} minute(s)...")
            time.sleep(1)  # 1 sec = 1 min for demo
        trip.driver.location = pickup
        display_city_map(trip.driver.location, pickup, dropoff)
        print(f"Driver {trip.driver.driver_id} has arrived at pickup location!")

        # 2️⃣ Trip starts (ONGOING)
        trip.state = "ONGOING"
        print(f"\nTrip {trip.trip_id} is now ONGOING. Traveling to {dropoff}...")

        # 3️⃣ Simulate travel with driver moving
        travel_distance = trip.distance
        for minute in range(1, travel_distance + 1):
            display_city_map(trip.driver.location, pickup, dropoff)
            print(f"Minute {minute}/{travel_distance} en route...")
            time.sleep(1)
        trip.driver.location = dropoff

        # 4️⃣ Trip completed
        trip.state = "COMPLETED"
        display_city_map(trip.driver.location, pickup, dropoff)
        print(f"\nTrip {trip.trip_id} COMPLETED! You have reached {dropoff}.")

        # Update trip history
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

    elif choice == "5":  # Exit
        print("Exiting RideShare System.")
        break

    else:
        print("Invalid choice. Try again.")

