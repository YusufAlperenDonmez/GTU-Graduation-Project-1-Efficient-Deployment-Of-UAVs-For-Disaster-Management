UAV Deployment for Disaster Management Simulation

This project provides a comprehensive simulation and optimization system for the efficient deployment of Unmanned Aerial Vehicles (UAVs) for disaster management. The methodology is based on a Multi-Criterion Optimization Model utilizing Integer Linear Programming (ILP) and heuristic algorithms.
Reference Paper

Efficient deployment of UAVs for disaster management: A multi-criterion optimization approach

    Journal: Computer Communications (Elsevier), 2021 

Authors: Rooha Masroor, Muhammad Naeem, Waleed Ejaz

DOI: 10.1016/j.comcom.2021.07.006

Project Goal

The primary objective of this project is to develop a comprehensive decision-support tool that can:

    Determine the optimal locations for UAVs to act as mobile helping units in disaster scenarios (floods, earthquakes, fires) .

Maximize user connectivity while minimizing both the number of deployed UAVs and the deployment cost .

    Provide a desktop-based GUI for interactive scenario building, parameter adjustment, and comparative results visualization.

Key Features

    Multi-Objective Optimization: Balances four competing objectives: minimizing UAV count, maximizing user connections, minimizing user-to-UAV distance, and minimizing cost .

Interactive Simulation Interface: Allows users to configure grid environments and constraints directly using a Tkinter-based dashboard.

Dual Optimization Methods: Provides solutions using both:

    Optimal Solution: Uses Integer Linear Programming (ILP) solved via Branch & Bound (B&B) for mathematically optimal results .

Proposed Heuristic: A low-complexity greedy algorithm for rapid decision-making in time-critical scenarios.

Performance Analysis: Includes a batch simulation feature to compare algorithms across different connectivity targets (β).

Visual Analytics: Generates comparative bar charts for connection counts, installed UAVs, and weighted utility scores.

Usage

How to Use the Application:

    Configure Inputs: Set the simulation parameters on the left panel, including Grid Size (e.g., 4x4), Number of Victims (N), and UAV Cost/Budget.

    Define Constraints: Adjust the Load Balancing constraints (γmin​ and γmax​) and the Maximum Signal Radius.

    Run Simulation: Click the "RUN BATCH SIMULATION" button. This executes the solvers across a range of Beta values (0.2 to 0.6).

    Visualize Map: Switch to the "Map Visualization" tab to see the spatial deployment of UAVs and user connections. Use the slider to toggle between different Beta scenarios.

    Analyze Results: Switch to the "Performance Analysis" tab to view detailed charts comparing the Optimal vs. Proposed Heuristic methods.

Model Outputs

The optimization model generates the following key outputs:

    The total number of UAVs installed to cover the disaster area.

The total number of user connections established.

A Weighted Utility Score that combines cost, distance, and coverage into a single metric .

Runtime analysis comparing the speed of the Optimal vs. Heuristic algorithms.

A full visualization of active UAV locations and their connections to specific users.

Acknowledgements

This project was developed as a Graduation Project for the CSE 495 / 496 courses at Gebze Technical University.

    Project Supervisor: Prof. Dr. Didem Gözüpek Kocaman

    Project Student: Yusuf Alperen Dönmez

License

This project is licensed under the MIT License. See the LICENSE file for more details.
