class RollbackManager:
    def __init__(self):
        self.stack = []

    def save(self, trip, driver):
        self.stack.append((trip, driver))

    def rollback(self):
        if self.stack:
            return self.stack.pop()
        return None