# DispatchEngine.py
from city import City



class DispatchEngine:
    def __init__(self, drivers, city):
        self.drivers = drivers
        self.city = city

    def assign_driver_with_choice(self, pickup, dropoff):
        """
        Assigns a driver considering:
        - Nearest driver available immediately
        - If nearest is busy, ask rider if they want to wait or take a farther driver
        Returns: (driver_object, extra_fare, nearest_driver_name)
        """
        # Step 1: Find nearest driver
        nearest_driver = None
        nearest_distance = float('inf')
        for d in self.drivers:
            dist = self.city.shortest_path(d.location, pickup)
            if dist < nearest_distance:
                nearest_distance = dist
                nearest_driver = d

        nearest_name = nearest_driver.driver_id

        # Step 2: Check availability
        if nearest_driver.available:
            nearest_driver.available = False
            return nearest_driver, 0, nearest_name

        # Step 3: Nearest driver busy
        print(f"Nearest driver {nearest_driver.driver_id} is currently busy.")
        choice = input("Do you want to wait for them? (yes/no): ").lower()
        if choice == "yes":
            print("Waiting for nearest driver to become available...")
            while not nearest_driver.available:
                print("Still waiting...")
                # Simulate waiting
                import time
                time.sleep(1)  # 1 second wait for demo; can simulate minutes
            nearest_driver.available = False
            print(f"Driver {nearest_driver.driver_id} is now available and assigned to you!")
            return nearest_driver, 0, nearest_name
        else:
            # Find next available driver
            available_drivers = [d for d in self.drivers if d.available]
            if not available_drivers:
                print("No other drivers available at the moment. Please wait.")
                return None, 0, nearest_name

            # Pick the closest available driver
            assigned_driver = available_drivers[0]
            min_distance = self.city.shortest_path(assigned_driver.location, pickup)
            for d in available_drivers:
                dist = self.city.shortest_path(d.location, pickup)
                if dist < min_distance:
                    min_distance = dist
                    assigned_driver = d

            assigned_driver.available = False
            # Extra fare for farther driver
            extra_fare = max(0, int(min_distance - nearest_distance) * 10)
            return assigned_driver, extra_fare, nearest_name
