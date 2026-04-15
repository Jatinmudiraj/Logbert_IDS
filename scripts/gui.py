import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import os
import json
import time

class IDSGui:
    def __init__(self, root):
        self.root = root
        self.root.title("LogBERT IDS | Real-time Neural Defense")
        self.root.geometry("1000x700")
        self.root.configure(bg="#0d1117")

        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#161b22", foreground="#c9d1d9", fieldbackground="#161b22", borderwidth=0)
        style.map("Treeview", background=[('selected', '#58a6ff')])

        # Header
        header = tk.Frame(root, bg="#161b22", height=60)
        header.pack(fill=tk.X)
        header_label = tk.Label(header, text="LOGBERT IDS", font=("Arial", 20, "bold"), fg="#58a6ff", bg="#161b22")
        header_label.pack(side=tk.LEFT, padx=20, pady=10)

        self.status_label = tk.Label(header, text="● SYSTEM IDLE", font=("Arial", 12), fg="#8b949e", bg="#161b22")
        self.status_label.pack(side=tk.RIGHT, padx=20)

        # Main Layout
        main_frame = tk.Frame(root, bg="#0d1117")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Panel (Stats)
        left_panel = tk.Frame(main_frame, bg="#161b22", width=250, bd=1, relief=tk.FLAT)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="STATISTICS", font=("Arial", 10, "bold"), fg="#8b949e", bg="#161b22").pack(pady=(20, 10))
        
        self.total_logs = tk.StringVar(value="0")
        self.anomalies = tk.StringVar(value="0")
        
        self.create_stat(left_panel, "Total Logs", self.total_logs)
        self.create_stat(left_panel, "Anomalies", self.anomalies, color="#ff7b72")

        # Right Panel (Logs & Alerts)
        right_panel = tk.Frame(main_frame, bg="#0d1117")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Log Stream
        tk.Label(right_panel, text="LIVE LOG STREAM", font=("Arial", 10, "bold"), fg="#8b949e", bg="#0d1117").pack(anchor=tk.W)
        self.log_area = scrolledtext.ScrolledText(right_panel, height=15, bg="#0d1117", fg="#c9d1d9", font=("Consolas", 10), insertbackground="white")
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=(5, 15))

        # Alert List
        tk.Label(right_panel, text="HIGH-CONFIDENCE ALERTS", font=("Arial", 10, "bold"), fg="#ff7b72", bg="#0d1117").pack(anchor=tk.W)
        self.alert_tree = ttk.Treeview(right_panel, columns=("Time", "Severity", "Message"), show='headings', height=8)
        self.alert_tree.heading("Time", text="Time")
        self.alert_tree.heading("Severity", text="Severity")
        self.alert_tree.heading("Message", text="Message")
        self.alert_tree.column("Time", width=100)
        self.alert_tree.column("Severity", width=100)
        self.alert_tree.column("Message", width=500)
        self.alert_tree.pack(fill=tk.X)

        # Footer Controls
        footer = tk.Frame(root, bg="#161b22", height=80)
        footer.pack(fill=tk.X)

        self.btn_start = tk.Button(footer, text="START MONITORING", command=self.start_monitoring, bg="#238636", fg="white", font=("Arial", 10, "bold"), padx=20, pady=5)
        self.btn_start.pack(side=tk.LEFT, padx=20)

        self.btn_stop = tk.Button(footer, text="STOP", command=self.stop_monitoring, bg="#da3633", fg="white", font=("Arial", 10, "bold"), padx=20, pady=5, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT)

        self.process = None
        self.monitoring = False

    def create_stat(self, parent, label, var, color="#c9d1d9"):
        frame = tk.Frame(parent, bg="#161b22", pady=15)
        frame.pack(fill=tk.X, padx=20)
        tk.Label(frame, text=label, font=("Arial", 10), fg="#8b949e", bg="#161b22").pack()
        tk.Label(frame, textvariable=var, font=("Arial", 24, "bold"), fg=color, bg="#161b22").pack()

    def start_monitoring(self):
        self.monitoring = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.status_label.config(text="● SYSTEM ACTIVE", fg="#3fb950")
        
        # Start detection in background thread
        threading.Thread(target=self.run_detector, daemon=True).start()

    def stop_monitoring(self):
        self.monitoring = False
        if self.process:
            self.process.terminate()
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.status_label.config(text="● SYSTEM IDLE", fg="#8b949e")

    def run_detector(self):
        # Path to venv python and main.py
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        python_exec = os.path.join(project_root, 'venv', 'bin', 'python3')
        main_py = os.path.join(project_root, 'main.py')
        
        # Note: We need to handle sudo if /var/log/auth.log is the target
        # For this demo, let's assume we use regular privileges or a local file
        log_file = "/var/log/auth.log"
        
        cmd = [python_exec, main_py, "detect", "--file", log_file, "--live"]
        
        # Use stdbuf or similar to get unbuffered output
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        anom_count = 0
        log_count = 0
        
        for line in self.process.stdout:
            if not self.monitoring: break
            
            # Update Log Stream
            if "Event:" not in line and "ALERT" not in line and "Reason:" not in line:
                log_count += 1
                self.root.after(0, self.update_logs, line, log_count)
            
            # Handle Alerts
            if "[ALERT -" in line:
                anom_count += 1
                severity = line.split("-")[1].split("]")[0].strip()
                self.root.after(0, self.update_alerts, severity, line, anom_count)

    def update_logs(self, line, count):
        self.log_area.insert(tk.END, f"{line}")
        self.log_area.see(tk.END)
        self.total_logs.set(str(count))

    def update_alerts(self, severity, line, count):
        ts = time.strftime('%H:%M:%S')
        self.alert_tree.insert("", 0, values=(ts, severity, line.strip()))
        self.anomalies.set(str(count))

if __name__ == "__main__":
    root = tk.Tk()
    app = IDSGui(root)
    root.mainloop()
