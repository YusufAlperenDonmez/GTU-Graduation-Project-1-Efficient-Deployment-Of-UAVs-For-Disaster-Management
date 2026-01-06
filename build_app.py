# build_app.py
import PyInstaller.__main__
import os

print("--- STARTING BUILD PROCESS (NO CPLEX) ---")

PyInstaller.__main__.run([
    'main.py',
    '--name=UAV_Disaster_Sim',
    '--onefile',
    '--windowed',
    '--noconfirm',
    '--clean',
    # We ONLY need to hide/collect pulp now
    '--hidden-import=pulp',
    '--collect-all=pulp'  # Crucial: This grabs the default CBC solver binary
])

print("--- BUILD COMPLETE ---")
print(f"Your executable is located in: {os.path.abspath('dist')}")