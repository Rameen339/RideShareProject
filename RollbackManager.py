# RollbackManager.py
class Node:
    def __init__(self, trip):
        self.trip = trip
        self.next = None

class RollbackManager:
    def __init__(self):
        self.top = None

    def save_state(self, trip):
        node = Node(trip)
        node.next = self.top
        self.top = node

    def rollback_last(self):
        if self.top is None:
            print("Nothing to rollback")
            return
        trip = self.top.trip
        self.top = self.top.next
        trip.cancel_trip()
        print(f"Rolled back trip {trip.trip_id}")
