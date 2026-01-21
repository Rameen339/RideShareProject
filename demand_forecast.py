# demand_forecast.py
from collections import defaultdict
from datetime import datetime

class DemandForecast:
    def __init__(self):
        self.hourly_trips = defaultdict(int)

    def record_trip(self, trip):
        """
        Call this when a trip is CREATED
        """
        if hasattr(trip, "start_time"):
            hour = trip.start_time.hour
        else:
            hour = datetime.now().hour

        self.hourly_trips[hour] += 1

    def busiest_hours(self, top_n=5):
        if not self.hourly_trips:
            return []

        sorted_hours = sorted(
            self.hourly_trips.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_hours[:top_n]
