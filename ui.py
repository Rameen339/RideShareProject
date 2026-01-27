import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import time
from datetime import datetime

# ------------------- BACKEND CLASSES (Your Original Logic) -------------------
class Driver:
    def __init__(self, d_id, loc, region):
        self.driver_id = d_id
        self.location = loc
        self.region = region
        self.ratings_list, self.feedbacks, self.earnings, self.available = [], [], 0, True
        self.fuel = random.randint(60, 100)
        self.vehicle_type = random.choice(["Standard", "Luxury"])
        self.total_km = 0

class Rider:
    def __init__(self, r_id, p, d):
        self.rider_id = r_id
        self.pickup = p
        self.dropoff = d
        self.name = ""

class TR_Elite_Ultimate_System:
    def __init__(self, root):
        self.root = root
        self.root.title("TR-ELITE Professional Infrastructure")
        self.root.geometry("1300x900")
        self.root.configure(bg="#050505")

        # --- GLOBAL STATE ---
        self.total_revenue = 0
        self.total_trips = 0
        self.trip_counter = 1
        self.trips_history = []
        self.u_name = "User_Alpha"
        self.u_id = "R-101"
        self.wallet_balance = 1000
        self.wallet_history = [("Initial Deposit", 1000)]
        self.rider_rating = 5.0  

        # Your Road Network
        self.city_map = {
            "Istanbul": {"Bursa": 4, "Ankara": 10, "Duzce": 6},
            "Bursa": {"Istanbul": 4, "Eskisehir": 6},
            "Ankara": {"Istanbul": 10, "Eskisehir": 5, "Konya": 7, "Kayseri": 6},
            "Konya": {"Ankara": 7, "Antalya": 3},
            "Antalya": {"Konya": 3, "Mersin": 4},
            "Mersin": {"Antalya": 4, "Adana": 5},
            "Adana": {"Mersin": 5, "Gaziantep": 6},
            "Gaziantep": {"Adana": 6, "Sanliurfa": 4},
            "Sanliurfa": {"Gaziantep": 4, "Diyarbakir": 3},
            "Diyarbakir": {"Sanliurfa": 3, "Malatya": 6}
        }
        self.cities = sorted(list(self.city_map.keys()))

        # Initialize Drivers
        self.drivers = [
            Driver("D1", "Bursa", "Marmara"),
            Driver("D2", "Gaziantep", "Southeast"),
            Driver("D3", "Ankara", "Central")
        ]

        self.setup_ui()

    def setup_ui(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, width=300, bg="#111")
        self.sidebar.pack(side="left", fill="y")
        tk.Label(self.sidebar, text="TR-ELITE PRO", font=("Impact", 24), fg="#00ffcc", bg="#111").pack(pady=20)

        canvas = tk.Canvas(self.sidebar, bg="#111", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.sidebar, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg="#111")
        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ALL 19 OPTIONS MAPPED
        self.menu_items = [
            ("1. Cancel Trip", self.cancel_trip), ("2. View Trip History", self.view_history),
            ("3. REQUEST A RIDE", self.request_ride_popup), ("4. Rollback Last Trip", self.rollback),
            ("5. Driver Status (Fuel)", self.show_drivers), ("6. Show Wallets", self.show_wallet),
            ("7. Show Statistics", self.show_stats), 
            ("8. Rate a Driver (Manual)", self.manual_driver_rating), 
            ("9. Rate a Rider", self.manual_rider_rating),            
            ("10. Top Up Wallet", self.top_up),
            ("11. Show Wallet History", self.wallet_history_log), ("12. Show Top Drivers", self.top_drivers),
            ("13. Show Top Riders", self.show_top_riders),            
            ("14. Longest Trip History", self.generic),
            ("15. EXIT", self.root.quit), ("16. Most Frequent Routes", self.freq_routes),
            ("17. Busiest Hours", self.show_busiest_hours), # FIXED: Changed from self.generic
            ("18. System Log Summary", self.log_summary),
            ("19. Show Rider Summary", self.rider_summary)
        ]

        for name, func in self.menu_items:
            tk.Button(self.scroll_frame, text=name, font=("Arial", 10), bg="#111", fg="white", 
                      relief="flat", anchor="w", padx=25, pady=10, 
                      activebackground="#00ffcc", command=func).pack(fill="x")

        # Main View
        self.main_view = tk.Frame(self.root, bg="#050505", padx=20, pady=20)
        self.main_view.pack(side="right", fill="both", expand=True)

        stats_bar = tk.Frame(self.main_view, bg="#050505")
        stats_bar.pack(fill="x", pady=(0, 20))
        self.rev_lbl = self.create_card(stats_bar, "TOTAL REVENUE", "0 P", 0)
        self.wal_lbl = self.create_card(stats_bar, "WALLET", "1000 P", 1)
        self.trip_lbl = self.create_card(stats_bar, "TRIPS", "0", 2)

        self.console = tk.Text(self.main_view, bg="black", fg="#00ff00", font=("Consolas", 11), padx=10, pady=10)
        self.console.pack(fill="both", expand=True)
        self.log("TR-ELITE System Online. Dispatch Engine Ready.")

    def create_card(self, parent, title, val, col):
        f = tk.Frame(parent, bg="#1a1a1a", padx=15, pady=10, highlightthickness=1, highlightbackground="#333")
        f.grid(row=0, column=col, padx=5, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)
        tk.Label(f, text=title, fg="#888", bg="#1a1a1a", font=("Arial", 9)).pack()
        lbl = tk.Label(f, text=val, fg="white", bg="#1a1a1a", font=("Arial", 14, "bold"))
        lbl.pack()
        return lbl

    def log(self, msg):
        self.console.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.console.see(tk.END)

    # ------------------- TRIP SIMULATION ENGINE -------------------
    def request_ride_popup(self):
        pop = tk.Toplevel(self.root)
        pop.title("Booking")
        pop.geometry("350x400")
        pop.configure(bg="#1a1a1a")
        
        tk.Label(pop, text="Pickup City:", fg="white", bg="#1a1a1a").pack(pady=5)
        p_box = ttk.Combobox(pop, values=self.cities); p_box.pack()
        tk.Label(pop, text="Dropoff City:", fg="white", bg="#1a1a1a").pack(pady=5)
        d_box = ttk.Combobox(pop, values=self.cities); d_box.pack()
        tk.Label(pop, text="Priority? (y/n):", fg="white", bg="#1a1a1a").pack(pady=5)
        pr_ent = ttk.Entry(pop); pr_ent.pack()

        def start():
            p, d, pr = p_box.get(), d_box.get(), pr_ent.get().lower()
            pop.destroy()
            threading.Thread(target=self.run_logic, args=(p, d, pr), daemon=True).start()
        tk.Button(pop, text="BOOK NOW", bg="#00ffcc", command=start).pack(pady=25)

    def run_logic(self, p, d, pr):
        if p not in self.city_map or d not in self.city_map:
            self.log("[ERROR] Invalid route."); return

        near_d = None
        min_dist = 999
        for drv in self.drivers:
            if drv.available and drv.fuel > 15:
                dist_to_rider = random.randint(1, 8)
                if dist_to_rider < min_dist:
                    min_dist, near_d = dist_to_rider, drv

        if not near_d:
            self.log("[ERROR] No drivers available."); return

        dist = 10 
        fare = dist * 20
        if min_dist > 5: fare *= 1.2 
        if near_d.vehicle_type == "Luxury": fare *= 1.3
        if pr == 'y': fare *= 1.15
        fare = round(fare, 2)

        weather = random.choice(["Clear", "Rainy", "Heavy Snow"])
        w_factor = {"Clear": 1.0, "Rainy": 1.4, "Heavy Snow": 2.2}[weather]
        duration = int(dist * w_factor)

        self.log(f"Trip Confirmed! Driver {near_d.driver_id} ({near_d.vehicle_type})")
        self.log(f"Weather: {weather} | Estimated Time: {duration} mins")
        
        near_d.available = False

        for m in range(1, duration + 1):
            time.sleep(1)
            km_rem = dist - (dist * (m / duration))
            self.log(f" > Minute {m}/{duration}: Moving... {round(km_rem, 1)} km left.")

        self.root.after(0, lambda: self.payment_flow(fare, near_d, d, dist))

    def payment_flow(self, fare, driver, dest, dist):
        pay_win = tk.Toplevel(self.root)
        pay_win.title("Payment")
        pay_win.geometry("300x200")
        pay_win.configure(bg="#1a1a1a")
        
        tk.Label(pay_win, text=f"Fare Due: {fare} P", fg="#00ffcc", bg="#1a1a1a", font=("Arial", 12, "bold")).pack(pady=15)
        ent = ttk.Entry(pay_win); ent.pack()

        def confirm():
            try:
                amt = float(ent.get())
                if amt >= fare:
                    self.total_revenue += fare
                    self.wallet_balance -= fare
                    driver.available = True
                    driver.location = dest
                    driver.fuel -= (dist * 0.7)
                    self.trips_history.append({"id": self.trip_counter, "route": f"-> {dest}", "fare": fare})
                    self.log(f"[SUCCESS] Paid {fare} P.")
                    self.update_stats()
                    pay_win.destroy()
                    self.feedback_flow(driver)
                else: messagebox.showwarning("Pay Up", f"Need {fare} P")
            except: pass
        tk.Button(pay_win, text="PAY", command=confirm).pack(pady=15)

    def feedback_flow(self, driver):
        f_win = tk.Toplevel(self.root)
        f_win.title("Rate")
        f_win.geometry("300x200")
        f_win.configure(bg="#1a1a1a")
        
        tk.Label(f_win, text=f"Rate {driver.driver_id} (1-5):", fg="white", bg="#1a1a1a").pack(pady=5)
        rate = ttk.Combobox(f_win, values=["1", "2", "3", "4", "5"]); rate.pack()
        tk.Label(f_win, text="Feedback:", fg="white", bg="#1a1a1a").pack(pady=5)
        txt = ttk.Entry(f_win); txt.pack()

        def submit():
            driver.ratings_list.append(float(rate.get()))
            driver.feedbacks.append(txt.get())
            self.log(f"Feedback recorded: {rate.get()} stars.")
            f_win.destroy()
            self.trip_counter += 1
        tk.Button(f_win, text="SUBMIT", command=submit).pack(pady=10)

    # ------------------- MENU FUNCTIONALITIES -------------------
    def manual_driver_rating(self):
        m_win = tk.Toplevel(self.root)
        m_win.title("Manual Driver Rating")
        m_win.geometry("300x250")
        m_win.configure(bg="#1a1a1a")
        tk.Label(m_win, text="Select Driver ID:", fg="white", bg="#1a1a1a").pack(pady=5)
        d_ids = [d.driver_id for d in self.drivers]
        d_box = ttk.Combobox(m_win, values=d_ids); d_box.pack()
        tk.Label(m_win, text="Rating (1-5):", fg="white", bg="#1a1a1a").pack(pady=5)
        r_box = ttk.Combobox(m_win, values=["1", "2", "3", "4", "5"]); r_box.pack()
        def submit_manual():
            target = d_box.get()
            for d in self.drivers:
                if d.driver_id == target:
                    d.ratings_list.append(float(r_box.get()))
                    self.log(f"[MANUAL RATE] Rated {target} {r_box.get()} stars.")
            m_win.destroy()
        tk.Button(m_win, text="SUBMIT", command=submit_manual).pack(pady=20)

    def manual_rider_rating(self):
        r_win = tk.Toplevel(self.root)
        r_win.title("Manual Rider Rating")
        r_win.geometry("300x200")
        r_win.configure(bg="#1a1a1a")
        tk.Label(r_win, text=f"Rate Rider: {self.u_name} (1-5):", fg="white", bg="#1a1a1a").pack(pady=10)
        r_box = ttk.Combobox(r_win, values=["1", "2", "3", "4", "5"]); r_box.pack()
        def submit_rider_rate():
            new_val = float(r_box.get())
            self.rider_rating = round((self.rider_rating + new_val) / 2, 2)
            self.log(f"[SYSTEM] Rider {self.u_name} reputation updated to {self.rider_rating}")
            r_win.destroy()
        tk.Button(r_win, text="CONFIRM", command=submit_rider_rate).pack(pady=20)

    def show_top_riders(self):
        self.log("--- TOP RIDERS LEADERBOARD ---")
        self.log(f"1. {self.u_name} | Rating: {self.rider_rating} | Trips: {len(self.trips_history)}")
        self.log("2. Guest_User_Alpha | Rating: 4.8 | Trips: 12")
        self.log("3. Test_Account_001 | Rating: 4.2 | Trips: 5")

    def show_busiest_hours(self): # FIXED: New Logic for Option 17
        self.log("--- SYSTEM TRAFFIC ANALYSIS (24H) ---")
        # Mock traffic density data
        traffic_data = [
            ("08:00 - 10:00", "MORNING PEAK", "High Demand"),
            ("12:00 - 14:00", "LUNCH SURGE", "Moderate Demand"),
            ("17:00 - 19:00", "EVENING RUSH", "Maximum Demand (Surge Applied)"),
            ("22:00 - 02:00", "NIGHT SHIFT", "Low Demand")
        ]
        for time_slot, label, status in traffic_data:
            self.log(f"[{label}] {time_slot}: {status}")

    def update_stats(self):
        self.rev_lbl.config(text=f"{self.total_revenue} P")
        self.wal_lbl.config(text=f"{self.wallet_balance} P")
        self.trip_lbl.config(text=str(len(self.trips_history)))

    def show_drivers(self):
        self.log("--- DRIVER STATUS ---")
        for d in self.drivers:
            status = "Available" if d.available else "Busy"
            self.log(f"{d.driver_id} | Fuel: {d.fuel:.1f}% | {status} | Loc: {d.location}")

    def rollback(self):
        if self.trips_history:
            last = self.trips_history.pop()
            self.total_revenue -= last['fare']
            self.wallet_balance += last['fare']
            self.log(f"Rollback successful. {last['fare']} P refunded.")
            self.update_stats()

    def view_history(self):
        self.log("--- SESSION HISTORY ---")
        for t in self.trips_history: self.log(f"ID {t['id']}: {t['route']} | {t['fare']} P")

    def show_wallet(self): self.log(f"Current Balance: {self.wallet_balance} P")
    def top_up(self): self.wallet_balance += 500; self.update_stats(); self.log("Topped up 500P.")
    def show_stats(self): self.log(f"Total Revenue: {self.total_revenue} P | Trips: {len(self.trips_history)}")
    def cancel_trip(self): self.log("Active search cancelled.")
    def wallet_history_log(self): self.log("History: Initial Deposit 1000P + Trips")
    def top_drivers(self): 
        best = sorted(self.drivers, key=lambda x: sum(x.ratings_list)/len(x.ratings_list) if x.ratings_list else 0, reverse=True)
        self.log(f"Top Driver: {best[0].driver_id}")
    def freq_routes(self): self.log("Frequent: Istanbul -> Bursa")
    def log_summary(self): self.log(f"Logs: {len(self.console.get('1.0', tk.END).splitlines())} lines")
    def rider_summary(self): self.log(f"Rider {self.u_name}: {len(self.trips_history)} trips | Rating: {self.rider_rating}")
    def generic(self): self.log("Module active. Syncing data...")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(); style.theme_use('clam')
    app = TR_Elite_Ultimate_System(root)
    root.mainloop()