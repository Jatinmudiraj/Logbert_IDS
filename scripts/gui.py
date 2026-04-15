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
        self.root.title("LogBERT IDS | Neural Threat Intelligence")
        self.root.geometry("1100x750")
        self.root.configure(bg="#010409")

        # Custom Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview", 
            background="#0d1117", 
            foreground="#c9d1d9", 
            rowheight=30,
            fieldbackground="#0d1117", 
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        self.style.configure("Treeview.Heading", 
            background="#161b22", 
            foreground="#8b949e", 
            font=("Segoe UI", 10, "bold"),
            borderwidth=0
        )
        self.style.map("Treeview", background=[('selected', '#1f6feb')])

        # Build UI
        self.create_header()
        
        main_frame = tk.Frame(root, bg="#010409")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        # Stats Sidebar
        self.create_sidebar(main_frame)

        # Main Content Area
        content_frame = tk.Frame(main_frame, bg="#010409")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Log Console
        tk.Label(content_frame, text="Neural Log Stream", font=("Segoe UI", 10, "bold"), fg="#58a6ff", bg="#010409").pack(anchor=tk.W, pady=(0, 5))
        self.log_area = scrolledtext.ScrolledText(content_frame, height=12, bg="#0d1117", fg="#c9d1d9", font=("Consolas", 10), bd=1, relief=tk.FLAT)
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Alerts Table
        tk.Label(content_frame, text="Detected Threats & Classifications", font=("Segoe UI", 10, "bold"), fg="#ff7b72", bg="#010409").pack(anchor=tk.W, pady=(0, 5))
        self.alert_tree = ttk.Treeview(content_frame, columns=("Time", "Severity", "Type", "Event"), show='headings', height=10)
        self.alert_tree.heading("Time", text="TIMESTAMP")
        self.alert_tree.heading("Severity", text="SEVERITY")
        self.alert_tree.heading("Type", text="THREAT TYPE")
        self.alert_tree.heading("Event", text="EVENT DATA")
        self.alert_tree.column("Time", width=100, anchor=tk.CENTER)
        self.alert_tree.column("Severity", width=120, anchor=tk.CENTER)
        self.alert_tree.column("Type", width=180, anchor=tk.W)
        self.alert_tree.column("Event", width=500, anchor=tk.W)
        self.alert_tree.pack(fill=tk.BOTH, expand=True)

        # Footer
        self.create_footer()

        self.process = None
        self.monitoring = False

    def create_header(self):
        header = tk.Frame(self.root, bg="#161b22", height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg="#161b22")
        title_frame.pack(side=tk.LEFT, padx=30)
        
        tk.Label(title_frame, text="LOGBERT", font=("Segoe UI", 22, "bold"), fg="white", bg="#161b22").pack(side=tk.LEFT)
        tk.Label(title_frame, text="IDS", font=("Segoe UI", 22, "bold"), fg="#238636", bg="#161b22").pack(side=tk.LEFT)
        
        self.status_dot = tk.Label(header, text="●", font=("Arial", 16), fg="#8b949e", bg="#161b22")
        self.status_dot.pack(side=tk.RIGHT, padx=(0, 10))
        self.status_text = tk.Label(header, text="ENGINE OFFLINE", font=("Segoe UI", 10, "bold"), fg="#8b949e", bg="#161b22")
        self.status_text.pack(side=tk.RIGHT, padx=(0, 30))

    def create_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg="#0d1117", width=220, bd=1, relief=tk.FLAT)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="SYSTEM METRICS", font=("Segoe UI", 9, "bold"), fg="#8b949e", bg="#0d1117").pack(pady=(20, 10))
        
        self.total_logs = tk.StringVar(value="0")
        self.anom_count = tk.StringVar(value="0")
        self.confidence = tk.StringVar(value="100%")

        self.add_metric(sidebar, "LOGS ANALYZED", self.total_logs, "#c9d1d9")
        self.add_metric(sidebar, "THREATS FOUND", self.anom_count, "#ff7b72")
        self.add_metric(sidebar, "SYS CONFIDENCE", self.confidence, "#58a6ff")

    def add_metric(self, parent, label, var, color):
        f = tk.Frame(parent, bg="#0d1117", pady=15)
        f.pack(fill=tk.X, padx=15)
        tk.Label(f, text=label, font=("Segoe UI", 8, "bold"), fg="#8b949e", bg="#0d1117").pack(anchor=tk.W)
        tk.Label(f, textvariable=var, font=("Segoe UI", 20, "bold"), fg=color, bg="#0d1117").pack(anchor=tk.W)

    def create_footer(self):
        footer = tk.Frame(self.root, bg="#0d1117", height=80)
        footer.pack(fill=tk.X, pady=10)
        
        btn_frame = tk.Frame(footer, bg="#0d1117")
        btn_frame.pack(side=tk.RIGHT, padx=40)

        self.btn_start = tk.Button(btn_frame, text="START DEFENSE ENGINE", command=self.start_monitoring, 
                                  bg="#238636", fg="white", font=("Segoe UI", 10, "bold"), 
                                  activebackground="#2ea043", relief=tk.FLAT, padx=25, pady=8)
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(btn_frame, text="STOP", command=self.stop_monitoring, 
                                 bg="#b62324", fg="white", font=("Segoe UI", 10, "bold"), 
                                 activebackground="#da3633", relief=tk.FLAT, padx=20, pady=8, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT)

    def start_monitoring(self):
        self.monitoring = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.status_dot.config(fg="#3fb950")
        self.status_text.config(text="LOGBERT ACTIVE", fg="#3fb950")
        threading.Thread(target=self.run_detector, daemon=True).start()

    def stop_monitoring(self):
        self.monitoring = False
        if self.process: self.process.terminate()
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.status_dot.config(fg="#8b949e")
        self.status_text.config(text="ENGINE OFFLINE", fg="#8b949e")

    def run_detector(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        python_exec = os.path.join(project_root, 'venv', 'bin', 'python3')
        main_py = os.path.join(project_root, 'main.py')
        log_file = "/var/log/auth.log"
        
        # In a real environment, we'd want to browse for a file, but let's stick to auth.log for now
        cmd = [python_exec, "-u", main_py, "detect", "--file", log_file, "--live"]
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        l_count = 0
        a_count = 0
        
        for line in self.process.stdout:
            if not self.monitoring: break
            
            # Simple line parsing for the GUI update
            if "Event:" in line:
                pass # Already handled by ALERT
            elif "[ALERT -" in line:
                a_count += 1
                sev = line.split("-")[1].split("]")[0].strip()
                # Read next lines for details
                t_type = "Neural Outlier"
                for i in range(2):
                    next_line = self.process.stdout.readline()
                    if "Threat Type:" in next_line:
                        t_type = next_line.split(":")[1].strip()
                
                self.root.after(0, self.update_alerts, sev, t_type, line.strip(), a_count)
            else:
                l_count += 1
                self.root.after(0, self.update_logs, line, l_count)

    def update_logs(self, line, count):
        self.log_area.insert(tk.END, f" {line}")
        if count % 10 == 0: self.log_area.see(tk.END)
        self.total_logs.set(str(count))

    def update_alerts(self, sev, t_type, line, count):
        ts = time.strftime('%H:%M:%S')
        # Insert with color based on severity
        tags = (sev,)
        self.alert_tree.insert("", 0, values=(ts, sev, t_type, line), tags=tags)
        self.alert_tree.tag_configure("CRITICAL", foreground="#ff4444", font=("Segoe UI", 10, "bold"))
        self.alert_tree.tag_configure("HIGH", foreground="#ff7b72")
        self.alert_tree.tag_configure("MEDIUM", foreground="#ffa657")
        self.anom_count.set(str(count))
        # Dramatic flash for Critical
        if sev == "CRITICAL":
            self.header_flash("#b62324", 3)

    def header_flash(self, color, count):
        if count <= 0: return
        current = self.status_dot.cget("fg")
        self.status_dot.config(fg="#ff0000" if count % 2 == 0 else "#3fb950")
        self.root.after(200, lambda: self.header_flash(color, count-1))

if __name__ == "__main__":
    root = tk.Tk()
    app = IDSGui(root)
    root.mainloop()
