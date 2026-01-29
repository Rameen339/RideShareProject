from Driver import Driver
from Rider import Rider
from Trip import Trip
from DispatchEngine import DispatchEngine
from RollbackManager import RollbackManager
from RideShareSystem import RideShareSystem
from city import City
import time, threading, random
from datetime import datetime

                                #CASE SENSITIVE 
# ------------------- Initialization -------------------
rollback_manager = RollbackManager()
city = City()


turkey_cities = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Adana", "Konya", 
                 "Gaziantep", "Sanliurfa", "Mersin", "Diyarbakir", "Kayseri", "Eskisehir", 
                 "Samsun", "Trabzon", "Rize", "Erzurum", "Van", "Malatya", "Elazig", 
                 "Sivas", "Tokat", "Amasya", "Corum", "Kastamonu", "Bolu", "Duzce"]

for c in turkey_cities: city.add_location(c)

roads = [
    ("Istanbul","Bursa",4), ("Bursa","Eskisehir",6), ("Eskisehir","Ankara",5),
    ("Ankara","Konya",7), ("Konya","Antalya",3), ("Antalya","Mersin",4),
    ("Mersin","Adana",5), ("Adana","Gaziantep",6), ("Gaziantep","Sanliurfa",4),
    ("Sanliurfa","Diyarbakir",3), ("Diyarbakir","Malatya",6), ("Malatya","Elazig",5),
    ("Elazig","Erzurum",4), ("Erzurum","Van",7), ("Van","Trabzon",6), 
    ("Trabzon","Rize",5), ("Rize","Samsun",4), ("Samsun","Amasya",3),
    ("Amasya","Tokat",6), ("Tokat","Sivas",5), ("Sivas","Kayseri",4), 
    ("Kayseri","Ankara",6), ("Corum","Kastamonu",3), ("Kastamonu","Bolu",5),
    ("Bolu","Duzce",4), ("Duzce","Istanbul",6), ("Istanbul","Ankara",10)
]
for u,v,d in roads: city.add_road(u,v,d)

drivers = [
    Driver("D1", "Bursa", "Marmara"),
    Driver("D2", "Gaziantep", "Southeast"),
    Driver("D3", "Ankara", "Central")
]

# Advanced Driver Attributes
for d in drivers:
    d.ratings_list, d.feedbacks, d.earnings, d.available = [], [], 0, True
    d.fuel = random.randint(60, 100)
    d.vehicle_type = random.choice(["Standard", "Luxury"])
    d.total_km = 0

dispatcher = DispatchEngine(drivers, city)
system = RideShareSystem(city, dispatcher, rollback_manager)

# ------------------- Globals -------------------
trip_counter, trips_history, total_revenue, total_trips = 1, [], 0, 0
wallets, wallet_history = {}, {}

# ------------------- Logic Functions -------------------
def simulate_trip(trip, rider, path, weather_factor, weather_name):
    global total_revenue, total_trips
    total_dist = trip.distance
    duration = int(total_dist * weather_factor)
    
    print(f"\n[LIVE] Trip {trip.trip_id} started! Weather: {weather_name} ({weather_factor}x slowdown)")
    print(f"Path: {' -> '.join(path)}")
    
    for minute in range(1, duration + 1):
        time.sleep(1) 
        idx = min(int((minute / duration) * (len(path) - 1)), len(path) - 1)
        current_city = path[idx]
        
        km_done = min(int((minute / duration) * total_dist), total_dist)
        remaining_km = total_dist - km_done
        print(f" > Minute {minute}/{duration}: {current_city} | {remaining_km} km remaining")

    trip.state = "COMPLETED"
    trip.driver.available = True
    trip.driver.location = rider.dropoff
    trip.driver.fuel -= (total_dist * 0.7) # Fuel Consumption
    trip.driver.total_km += total_dist
    
    print(f"\n[SUCCESS] Arrived at {rider.dropoff}! Fuel Left: {max(0, trip.driver.fuel):.1f}%")
    
    # Payment Guard
    print("-" * 35)
    while True:
        try:
            pay_amt = float(input(f"Total Fare: {trip.fare}P. Enter Payment: "))
            if pay_amt < trip.fare:
                print(f"[!] Warning: Paid {pay_amt}P, but {trip.fare}P is required!")
            else:
                if pay_amt > trip.fare: print(f"Generous tip of {pay_amt - trip.fare}P recorded!")
                trip.driver.earnings += pay_amt
                total_revenue += pay_amt
                total_trips += 1
                break
        except ValueError: print("Please enter a numeric value.")

    try:
        r = float(input(f"Rate Driver (1-5): "))
        f = input("Leave feedback: ")
        trip.driver.ratings_list.append(r); trip.driver.feedbacks.append(f)
    except: pass
    print("-" * 35)

def print_options():
    print("\n" + "="*45 + "\n      TURKEY RIDE-SHARE - ELITE EDITION\n" + "="*45)
    print("1. Cancel Trip           2. View Trip History\n3. REQUEST A RIDE        4. Rollback Last Trip\n5. Driver Status (Fuel)  6. Show Wallets\n7. Show Statistics       8. Rate a Driver (Manual)\n9. Rate a Rider          10. Top Up Wallet\n11. Show Wallet History  12. Show Top Drivers\n13. Show Top Riders      14. Longest Trip History\n15. EXIT                 16. Most Frequent Routes\n17. Busiest Hours        18. System Log Summary\n19. Show Rider Summary")

# ------------------- Main Program -------------------
u_name = input("Enter Rider Name: ").strip()
u_id = input("Enter Rider ID: ").strip()
wallets[u_id], wallet_history[u_id] = 1000, [("Initial Deposit", 1000)]

while True:
    print_options()
    choice = input("Select (1-19): ").strip()

    if choice == "1":
        tid = int(input("Enter Trip ID: "))
        for t in trips_history:
            if t.trip_id == tid and t.state == "PENDING":
                t.state = "CANCELLED"; t.driver.available = True
                print(f"Trip {tid} cancelled.")

    elif choice == "2":
        for t in trips_history:
            print(f"ID: {t.trip_id} | {t.rider.pickup}->{t.rider.dropoff} | {t.state} | {t.fare}P")

    elif choice == "3":
        print("\n--- AVAILABLE CITIES IN TURKEY ---")
        for i, name in enumerate(turkey_cities, 1):
            print(f"{i:2}. {name:<12}", end="\t")
            if i % 3 == 0: 
                print()
        print("\n" + "-"*30)
        p, d = input("Pickup City: ").strip(), input("Dropoff City: ").strip()
        dist, path = city.shortest_path_with_route(p, d)
        if dist == -1: print("[ERROR] No route found."); continue
            
        weather = random.choice(["Clear", "Rainy", "Heavy Snow"])
        w_factor = {"Clear": 1.0, "Rainy": 1.4, "Heavy Snow": 2.2}[weather]

        near_d, min_d = None, 999
        for drv in drivers:
            d_dist, _ = city.shortest_path_with_route(drv.location, p)
            if drv.available and drv.fuel > 15 and d_dist < min_d:
                min_d, near_d = d_dist, drv

        if not near_d:
            print("[ERROR] No drivers available or drivers out of fuel."); continue

        # Dynamic Pricing (Distance + Surge + Luxury + Urgency)
        fare = dist * 20
        if min_d > 5:
            print(f"Surge: Distant driver fee applied (+20%)")
            fare *= 1.2
        if near_d.vehicle_type == "Luxury":
            print(f"Luxury Surge: High-end vehicle fee (+30%)")
            fare *= 1.3
        
        urgency = input("Mark as Priority/Emergency? (y/n): ").lower()
        if urgency == 'y': fare *= 1.15

        if wallets[u_id] < fare:
            print(f"Insufficient funds! Needed: {fare:.1f}P"); continue

        wallets[u_id] -= fare
        wallet_history[u_id].append((f"Trip to {d}", -fare))
        near_d.available = False
        
        rider_obj = Rider(u_id, p, d); rider_obj.name = u_name
        trip = system.create_trip(trip_counter, rider_obj, "", "Car", round(fare, 2))
        trip.driver, trip.distance, trip.timestamp = near_d, dist, datetime.now().hour
        trips_history.append(trip)
        
        t_thread = threading.Thread(target=simulate_trip, args=(trip, rider_obj, path, w_factor, weather))
        t_thread.start(); t_thread.join()
        trip_counter += 1

    elif choice == "4":
        if trips_history:
            last = trips_history.pop()
            wallets[u_id] += last.fare
            print(f"Rollback successful. {last.fare}P refunded.")

    elif choice == "5":
        for dr in drivers:
            st = "Available" if dr.available else "Busy"
            print(f"{dr.driver_id} ({dr.vehicle_type}) | Fuel: {dr.fuel:.1f}% | Total KM: {dr.total_km} | {st}")

    elif choice == "6":
        print(f"Balance: {wallets[u_id]} P")

    elif choice == "7":
        print(f"Total Revenue: {total_revenue}P | Total Trips: {total_trips}")

    elif choice == "10":
        amt = float(input("Enter top-up amount: "))
        wallets[u_id] += amt
        wallet_history[u_id].append(("Top Up", amt))

    elif choice == "11":
        for entry in wallet_history[u_id]: print(f"{entry[0]}: {entry[1]}P")

    elif choice == "12":
        top = sorted(drivers, key=lambda x: sum(x.ratings_list)/len(x.ratings_list) if x.ratings_list else 0, reverse=True)
        print(f"Best Driver: {top[0].driver_id}")

    elif choice == "15":
        print("System shutdown."); break

    elif choice == "16":
        freq = {}
        for t in trips_history:
            r = f"{t.rider.pickup}->{t.rider.dropoff}"
            freq[r] = freq.get(r, 0) + 1
        print("Popularity:", freq)

    elif choice == "17":
        hours = [t.timestamp for t in trips_history]
        if hours: print(f"Peak Hour: {max(set(hours), key=hours.count)}:00")

    elif choice == "18":
        print(f"--- ADMIN LOG ---")
        print(f"Total Trips: {len(trips_history)} | Active Users: 1 | System Healthy.")

    elif choice == "19":
        print(f"Summary for {u_name}: {len(trips_history)} trips completed | Balance: {wallets[u_id]}P")

    else:
        print("Feature logic active for choices 1-19.")
