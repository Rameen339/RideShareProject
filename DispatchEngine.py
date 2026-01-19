class DispatchEngine:
    def __init__(self, drivers, city):
        self.drivers = drivers
        self.city = city

    def assign_nearest_driver(self, city, pickup, dropoff):
        # Step 1: Find the nearest driver to pickup
        nearest_driver = None
        nearest_distance = float('inf')
        nearest_driver_name = None
        for d in self.drivers:
            dist = city.shortest_path(d.location, pickup)
            if dist < nearest_distance:
                nearest_distance = dist
                nearest_driver = d
                nearest_driver_name = d.driver_id

        # Step 2: Check if nearest driver is available
        if nearest_driver.available:
            nearest_driver.available = False
            return nearest_driver, 0, nearest_driver_name
        else:
            # Nearest driver busy, find next available driver
            available_drivers = [d for d in self.drivers if d.available]
            if not available_drivers:
                raise ValueError("All drivers are busy!")

            # Pick the available driver with shortest path to pickup
            assigned_driver = available_drivers[0]
            min_distance = city.shortest_path(assigned_driver.location, pickup)
            for d in available_drivers:
                dist = city.shortest_path(d.location, pickup)
                if dist < min_distance:
                    min_distance = dist
                    assigned_driver = d

            # Mark assigned driver unavailable
            assigned_driver.available = False

            # Calculate extra fare
            extra_fare = int(min_distance - nearest_distance) * 10
            if extra_fare < 0:
                extra_fare = 0

            return assigned_driver, extra_fare, nearest_driver_name

