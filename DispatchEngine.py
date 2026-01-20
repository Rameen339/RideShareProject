# DispatchEngine.py
from city import City
class DispatchEngine:
    def __init__(self, drivers, city):
        self.drivers = drivers
        self.city = city

    def assign_nearest_driver(self, city, pickup, dropoff):
        # Step 1: Find nearest driver
        nearest_driver = None
        nearest_distance = float('inf')
        nearest_name = None

        for d in self.drivers:
            dist = city.shortest_path(d.location, pickup)
            if dist < nearest_distance:
                nearest_distance = dist
                nearest_driver = d
                nearest_name = d.driver_id

        if not nearest_driver:
            raise ValueError("No drivers available!")

        # Step 2: Check if nearest driver is available
        if nearest_driver.available:
            nearest_driver.available = False
            extra_fare = 0
            return nearest_driver, extra_fare, nearest_name
        else:
            # Find next available driver
            available_drivers = [d for d in self.drivers if d.available]
            if not available_drivers:
                raise ValueError("All drivers are busy!")

            # Pick closest available driver
            assigned_driver = available_drivers[0]
            min_distance = city.shortest_path(assigned_driver.location, pickup)
            for d in available_drivers:
                dist = city.shortest_path(d.location, pickup)
                if dist < min_distance:
                    min_distance = dist
                    assigned_driver = d

            assigned_driver.available = False
            extra_fare = int(min_distance - nearest_distance) * 10
            if extra_fare < 0:
                extra_fare = 0

            return assigned_driver, extra_fare, nearest_name

