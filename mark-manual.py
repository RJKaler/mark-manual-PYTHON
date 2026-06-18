#!/usr/bin/env python3

import subprocess
import time
import sys
import os

# Explicit path
LOG_FILE = "/home/richie/logs/markmanual.log"

def daemonize():
    """Detaches the script from the terminal."""
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    print("Marking process initiated. Moving to background...")
    
    try:
        pid = os.fork()
        if pid > 0:
            print(f"Success! Running as background job (PID: {pid}).")
            sys.exit(0)
    except OSError as e:
        print(f"Fork failed: {e}")
        sys.exit(1)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError:
        sys.exit(1)

def mark_packages():
    # Fetch list
    cmd = "apt list --installed 2>/dev/null | grep -v 'Listing...' | cut -d/ -f1"
    raw_output = subprocess.check_output(cmd, shell=True, text=True)
    packages = [p.strip() for p in raw_output.splitlines() if p.strip()]

    # Batch process
    batch_size = 100
    for i in range(0, len(packages), batch_size):
        batch = packages[i:i + batch_size]
        try:
            # Sudo is inside the subprocess call here
            subprocess.run(['sudo', 'apt-mark', 'manual'] + batch, check=True, capture_output=True)
            with open(LOG_FILE, "a") as f:
                f.write(f"[{time.ctime()}] Processed batch {i//batch_size + 1} ({len(batch)} pkgs).\n")
            time.sleep(1.5)
        except subprocess.CalledProcessError:
            continue

    with open(LOG_FILE, "a") as f:
        f.write(f"Finished at {time.ctime()}\n")

if __name__ == "__main__":
    # If not running as root, we ask sudo to run this script instance
    if os.geteuid() != 0:
        print("Requesting elevated privileges...")
        # This replaces the current process with a sudo version of itself
        os.execvp('sudo', ['sudo', sys.executable] + sys.argv)
    
    # If we reached here, we are root
    daemonize()
    mark_packages()
