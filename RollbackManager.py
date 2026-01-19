# RollbackManager.py
class RollbackManager:
    def __init__(self):
        self.stack = []

    def save_state(self, trip):
        self.stack.append(trip)

    def rollback(self):
        if self.stack:
            trip = self.stack.pop()
            trip.state = "CANCELLED"
            trip.driver.available = True
            return trip
        return None
