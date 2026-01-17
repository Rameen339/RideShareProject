# main.py
from city import City
from Driver import Driver
from Rider import Rider
from DispatchEngine import DispatchEngine
from RollbackManager import RollbackManager
from RideShareSystem import RideShareSystem

# Initialize
print("RideShare Project Started")
city = City()
city.add_location("A")
city.add_location("B")
city.add_road("A", "B", 5)

driver1 = Driver(1, "Alice", "Zone1")
driver2 = Driver(2, "Bob", "Zone2")
drivers = [driver1, driver2]

dispatcher = DispatchEngine(drivers)
rollback = RollbackManager()
system = RideShareSystem(city, dispatcher, rollback)

trip_counter = 1
while True:
    print("\nOptions: ")
    print("1. Request a ride")
    print("2. View trip history")
    print("3. Rollback last trip")
    print("4. Exit")
    choice = input("Choose an option: ")

    if choice == "1":
        pickup = input("Enter pickup location: ")
        dropoff = input("Enter dropoff location: ")
        rider = Rider(trip_counter, pickup, dropoff)
        trip = system.create_trip(trip_counter, rider)
        if trip:
            trip_counter += 1
            cancel = input("Do you want to cancel this trip? (y/n): ")
            if cancel.lower() == "y":
                system.cancel_trip(trip)
    elif choice == "2":
        system.view_history()
    elif choice == "3":
        rollback.rollback_last()
    elif choice == "4":
        print("Exiting...")
        break
    else:
        print("Invalid choice")
