# rider_feedback.py
# ------------------- Rider Feedback, Wallet & Payment Module -------------------

from datetime import datetime
import random

class WalletManager:
    """Manage rider wallets, payments, and top-ups"""

    def __init__(self):
        self.wallets = {}  # {rider_id: balance}
        self.transactions = {}  # {rider_id: [{"type":, "amount":, "trip":, "timestamp":}]}

    def initialize_wallet(self, rider_id, initial_amount=500):
        self.wallets[rider_id] = initial_amount
        self.transactions[rider_id] = []
        print(f"Wallet initialized for Rider {rider_id}. Balance: {initial_amount} PKR")

    def top_up(self, rider_id, amount):
        if amount <= 0:
            print("Top-up amount must be greater than zero.")
            return False
        self.wallets[rider_id] += amount
        self.transactions[rider_id].append({
            "type": "topup",
            "amount": amount,
            "trip": None,
            "timestamp": datetime.now()
        })
        print(f"Rider {rider_id} wallet topped up by {amount} PKR. Current balance: {self.wallets[rider_id]}")
        return True

    def pay(self, rider_id, required_amount):
        balance = self.wallets.get(rider_id, 0)
        if balance < required_amount:
            print(f"Insufficient balance! Wallet: {balance} PKR | Required: {required_amount} PKR")
            print("Please top up your wallet to complete the payment.")
            return False
        self.wallets[rider_id] -= required_amount
        self.transactions[rider_id].append({
            "type": "payment",
            "amount": required_amount,
            "trip": None,
            "timestamp": datetime.now()
        })
        print(f"Payment of {required_amount} PKR successful. Remaining balance: {self.wallets[rider_id]}")
        return True

    def get_balance(self, rider_id):
        return self.wallets.get(rider_id, 0)

    def wallet_history(self, rider_id):
        print(f"\nWallet History for Rider {rider_id}:")
        if rider_id not in self.transactions or not self.transactions[rider_id]:
            print("No transactions found.")
            return
        for t in self.transactions[rider_id]:
            ts = t["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            print(f"{ts} | {t['type'].capitalize()} | Amount: {t['amount']} | Trip: {t['trip']}")

# ------------------- Rider Feedback System -------------------

class FeedbackManager:
    """Collect and analyze feedback for riders and drivers"""

    def __init__(self):
        self.rider_feedback = {}  # {rider_id: [ratings]}
        self.driver_feedback = {}  # {driver_id: [ratings]}
        self.comments = {}  # {rider_id: [comments]}

    def rate_rider(self, rider_id, rating, comment=None):
        if rating < 1 or rating > 5:
            print("Rating must be 1-5 stars.")
            return False
        self.rider_feedback.setdefault(rider_id, []).append(rating)
        if comment:
            self.comments.setdefault(rider_id, []).append(comment)
        print(f"Rider {rider_id} rated {rating} stars.")
        return True

    def rate_driver(self, driver_id, rating, comment=None):
        if rating < 1 or rating > 5:
            print("Rating must be 1-5 stars.")
            return False
        self.driver_feedback.setdefault(driver_id, []).append(rating)
        if comment:
            self.comments.setdefault(driver_id, []).append(comment)
        print(f"Driver {driver_id} rated {rating} stars.")
        return True

    def show_rider_feedback(self, rider_id):
        ratings = self.rider_feedback.get(rider_id, [])
        if not ratings:
            print(f"No ratings for Rider {rider_id}")
            return
        avg = sum(ratings)/len(ratings)
        print(f"Rider {rider_id} Average Rating: {avg:.1f} ({len(ratings)} ratings)")
        if rider_id in self.comments:
            for c in self.comments[rider_id]:
                print(f"Comment: {c}")

    def show_driver_feedback(self, driver_id):
        ratings = self.driver_feedback.get(driver_id, [])
        if not ratings:
            print(f"No ratings for Driver {driver_id}")
            return
        avg = sum(ratings)/len(ratings)
        print(f"Driver {driver_id} Average Rating: {avg:.1f} ({len(ratings)} ratings)")
        if driver_id in self.comments:
            for c in self.comments[driver_id]:
                print(f"Comment: {c}")

# ------------------- Random Rider Analytics -------------------

class RiderAnalytics:
    """Analyze rider patterns and feedback"""

    def __init__(self, feedback_manager, wallet_manager):
        self.feedback_manager = feedback_manager
        self.wallet_manager = wallet_manager
        self.trip_count = {}  # {rider_id: number of trips}
        self.payment_history = {}  # {rider_id: [payments]}

    def record_trip(self, rider_id, payment_amount):
        self.trip_count[rider_id] = self.trip_count.get(rider_id, 0) + 1
        self.payment_history.setdefault(rider_id, []).append(payment_amount)

    def top_riders(self, top_n=5):
        sorted_riders = sorted(self.trip_count.items(), key=lambda x: x[1], reverse=True)
        print(f"\nTop {top_n} Riders by Trips:")
        for r_id, count in sorted_riders[:top_n]:
            print(f"Rider {r_id}: {count} trips")

    def rider_payment_stats(self, rider_id):
        payments = self.payment_history.get(rider_id, [])
        if not payments:
            print(f"No payments for Rider {rider_id}")
            return
        total = sum(payments)
        avg = total / len(payments)
        print(f"Rider {rider_id} Total Paid: {total} PKR | Average per trip: {avg:.2f} PKR | Trips: {len(payments)}")

# ------------------- Advanced Suggestions & Promo -------------------

class RiderPromotions:
    """Manage promo codes and discounts for riders"""

    def __init__(self):
        self.promo_codes = {"DISCOUNT10": 0.9, "FLAT50": 50}

    def apply_promo(self, fare, code):
        if code not in self.promo_codes:
            print("Invalid promo code.")
            return fare
        disc = self.promo_codes[code]
        if disc < 1:
            fare *= disc
        else:
            fare -= disc
        return max(fare, 0)

    def add_promo(self, code, discount):
        if code in self.promo_codes:
            print("Promo code already exists.")
            return False
        self.promo_codes[code] = discount
        print(f"Promo {code} added.")
        return True

# ------------------- Example Utilities -------------------

def simulate_rider_activity(wallet_manager, feedback_manager, analytics):
    """Simulate multiple rider actions"""
    rider_ids = ["A","B","C","D"]
    for rider in rider_ids:
        wallet_manager.initialize_wallet(rider)
        payment = random.randint(50, 200)
        wallet_manager.pay(rider, payment)
        analytics.record_trip(rider, payment)
        feedback_manager.rate_rider(rider, random.randint(3,5), comment="Good experience!")

def print_rider_summary(analytics, feedback_manager, wallet_manager):
    print("\n--- Rider Summary ---")
    for rider in ["A","B","C","D"]:
        print(f"\nRider {rider}:")
        print(f"Wallet Balance: {wallet_manager.get_balance(rider)} PKR")
        analytics.rider_payment_stats(rider)
        feedback_manager.show_rider_feedback(rider)
        wallet_manager.wallet_history(rider)

# ------------------- End of rider_feedback.py -------------------
