from flask import Flask, render_template, request, jsonify
from city import City
from Driver import Driver
from Rider import Rider
from Trip import Trip
from DispatchEngine import DispatchEngine
from RollbackManager import RollbackManager
from RideShareSystem import RideShareSystem

app = Flask(__name__)

# Initialize backend
city = City()
dispatcher = DispatchEngine([])  # start with empty driver list
rollback = RollbackManager()
system = RideShareSystem(city, dispatcher, rollback)

# Add some drivers
driver1 = Driver(1, "A", "Zone1")
driver2 = Driver(2, "B", "Zone2")
dispatcher.drivers.extend([driver1, driver2])

trip_counter = 1
trip_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/request_ride', methods=['POST'])
def request_ride():
    global trip_counter
    data = request.get_json()
    pickup = data['pickup']
    dropoff = data['dropoff']

    rider = Rider(trip_counter, pickup, dropoff)
    driver = dispatcher.assign_driver()  # assign first available driver

    if not driver:
        return jsonify({'success': False, 'message': 'No drivers available'})

    trip = Trip(trip_counter, rider, driver)
    system.trips.append(trip)
    trip_history.append({
        'trip_id': trip_counter,
        'rider': rider.rider_id,
        'driver': driver.driver_id,
        'pickup': pickup,
        'dropoff': dropoff,
        'state': trip.state
    })

    trip_counter += 1
    eta = 5  # simulated minutes

    return jsonify({'success': True, 'driver': driver.driver_id, 'eta': eta, 'trip_id': trip.trip_id})

@app.route('/view_history')
def view_history():
    return jsonify(trip_history)

@app.route('/cancel_trip', methods=['POST'])
def cancel_trip():
    data = request.get_json()
    trip_id = data['trip_id']

    trip = next((t for t in system.trips if t.trip_id == trip_id), None)
    if not trip:
        return jsonify({'success': False, 'message': 'Trip not found'})

    system.cancel_trip(trip)
    for h in trip_history:
        if h['trip_id'] == trip_id:
            h['state'] = trip.state

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
