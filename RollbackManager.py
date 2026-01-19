# RollbackManager.py
class RollbackManager:
    def __init__(self):
        self.stack = []

    def save_state(self, trip):
        self.stack.append(trip)

    def rollback_last_k(self, system, k):
        count = 0
        while self.stack and count < k:
            trip = self.stack.pop()
            if trip.state not in ["COMPLETED", "CANCELLED"]:
                trip.state = "CANCELLED"
                if trip.driver:
                    trip.driver.available = True
                count += 1
