import time
import random
import threading
import os

class LogSimulator(threading.Thread):
    def __init__(self, target_file="data/sim.log", interval=1.0):
        super().__init__()
        self.target_file = target_file
        self.interval = interval
        self.daemon = True
        self.running = False
        self.stop_event = threading.Event()
        
        self.normal_logs = [
            "Jul  1 09:01:05 server-01 com.apple.CDScheduler[43]: Thermal pressure state: 1 Memory pressure state: 0",
            "Jul  1 09:02:26 server-01 kernel[0]: ARPT: 620701.011328: AirPort_Brcm43xx::syncPowerState: WWEN[enabled]",
            "Jun 15 04:06:18 server-02 su(pam_unix)[21416]: session opened for user admin by (uid=0)",
            "Dec 10 06:55:46 node-3 sshd[24200]: Connection closed by 112.91.230.3",
            "Sun Dec 04 04:47:44 2005 [info] [client 127.0.0.1] File does not exist: /var/www/favicon.ico",
            "May 12 10:00:01 web-app-01 systemd[1]: Started Periodic Background Migration Service.",
            "May 12 10:05:22 db-master postgres[1234]: LOG: checkpoint starting: time",
            "May 12 10:05:25 db-master postgres[1234]: LOG: checkpoint complete: wrote 45 buffers"
        ]
        
        self.attack_logs = [
            "Jun 14 15:16:01 server-01 sshd(pam_unix)[19939]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4",
            "Jun 14 15:16:02 server-01 sshd(pam_unix)[19937]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4",
            "Jun 14 15:16:03 server-01 sshd(pam_unix)[19940]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4",
            "Jun 14 15:16:05 server-01 sshd(pam_unix)[19942]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=218.188.2.4",
            "2026-04-29 03:20:01.001 1234 ERROR nova.api.openstack [req-999] [instance: 1] Exploit attempt: SQL Injection detected in query parameter",
            "2026-04-29 03:21:30, Warning CBS [req-888] Unauthorized registry access attempt from 192.168.1.50",
            "May 12 11:00:01 server-01 sshd[5432]: Received disconnect from 10.0.0.5 port 1234:11: Bye Bye [preauth]"
        ]

    def run(self):
        self.running = True
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.target_file), exist_ok=True)
        
        with open(self.target_file, "a") as f:
            while not self.stop_event.is_set():
                # Randomly pick normal or attack
                if random.random() > 0.85:
                    # Malicious burst
                    num_attacks = random.randint(3, 8)
                    for _ in range(num_attacks):
                        line = random.choice(self.attack_logs)
                        f.write(line + "\n")
                        f.flush()
                        time.sleep(0.2)
                else:
                    line = random.choice(self.normal_logs)
                    f.write(line + "\n")
                    f.flush()
                
                time.sleep(random.uniform(self.interval * 0.5, self.interval * 1.5))
        
        self.running = False

    def stop(self):
        self.stop_event.set()
