#!/usr/bin/env python3
import subprocess
import sys
import os

print("Starting Affiliate Link Generator...")
try:
    # Change to source_code directory
    source_dir = os.path.join(os.path.dirname(__file__), 'source_code')
    app_script = os.path.join(source_dir, 'run_app.py')
    
    if os.path.exists(app_script):
        subprocess.run([sys.executable, app_script])
    else:
        print(f"Error: {app_script} not found")
except Exception as e:
    print(f"Error: {e}")
    
input("Press Enter to exit...")