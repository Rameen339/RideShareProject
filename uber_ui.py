import tkinter as tk
from tkinter import messagebox, simpledialog
from city import City
from Driver import Driver
from Rider import Rider
from Trip import Trip
from DispatchEngine import DispatchEngine
from RollbackManager import RollbackManager
from RideShareSystem import RideShareSystem
import threading
import time

# ----- Backend Initialization -----
city = City()
city.add_location("A")
city.add_location("B")
city.add_location("C")
city.add_road("A", "B", 5)
city.add_road("B", "C", 7)
city.add_road("A", "C", 10)

driver1 = Driver("A", "A", "Zone1")
driver2 = Driver("B", "B", "Zone2")
drivers = [driver1, driver2]

dispatcher = DispatchEngine(drivers, city)
rollback = RollbackManager()
system = RideShareSystem(city, dispatcher, rollback)

trip_counter = 1
trip_history = []

# ----- UI Setup -----
root = tk.Tk()
root.title("UBER Ride Sharing")
root.geometry("700x500")
root.config(bg="#1db954")  # Uber-style green background

title_label = tk.Label(root, text="UBER Ride Sharing", font=("Helvetica", 24, "bold"), bg="#1db954", fg="white")
title_label.pack(pady=20)

status_frame = tk.Frame(root, bg="white", relief="sunken", bd=2)
status_frame.pack(pady=10, padx=20, fill="both", expand=True)

status_text = tk.Text(status_frame, height=15, bg="black", fg="white", font=("Helvetica", 12))
status_text.pack(fill="both", expand=True)

# ----- Helper function to update status -----
def update_status(msg):
    status_text.insert(tk.END, msg + "\n")
    status_text.see(tk.END)

# ----- Real-time ride simulation in separate thread -----
def simulate_trip(trip):
    global trip_history
    driver = trip.driver
    update_status(f"Trip {trip.trip_id} REQUESTED. Searching for nearest driver...")
    time.sleep(1)

    # Simulate driver moving to pickup
    eta_pickup = 5
    for i in range(eta_pickup, 0, -1):
        update_status(f"Driver {driver.driver_id} arriving at pickup in {i} min...")
        time.sleep(1)

    update_status(f"Driver {driver.driver_id} arrived at pickup. Trip starts!")
    trip.state = "ONGOING"

    # Simulate travel
    travel_time = trip.distance
    for t in range(1, travel_time + 1):
        update_status(f"Minute {t}/{travel_time} en route to {trip.rider.dropoff}...")
        time.sleep(1)

    trip.state = "COMPLETED"
    driver.location = trip.rider.dropoff
    update_status(f"Trip {trip.trip_id} COMPLETED! You have reached {trip.rider.dropoff}.")

    # Update trip history
    for h in trip_history:
        if h['trip_id'] == trip.trip_id:
            h['state'] = "COMPLETED"

# ----- Button Commands -----
def request_ride():
    global trip_counter
    pickup = simpledialog.askstring("Pickup Location", "Enter Pickup Location:")
    dropoff = simpledialog.askstring("Dropoff Location", "Enter Dropoff Location:")

    if city.get_node(pickup) is None or city.get_node(dropoff) is None:
        messagebox.showerror("Error", "Invalid pickup or dropoff location!")
        return

    rider = Rider(trip_counter, pickup, dropoff)
    trip = system.create_trip(trip_counter, rider)

    if trip is None or trip.state == "CANCELLED":
        update_status("Trip could not be created.")
        return

    trip_history.append({
        'trip_id': trip.trip_id,
        'rider': rider.rider_id,
        'driver': trip.driver.driver_id,
        'pickup': pickup,
        'dropoff': dropoff,
        'fare': trip.fare,
        'state': trip.state
    })

    # Start simulation in a new thread
    threading.Thread(target=simulate_trip, args=(trip,), daemon=True).start()
    trip_counter += 1

def cancel_trip():
    if not system.trips:
        messagebox.showinfo("Info", "No trips to cancel.")
        return
    t_id = simpledialog.askinteger("Cancel Trip", "Enter Trip ID to cancel:")
    trip = next((t for t in system.trips if t.trip_id == t_id), None)
    if not trip:
        messagebox.showerror("Error", "Trip not found.")
        return
    if trip.state in ["COMPLETED", "CANCELLED"]:
        messagebox.showinfo("Info", f"Trip {t_id} cannot be cancelled (already {trip.state})")
        return
    trip.state = "CANCELLED"
    if trip.driver:
        trip.driver.available = True
    for h in trip_history:
        if h['trip_id'] == t_id:
            h['state'] = "CANCELLED"
    update_status(f"Trip {t_id} CANCELLED. Driver is now available.")

def view_history():
    if not trip_history:
        messagebox.showinfo("Trip History", "No trips yet.")
        return
    history_str = ""
    for h in trip_history:
        history_str += f"Trip {h['trip_id']}: Rider {h['rider']} with Driver {h['driver']}, "
        history_str += f"{h['pickup']} -> {h['dropoff']}, Fare: {h['fare']} PKR, State: {h['state']}\n"
    messagebox.showinfo("Trip History", history_str)

def rollback_operation():
    k = simpledialog.askinteger("Rollback", "Enter number of last operations to rollback:")
    rollback.rollback_last_k(system, k)
    update_status(f"Rolled back last {k} operation(s).")

def exit_app():
    root.destroy()

# ----- Buttons -----
button_frame = tk.Frame(root, bg="#1db954")
button_frame.pack(pady=10)

tk.Button(button_frame, text="Request Ride", width=15, bg="white", fg="green", font=("Helvetica", 12), command=request_ride).grid(row=0, column=0, padx=10, pady=5)
tk.Button(button_frame, text="Cancel Trip", width=15, bg="white", fg="green", font=("Helvetica", 12), command=cancel_trip).grid(row=0, column=1, padx=10, pady=5)
tk.Button(button_frame, text="View History", width=15, bg="white", fg="green", font=("Helvetica", 12), command=view_history).grid(row=0, column=2, padx=10, pady=5)
tk.Button(button_frame, text="Rollback", width=15, bg="white", fg="green", font=("Helvetica", 12), command=rollback_operation).grid(row=1, column=0, padx=10, pady=5)
tk.Button(button_frame, text="Exit", width=15, bg="white", fg="green", font=("Helvetica", 12), command=exit_app).grid(row=1, column=1, padx=10, pady=5)

# ----- Run the UI -----
root.mainloop()

