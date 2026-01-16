print("RideShare Project Started")
from City import City
from Driver import Driver
from Rider import Rider
from DispatchEngine import DispatchEngine
from RollbackManager import RollbackManager
from RideShareSystem import RideShareSystem

print("RideShare System Started")

city = City()
city.add_location("A")
city.add_location("B")
city.add_road("A", "B", 5)

driver1 = Driver(1, "A", 1)
drivers = [driver1]

dispatch = DispatchEngine(drivers)
rollback = RollbackManager()

system = RideShareSystem(city, dispatch, rollback)

rider1 = Rider(101, "A", "B")
trip = system.create_trip(1, rider1, 1)

print("Trip State:", trip.state)

system.cancel_trip(trip)
print("After Cancel:", trip.state)
