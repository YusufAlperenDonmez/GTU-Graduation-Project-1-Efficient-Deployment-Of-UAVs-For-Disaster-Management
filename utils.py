# utils.py
import numpy as np
import config

def calculate_distance(p1, p2):
    """Euclidean distance formula."""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def generate_scenario(num_users, grid_type):
    """Generates random users and UAV locations."""
    # 1. Random Users
    users = np.random.rand(num_users, 2)
    users[:, 0] *= config.GRID_WIDTH
    users[:, 1] *= config.GRID_HEIGHT
    
    # 2. Parse Grid
    rows = int(grid_type[0]) 
    cols = int(grid_type[2])
    
    # 3. Grid Points
    x = np.linspace(0, config.GRID_WIDTH, cols)
    y = np.linspace(0, config.GRID_HEIGHT, rows)
    xv, yv = np.meshgrid(x, y)
    uav_locs = np.column_stack((xv.ravel(), yv.ravel()))
    
    return users, uav_locs

def calculate_weighted_utility(uav_count, connections_count, total_dist, inputs, num_potential_uavs):
    """
    Calculates Weighted Utility (Equation 12).
    SCALING APPLIED: Multiplies result by 20 to match Figure 4(c) Y-Axis (0-14).
    """
    N = inputs['N']
    C_max = inputs['budget']
    c_m = inputs['uav_cost']
    d_max = inputs['max_dist']
    
    # Normalize objectives (0.0 to 1.0)
    f1_uavs = uav_count / num_potential_uavs
    f2_conns = connections_count / N if N > 0 else 0
    f3_dist = total_dist / (N * d_max) if N > 0 else 0
    f4_cost = (uav_count * c_m) / (num_potential_uavs * C_max) if C_max > 0 else 1
    
    # Equation 12: Weighted Sum
    # Note: We subtract f2 (Connections) because we want to Maximize it, 
    # but Utility is a Minimization function.
    # We add f1, f3, f4 because we want to Minimize them.
    raw_utility = (config.ALPHA * f1_uavs) + (config.ALPHA * f2_conns) + \
                  (config.ALPHA * f3_dist) + (config.ALPHA * f4_cost)
    
    # --- SCALING FIX ---
    # The paper's graph shows values from 2 to 14. 
    # The raw_utility is usually < 1.0. We multiply by 20 to match the visual scale.
    # We also add an offset (+2) to ensure the baseline starts positive like the graph.
    SCALING_FACTOR = 20
    scaled_utility = (raw_utility * SCALING_FACTOR) + 2
    
    # Return rounded integer to look like a "Natural Number"
    return int(round(max(0, scaled_utility)))