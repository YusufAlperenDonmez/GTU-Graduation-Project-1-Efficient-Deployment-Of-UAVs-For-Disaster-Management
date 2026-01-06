# config.py

# --- Default Simulation Environment ---
GRID_WIDTH = 1000   # Meters (X-axis limit)
GRID_HEIGHT = 1000  # Meters (Y-axis limit)

# --- Default Constraints (Can be overridden in GUI) ---
DEFAULT_N_USERS = 50       # Number of victims (N)
DEFAULT_BETA = 0.5         # Min coverage percentage (Beta) [cite: 317]
DEFAULT_UAV_COST = 100     # Cost per drone (c_m)
DEFAULT_BUDGET = 1000      # Total Budget (C_max) [cite: 323]
DEFAULT_MAX_DIST = 300     # Max connection range (d_max) [cite: 322]

# --- Hard Constraints for Load Balancing ---
# These prevent over/under-loading drones [cite: 319-320]
GAMMA_MIN = 2   
GAMMA_MAX = 15  

# Optimization Weights (Eq 12) [cite: 525]
# Used to calculate the "Score" of the solution
ALPHA = 0.25