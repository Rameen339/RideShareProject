# DispatchEngine.py
from city import City
class DispatchEngine:
    def __init__(self, drivers, city):
        self.drivers = drivers
        self.city = city

    def assign_driver_with_choice(self, pickup):
        nearest_driver = None
        nearest_distance = float('inf')

        # Find nearest driver
        for d in self.drivers:
            dist = self.city.shortest_path(d.location, pickup)
            if dist < nearest_distance:
                nearest_distance = dist
                nearest_driver = d

        # Case 1: Nearest driver is available
        if nearest_driver.available:
            nearest_driver.available = False
            return nearest_driver, nearest_distance, 0, "ASSIGNED"

        # Case 2: Nearest driver is busy
        print(f"\nNearest driver {nearest_driver.driver_id} is busy.")
        print("1. Wait for nearest driver")
        print("2. Assign another driver (higher fare)")

        choice = input("Enter choice (1/2): ")

        if choice == "1":
            return nearest_driver, nearest_distance, 0, "WAIT"

        # Assign far available driver
        available_drivers = [d for d in self.drivers if d.available]

        if not available_drivers:
            print("No other drivers available.")
            return None, None, None, "CANCELLED"

        assigned_driver = min(
            available_drivers,
            key=lambda d: self.city.shortest_path(d.location, pickup)
        )

        assigned_distance = self.city.shortest_path(assigned_driver.location, pickup)
        extra_fare = int((assigned_distance - nearest_distance) * 10)
        assigned_driver.available = False

        return assigned_driver, assigned_distance, extra_fare, "ASSIGNED"

