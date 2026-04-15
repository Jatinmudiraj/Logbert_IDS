import time
import os
import random

def generate_logs():
    print("[*] Starting Log Simulator...")
    samples = [
        "sshd[2245]: Accepted password for geeta from 192.168.1.10",
        "sshd[2245]: pam_unix(sshd:session): session opened for user geeta",
        "systemd[1]: Started Session 15 of user geeta.",
        "CRON[3312]: (root) CMD (run-parts /etc/cron.hourly)",
        "sshd[4567]: Invalid user admin from 8.8.8.8",
        "sshd[4567]: pam_unix(sshd:auth): authentication failure; UID=0",
        "sshd[8891]: Failed password for root from 1.1.1.1 port 54321",
        "sudo: geeta : TTY=pts/0 ; PWD=/home/geeta ; USER=root ; COMMAND=/usr/bin/ls"
    ]
    
    auth_log = "/var/log/auth.log"
    if not os.access(auth_log, os.W_OK):
        print("[!] No write access to /var/log/auth.log. Simulating to local 'data/sim.log' instead.")
        os.makedirs("data", exist_ok=True)
        auth_log = "data/sim.log"

    count = 0
    while True:
        log = samples[random.randint(0, len(samples)-1)]
        ts = time.strftime("%b %d %H:%M:%S")
        entry = f"{ts} ubt-machine {log}\n"
        
        with open(auth_log, "a") as f:
            f.write(entry)
        
        print(f"[+] Injected: {entry.strip()}")
        count += 1
        time.sleep(random.uniform(1, 4))

if __name__ == "__main__":
    generate_logs()
