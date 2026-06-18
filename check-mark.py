#!/usr/bin/env python3

import subprocess
import time
import sys
import os

LOG_FILE = "/home/richie/logs/markmanual.log"

def elevate():
    """Ensure the script is running as root."""
    if os.geteuid() != 0:
        print("Privileges required. Requesting sudo...")
        os.execvp('sudo', ['sudo', sys.executable] + sys.argv)

def mark_packages():
    # 1. Fetch package list
    print("Fetching installed package list...")
    cmd = "apt list --installed 2>/dev/null | grep -v 'Listing...' | cut -d/ -f1"
    raw_output = subprocess.check_output(cmd, shell=True, text=True)
    packages = [p.strip() for p in raw_output.splitlines() if p.strip()]
    
    total = len(packages)
    batch_size = 100
    
    print(f"Total packages to process: {total}")
    print("---------------------------------------")

    # 2. Loop until finished
    i = 0
    while i < total:
        batch = packages[i : i + batch_size]
        
        # Output status to terminal
        print(f"[{time.strftime('%H:%M:%S')}] Marking {i+1} to {min(i+batch_size, total)} of {total}...")
        
        try:
            subprocess.run(['apt-mark', 'manual'] + batch, check=True, capture_output=True)
            
            # Log progress
            with open(LOG_FILE, "a") as f:
                f.write(f"[{time.ctime()}] Processed {len(batch)} packages.\n")
            
            # Thermal breather
            time.sleep(1.5)
            i += batch_size
            
        except subprocess.CalledProcessError as e:
            print(f"Error encountered at batch {i}: {e}")
            break
            
    print("---------------------------------------")
    print("All packages marked successfully.")

if __name__ == "__main__":
    # 1. Elevate
    elevate()
    # 2. Run in foreground
    mark_packages()
