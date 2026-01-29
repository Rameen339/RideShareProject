# RideShareProject
Python Ride-Sharing Dispatch &amp; Trip Management System
1.Graph Representation and Routing Approach
Graph Representation
The system models the map of Turkey as a Weighted Undirected Graph.

Nodes : Represent cities (e.g., Istanbul, Ankara, Izmir).
Edges : Represent highways/roads connecting the cities.
Weights : Represent the physical distance (km) or cost between two cities.
The graph is implemented using an Adjacency List. This is memory efficient for road networks which are typically sparse graphs (cities usually connect to only a few neighbors, not all other cities).
Routing Algorithm
To determine the route between a Pickup location (P) and a Dropoff location (D), the system utilizes Dijkstra’s Algorithm.
Objective: Find the path with the minimum sum of weights (shortest distance).
Dispatch Logic:
When a ride is requested, the system calculates the shortest path from P to D for the rider.
Simultaneously, it calculates the distance from every available Driver's current location to P
The driver with the shortest distance to P (who meets fuel requirements) is assigned.
2. Trip State Machine Design
The lifecycle of a trip is managed through a specific set of states to ensure data consistency and logical flow.
States
PENDING: The trip is created, a driver is assigned, but the journey has not started.
IN_PROGRESS: The driver has picked up the rider and is moving through the path nodes. This is simulated via the threading module in main.py.
COMPLETED: The driver has arrived at the destination, fuel has been consumed, and the rider is prompted for payment.
CANCELLED: The trip was aborted by the user before completion.
3. Rollback Strategy
The system implements a LIFO (Last-In, First-Out) Transactional Rollback to handle errors or user disputes.
Mechanism
History Stack: All completed trips are stored in a global list trips_history. This acts as a stack data structure.
Rollback Manager: When the "Rollback Last Trip" (Option 4) command is issued:
The system identifies the most recently pushed Trip object from trips_history.
Financial Reversal: The fare amount is refunded to the Rider's wallet (wallets[u_id] += last.fare).
Record Removal: The trip is popped (removed) from the history stack (trips_history.pop()).
Note: In the current implementation, fuel consumed and driver displacement are not physically reversed (the car stays at the dropoff), but the financial transaction is fully voided.
4. Time and Space Complexity Analysis
Time Complexity
Routing (Shortest Path): O(E + V \log V)
The system uses Dijkstra’s algorithm with a priority queue (heap). This is the standard efficiency for finding the shortest path in a weighted graph.
Dispatching: O(K . (E + V \log V))
Where K is the number of drivers. To find the nearest driver, the system may need to calculate the shortest path from every available driver (K) to the pickup point.
Simulation: O(D)
The simulation loop runs linearly proportional to the total distance (D) of the trip to simulate minute-by-minute travel.
Rollback: O(1)
Popping the last item from a list (stack) and performing a dictionary lookup to refund the wallet are constant time operations.
Space Complexity
Graph Storage: O(V + E)
The Adjacency List stores every city (V) and every road connection (E) exactly once. This is significantly more efficient than an Adjacency Matrix (O(V^2)).
Trip History: O(T)
Where T is the total number of trips taken since the server started. The trips_history list grows linearly as the application runs.
Entity Storage: O(N)
Storage for Driver and Rider objects is linear relative to the number of users and drivers registered in the system.

