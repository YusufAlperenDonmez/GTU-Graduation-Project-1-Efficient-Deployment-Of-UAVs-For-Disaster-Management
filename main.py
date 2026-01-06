# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator # <--- NEW: For integer axis ticks
import numpy as np
import sys
import config
import utils
import algorithms

class DisasterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UAV Deployment: Multi-Criterion Optimization Framework")
        
        # 1. FORCE MAXIMIZED WINDOW
        try:
            self.state('zoomed')
        except:
            self.attributes('-fullscreen', True) 
        
        # 2. SAFETY FLAGS
        self.app_running = True
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Escape>", self.on_close)

        # 3. DATA STORAGE
        self.map_data_history = {} 
        self.available_betas = [0.2, 0.3, 0.4, 0.5, 0.6] 
        
        # --- Layout ---
        self.left_panel = ttk.Frame(self, padding=10, width=350)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        self.right_panel = ttk.Frame(self)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Main Tabs
        self.main_tabs = ttk.Notebook(self.right_panel)
        self.main_tabs.pack(fill=tk.BOTH, expand=True)
        
        self.tab_map = ttk.Frame(self.main_tabs)
        self.tab_charts = ttk.Frame(self.main_tabs)
        
        self.main_tabs.add(self.tab_map, text="Map Visualization (Interactive)")
        self.main_tabs.add(self.tab_charts, text="Performance Analysis (Beta Sweep)")
        
        # Chart Sub-Tabs
        self.chart_tabs = ttk.Notebook(self.tab_charts)
        self.chart_tabs.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.page_conns = ttk.Frame(self.chart_tabs)
        self.page_uavs = ttk.Frame(self.chart_tabs)
        self.page_util = ttk.Frame(self.chart_tabs)
        self.page_time = ttk.Frame(self.chart_tabs)
        
        self.chart_tabs.add(self.page_conns, text="Number of Connections")
        self.chart_tabs.add(self.page_uavs, text="Number of Installed UAVs")
        self.chart_tabs.add(self.page_util, text="Weighted Utility")
        self.chart_tabs.add(self.page_time, text="Runtime Analysis")

        self.setup_controls()
        self.setup_map_tab()
        self.setup_chart_pages()

    def on_close(self, event=None):
        """Safe shutdown sequence."""
        self.app_running = False
        self.destroy() 
        sys.exit(0)    

    def setup_controls(self):
        """Builds the Input Form."""
        lbl_font = ("Arial", 11, "bold")
        ttk.Label(self.left_panel, text="Simulation Inputs", font=("Arial", 16, "bold")).pack(pady=15)
        
        # Scenario
        ttk.Label(self.left_panel, text="--- Scenario ---", foreground="gray").pack(pady=(10,5))
        
        ttk.Label(self.left_panel, text="Grid Size:", font=lbl_font).pack(anchor="w")
        self.var_grid = tk.StringVar(value="4x4")
        ttk.Combobox(self.left_panel, textvariable=self.var_grid, values=["3x3", "4x4", "5x5"], 
                     state="readonly", font=("Arial", 10)).pack(fill=tk.X, ipady=3)
        
        ttk.Label(self.left_panel, text="Number of Users (N):", font=lbl_font).pack(anchor="w", pady=(10,0))
        self.var_users = tk.IntVar(value=config.DEFAULT_N_USERS)
        ttk.Entry(self.left_panel, textvariable=self.var_users).pack(fill=tk.X, ipady=3)
        
        # Budget
        ttk.Label(self.left_panel, text="--- Budget & Costs ---", foreground="gray").pack(pady=(15,5))
        
        ttk.Label(self.left_panel, text="Cost per UAV:", font=lbl_font).pack(anchor="w")
        self.var_cost = tk.IntVar(value=config.DEFAULT_UAV_COST)
        ttk.Entry(self.left_panel, textvariable=self.var_cost).pack(fill=tk.X, ipady=3)

        ttk.Label(self.left_panel, text="Total Budget:", font=lbl_font).pack(anchor="w", pady=(10,0))
        self.var_budget = tk.IntVar(value=config.DEFAULT_BUDGET)
        ttk.Entry(self.left_panel, textvariable=self.var_budget).pack(fill=tk.X, ipady=3)

        # Constraints
        ttk.Label(self.left_panel, text="--- Constraints ---", foreground="gray").pack(pady=(15,5))
        
        row_load = ttk.Frame(self.left_panel)
        row_load.pack(fill=tk.X)
        
        col1 = ttk.Frame(row_load)
        col1.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(col1, text="Min Load:", font=("Arial", 9)).pack(anchor="w")
        self.var_gmin = tk.IntVar(value=config.GAMMA_MIN)
        ttk.Entry(col1, textvariable=self.var_gmin, width=10).pack(anchor="w")

        col2 = ttk.Frame(row_load)
        col2.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        ttk.Label(col2, text="Max Load:", font=("Arial", 9)).pack(anchor="w")
        self.var_gmax = tk.IntVar(value=config.GAMMA_MAX)
        ttk.Entry(col2, textvariable=self.var_gmax, width=10).pack(anchor="w")
        
        ttk.Label(self.left_panel, text="Max Signal Radius (m):", font=lbl_font).pack(anchor="w", pady=(10,0))
        self.var_dist = tk.IntVar(value=config.DEFAULT_MAX_DIST)
        ttk.Entry(self.left_panel, textvariable=self.var_dist).pack(fill=tk.X, ipady=3)

        # RUN BUTTON
        ttk.Button(self.left_panel, text="RUN BATCH SIMULATION", command=self.run_batch_simulation).pack(pady=30, fill=tk.X, ipady=10)

        # EXIT BUTTON
        btn_exit = tk.Button(self.left_panel, text="EXIT APP", bg="#ffcccc", fg="red", font=("Arial", 10, "bold"), command=self.on_close)
        btn_exit.pack(side=tk.BOTTOM, fill=tk.X, pady=20, ipady=5)

    def setup_map_tab(self):
        """Setup for the Map Tab with a Beta Slider."""
        self.map_ctrl_frame = ttk.Frame(self.tab_map, padding=10, relief=tk.RAISED)
        self.map_ctrl_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Label(self.map_ctrl_frame, text="View Simulation for Beta:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
        
        self.var_map_beta = tk.DoubleVar(value=0.2)
        self.scale_beta = tk.Scale(self.map_ctrl_frame, variable=self.var_map_beta, from_=0, to=4, 
                                   orient=tk.HORIZONTAL, length=300, showvalue=0, command=self.update_map_view)
        self.scale_beta.pack(side=tk.LEFT, padx=10)
        
        self.lbl_cur_beta = ttk.Label(self.map_ctrl_frame, text="Beta: 0.2", font=("Arial", 12))
        self.lbl_cur_beta.pack(side=tk.LEFT, padx=10)
        
        self.fig_map, (self.ax_opt, self.ax_heu) = plt.subplots(1, 2, figsize=(10, 5))
        self.canvas_map = FigureCanvasTkAgg(self.fig_map, master=self.tab_map)
        self.canvas_map.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_chart_pages(self):
        """Creates a dedicated Figure for each chart page."""
        self.fig_c1, self.ax_c1 = plt.subplots()
        self.cvs_c1 = FigureCanvasTkAgg(self.fig_c1, master=self.page_conns)
        self.cvs_c1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.fig_c2, self.ax_c2 = plt.subplots()
        self.cvs_c2 = FigureCanvasTkAgg(self.fig_c2, master=self.page_uavs)
        self.cvs_c2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.fig_c3, self.ax_c3 = plt.subplots()
        self.cvs_c3 = FigureCanvasTkAgg(self.fig_c3, master=self.page_util)
        self.cvs_c3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.fig_c4, self.ax_c4 = plt.subplots()
        self.cvs_c4 = FigureCanvasTkAgg(self.fig_c4, master=self.page_time)
        self.cvs_c4.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_batch_simulation(self):
        """Runs the algorithms 5 times."""
        try:
            base_inputs = {
                'N': self.var_users.get(),
                'uav_cost': self.var_cost.get(),
                'budget': self.var_budget.get(),
                'max_dist': self.var_dist.get(),
                'gamma_min': self.var_gmin.get(),
                'gamma_max': self.var_gmax.get()
            }
        except Exception:
            messagebox.showerror("Input Error", "Please ensure all fields are integers.")
            return

        grid_type = self.var_grid.get()
        users, uavs = utils.generate_scenario(base_inputs['N'], grid_type)
        
        self.available_betas = [0.2, 0.3, 0.4, 0.5, 0.6]
        self.map_data_history.clear()
        
        res_opt = {'conns': [], 'uavs': [], 'util': [], 'time': []}
        res_heu = {'conns': [], 'uavs': [], 'util': [], 'time': []}
        
        print(f"Starting Batch Simulation... (Max Load: {base_inputs['gamma_max']})")
        
        for b in self.available_betas:
            if not self.app_running: return 
            self.update()
            
            print(f"  Running Beta={b}...")
            current_inputs = base_inputs.copy()
            current_inputs['beta'] = b
            
            # Run Optimal
            opt_full = algorithms.solve_optimal(users, uavs, current_inputs)
            res_opt['conns'].append(sum(len(v) for v in opt_full[1].values()))
            res_opt['uavs'].append(len(opt_full[0]))
            res_opt['util'].append(opt_full[2])
            res_opt['time'].append(opt_full[3])

            # Run Heuristic
            heu_full = algorithms.solve_heuristic(users, uavs, current_inputs)
            res_heu['conns'].append(sum(len(v) for v in heu_full[1].values()))
            res_heu['uavs'].append(len(heu_full[0]))
            res_heu['util'].append(heu_full[2])
            res_heu['time'].append(heu_full[3])
            
            self.map_data_history[b] = {
                'users': users,
                'uavs': uavs,
                'opt': opt_full,
                'heu': heu_full
            }

        if not self.app_running: return

        # Plot Charts
        # --- INTEGER TICK UPDATE: Added integer_ticks=True for Counts and Utility ---
        self.plot_bar_chart(self.ax_c1, self.cvs_c1, self.available_betas, res_opt['conns'], res_heu['conns'], 
                            "Total Connections", "Count", integer_ticks=True)
                            
        self.plot_bar_chart(self.ax_c2, self.cvs_c2, self.available_betas, res_opt['uavs'], res_heu['uavs'], 
                            "Installed UAVs", "Count", integer_ticks=True)
                            
        self.plot_bar_chart(self.ax_c3, self.cvs_c3, self.available_betas, res_opt['util'], res_heu['util'], 
                            "Weighted Utility", "Score", integer_ticks=True)
                            
        self.plot_bar_chart(self.ax_c4, self.cvs_c4, self.available_betas, res_opt['time'], res_heu['time'], 
                            "Runtime", "Seconds", log_scale=True)
        
        self.scale_beta.set(0) 
        self.update_map_view(0)
        
        messagebox.showinfo("Done", "Batch Simulation Complete.")

    def update_map_view(self, val):
        if not self.map_data_history:
            return
        idx = int(float(val))
        if idx >= len(self.available_betas): idx = len(self.available_betas) - 1
        beta = self.available_betas[idx]
        self.lbl_cur_beta.config(text=f"Beta: {beta}")
        data = self.map_data_history[beta]
        self.plot_map(self.ax_opt, f"Optimal (Beta={beta})", data['users'], data['uavs'], data['opt'][0], data['opt'][1])
        self.plot_map(self.ax_heu, f"Proposed (Beta={beta})", data['users'], data['uavs'], data['heu'][0], data['heu'][1])
        self.canvas_map.draw()

    def plot_bar_chart(self, ax, canvas, x_vals, y_opt, y_heu, title, ylabel, log_scale=False, integer_ticks=False):
        ax.clear()
        x = np.arange(len(x_vals))
        
        # Superimposed Bars
        ax.bar(x, y_opt, width=0.6, label='Optimal', color='black', align='center')
        ax.bar(x, y_heu, width=0.3, label='Proposed', color='gray', align='center')
        
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_xlabel('Beta', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(x_vals)
        ax.legend(fontsize=10, loc='upper right')
        
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        
        # --- FIX: Force Integer Ticks if requested ---
        if log_scale:
            ax.set_yscale('log')
        elif integer_ticks:
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            
        canvas.draw()

    def plot_map(self, ax, title, users, uavs, active_idx, conns_dict):
        ax.clear()
        ax.set_title(title)
        
        buffer = 50 
        ax.set_xlim(-buffer, config.GRID_WIDTH + buffer)
        ax.set_ylim(-buffer, config.GRID_HEIGHT + buffer)
        ax.set_aspect('equal', adjustable='box')
        ax.grid(True, linestyle='--', alpha=0.3)
        
        ax.scatter(users[:,0], users[:,1], c='blue', s=20, alpha=0.6, label='Users')
        ax.scatter(uavs[:,0], uavs[:,1], c='lightgray', marker='s', s=60, label='Potential UAV')
        
        if active_idx:
            active_coords = uavs[active_idx]
            ax.scatter(active_coords[:,0], active_coords[:,1], c='red', marker='s', s=120, label='Active UAV', zorder=5)
            for m_idx, user_indices in conns_dict.items():
                start = uavs[m_idx]
                for u_idx in user_indices:
                    end = users[u_idx]
                    ax.plot([start[0], end[0]], [start[1], end[1]], 'r-', linewidth=1.0, alpha=0.4, zorder=1)
        
        ax.legend(loc='upper right', fontsize=9)

if __name__ == "__main__":
    app = DisasterApp()
    app.mainloop()