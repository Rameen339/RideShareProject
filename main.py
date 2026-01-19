from city import City
from Driver import Driver
from Rider import Rider
from Trip import Trip
from DispatchEngine import DispatchEngine
from RollbackManager import RollbackManager
from RideShareSystem import RideShareSystem
import time

# Initialize city graph
city = City()
city.add_location("A")
city.add_location("B")
city.add_location("C")
city.add_road("A", "B", 5)
city.add_road("B", "C", 7)
city.add_road("A", "C", 10)

# Initialize drivers
driver1 = Driver("A", "A", "Zone1")
driver2 = Driver("B", "B", "Zone2")
drivers = [driver1, driver2]

# Initialize dispatcher and rollback manager
dispatcher = DispatchEngine(drivers,city)
rollback = RollbackManager()
system = RideShareSystem(city, dispatcher, rollback)

# Trip counter and history
trip_counter = 1
trip_history = []

def print_options():
    print("\nOptions:")
    print("1. Cancel Trip")
    print("2. View History")
    print("3. Request Another Ride")
    print("4. Rollback Last Operation")
    print("5. Exit")

while True:
    print_options()
    choice = input("Enter your choice: ")

    if choice == "3":  # Request ride
        pickup = input("Enter pickup location: ")
        dropoff = input("Enter dropoff location: ")

        # Validate locations
        if city.get_node(pickup) is None or city.get_node(dropoff) is None:
            print("Invalid location! Choose from:", [node.name for node in city.locations])
            continue

        rider = Rider(trip_counter, pickup, dropoff)

        # Assign nearest driver (returns driver object and extra fare)
        try:
            driver, extra_fare, nearest_name = dispatcher.assign_nearest_driver(city, pickup, dropoff)
        except ValueError:
            print("No drivers available at the moment!")
            continue

        # Calculate shortest path distance and fare
        distance_km = city.shortest_path(pickup, dropoff)
        if distance_km == float('inf'):
            print(f"No route exists from {pickup} to {dropoff}.")
            continue

        base_fare = distance_km * 10
        total_fare = base_fare + extra_fare

        # Show assignment info
        print("\nRide Requested")
        if nearest_name != driver.driver_id:
            print(f"Nearest driver {nearest_name} is busy")
            print(f"Driver {driver.driver_id} has been assigned")
        else:
            print(f"Driver {driver.driver_id} has been assigned")

        print(f"Shortest path distance: {distance_km} km")
        if extra_fare > 0:
            print(f"Extra fare applied: {extra_fare} PKR")
        print(f"Total 3fare: {total_fare} PKR")
        print(f"Driver will reach in 5 minutes...")
        time.sleep(2)  # simulate ETA

        # Create Trip object
        trip = Trip(trip_counter, rider, driver,distance_km,fare)
        trip.state = "ASSIGNED"
        system.trips.append(trip)

        print("Trip is ASSIGNED. Driver is en route...")
        time.sleep(2)

        # Move trip to ONGOING
        trip.state = "ONGOING"
        print("Trip is ONGOING. You are en route...")
        print(f"Estimated arrival in {distance_km} minutes...")
        time.sleep(2)

        # Complete the trip
        trip.state = "COMPLETED"
        print("You have reached your destination. Trip COMPLETED!")

        # Save trip in history
        trip_history.append({
            'trip_id': trip_counter,
            'rider': rider.rider_id,
            'driver': driver.driver_id,
            'pickup': pickup,
            'dropoff': dropoff,
            'fare': total_fare,
            'state': trip.state
        })

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
        system.cancel_trip(trip)
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


