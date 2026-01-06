# algorithms.py
import pulp
import time
import numpy as np
import config
import utils

def solve_optimal(users, uav_locs, inputs):
    """
    Algorithm 1: Branch and Bound (Optimal).
    
    CHANGE: Time Limit Removed. 
    This will run until the absolute best solution is found.
    """
    start_time = time.time()
    
    num_users = len(users)
    num_uavs = len(uav_locs)
    
    # Inputs
    beta = inputs['beta']
    uav_cost = inputs['uav_cost']
    budget = inputs['budget']
    max_dist = inputs['max_dist']
    
    prob = pulp.LpProblem("UAV_Deployment", pulp.LpMinimize)
    
    # Variables
    x = pulp.LpVariable.dicts("x", range(num_uavs), cat='Binary')
    y = pulp.LpVariable.dicts("y", (range(num_uavs), range(num_users)), cat='Binary')
    
    # Pre-calculate distances
    dists = np.zeros((num_uavs, num_users))
    for m in range(num_uavs):
        for n in range(num_users):
            dists[m][n] = utils.calculate_distance(users[n], uav_locs[m])

    # --- OBJECTIVE FUNCTION ---
    # Multiply UAV Cost by 1000 so the solver prioritizes saving drones over distance.
    PRIORITY_WEIGHT = 1000 
    prob += (pulp.lpSum(x[m] for m in range(num_uavs)) * uav_cost * PRIORITY_WEIGHT) + \
            (pulp.lpSum(dists[m][n] * y[m][n] for m in range(num_uavs) for n in range(num_users)))

    # --- CONSTRAINTS ---
    
    # C1: Beta Coverage
    prob += pulp.lpSum(y[m][n] for m in range(num_uavs) for n in range(num_users)) >= beta * num_users
    
    # C7: Budget
    prob += (pulp.lpSum(x[m] for m in range(num_uavs)) * uav_cost) <= budget

    for m in range(num_uavs):
        for n in range(num_users):
            # C2: Validity
            prob += y[m][n] <= x[m]
        
        # C3 & C4: Dynamic Load Balancing
        prob += pulp.lpSum(y[m][n] for n in range(num_users)) <= inputs['gamma_max'] * x[m]
        prob += pulp.lpSum(y[m][n] for n in range(num_users)) >= inputs['gamma_min'] * x[m]

    for n in range(num_users):
        # C5: Single Connection
        prob += pulp.lpSum(y[m][n] for m in range(num_uavs)) <= 1
        
        # C6: Max Distance
        for m in range(num_uavs):
            if dists[m][n] > max_dist:
                prob += y[m][n] == 0

    # --- SOLVER CONFIGURATION (UNLIMITED) ---
    try:
        # REMOVED: timeLimit=5, options=['ratio 0.05']
        # Now it runs until optimality is proven.
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
    except:
        return [], {}, 0, 0

    # Check Validity
    if pulp.LpStatus[prob.status] != 'Optimal' and pulp.LpStatus[prob.status] != 'Feasible':
        return [], {}, 0, time.time() - start_time

    # Extract Results
    active_indices = [m for m in range(num_uavs) if pulp.value(x[m]) is not None and pulp.value(x[m]) > 0.5]
    connections_dict = {}
    total_dist = 0
    
    for m in active_indices:
        user_list = []
        for n in range(num_users):
            if pulp.value(y[m][n]) is not None and pulp.value(y[m][n]) > 0.5:
                user_list.append(n)
                total_dist += dists[m][n]
        connections_dict[m] = user_list

    conn_count = sum(len(u) for u in connections_dict.values())
    utility = utils.calculate_weighted_utility(len(active_indices), conn_count, total_dist, inputs, num_uavs)
    
    return active_indices, connections_dict, utility, time.time() - start_time

def solve_heuristic(users, uav_locs, inputs):
    """
    Algorithm 3: Greedy Heuristic with Set Cover Logic.
    Stops deploying as soon as Beta target is reached.
    """
    start_time = time.time()
    
    num_users = len(users)
    num_uavs = len(uav_locs)
    
    # Inputs
    beta = inputs['beta']
    max_dist = inputs['max_dist']
    budget = inputs['budget']
    uav_cost = inputs['uav_cost']
    g_min = inputs['gamma_min']
    g_max = inputs['gamma_max']
    
    # C1 Target
    target_users = int(np.ceil(beta * num_users))
    
    # Step 1: Map potentials
    potential_uav_users = {m: [] for m in range(num_uavs)}
    for m in range(num_uavs):
        for n in range(num_users):
            dist = utils.calculate_distance(users[n], uav_locs[m])
            if dist <= max_dist:
                potential_uav_users[m].append((n, dist))
    
    # Step 2: Sort by Popularity
    valid_uavs = []
    for m, user_list in potential_uav_users.items():
        if len(user_list) >= g_min:
            valid_uavs.append(m)
            
    valid_uavs.sort(key=lambda m: len(potential_uav_users[m]), reverse=True)
    
    # Step 3: Deployment
    active_indices = []
    connections_dict = {}
    covered_users_set = set()
    current_cost = 0
    final_dist = 0
    
    for m in valid_uavs:
        # STOP if Target Met
        if len(covered_users_set) >= target_users:
            break
        if current_cost + uav_cost > budget:
            break
            
        possible_users = potential_uav_users[m]
        possible_users.sort(key=lambda x: x[1])
        
        new_connections = []
        for n, dist in possible_users:
            if n not in covered_users_set:
                new_connections.append((n, dist))
        
        # Max Load Pruning
        if len(new_connections) > g_max:
            new_connections = new_connections[:g_max]
        
        # Deploy if meaningful
        if len(new_connections) > 0:
            if len(new_connections) >= g_min:
                current_cost += uav_cost
                active_indices.append(m)
                
                user_ids = [u[0] for u in new_connections]
                connections_dict[m] = user_ids
                
                for n, dist in new_connections:
                    covered_users_set.add(n)
                    final_dist += dist

    duration = time.time() - start_time
    conn_count = len(covered_users_set)
    utility = utils.calculate_weighted_utility(len(active_indices), conn_count, final_dist, inputs, num_uavs)
    
    return active_indices, connections_dict, utility, duration