import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import os
import json
import time

class IDSGui:
    def __init__(self, root):
        self.root = root
        self.root.title("LogBERT IDS | Professional Neural Defense Hub")
        self.root.geometry("1200x800")
        self.root.configure(bg="#010409")
        
        # Color Palette
        self.colors = {
            "bg": "#010409", "panel": "#0d1117", "border": "#30363d",
            "text": "#c9d1d9", "dim": "#8b949e", "accent": "#58a6ff",
            "success": "#238636", "warning": "#ffa657", "danger": "#ff7b72"
        }

        self.setup_styles()
        self.create_widgets()
        
        self.process = None
        self.monitoring = False
        self.data_count = 0
        self.threat_count = 0

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background=self.colors["panel"], foreground=self.colors["text"], 
                        rowheight=35, fieldbackground=self.colors["panel"], borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#161b22", foreground=self.colors["dim"], 
                        font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Treeview", background=[('selected', '#1f6feb')])

    def create_widgets(self):
        # Top HUD
        hud = tk.Frame(self.root, bg="#161b22", height=80, bd=0)
        hud.pack(fill=tk.X)
        hud.pack_propagate(False)

        tk.Label(hud, text="NEURAL DEFENSE HUB", font=("Segoe UI", 24, "bold"), fg="white", bg="#161b22").pack(side=tk.LEFT, padx=30)
        
        self.engine_status = tk.Label(hud, text="● DEFENSE ENGINE INACTIVE", font=("Segoe UI", 10, "bold"), fg=self.colors["dim"], bg="#161b22")
        self.engine_status.pack(side=tk.RIGHT, padx=30)

        # Body
        body = tk.Frame(self.root, bg=self.colors["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Sidebar Stats
        sidebar = tk.Frame(body, bg=self.colors["panel"], width=280, bd=1, relief=tk.FLAT)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        sidebar.pack_propagate(False)

        self.create_gauge(sidebar)
        
        self.stat_total = self.add_stat_box(sidebar, "LOGS SCANNED", "0", self.colors["accent"])
        self.stat_threats = self.add_stat_box(sidebar, "THREATS NEUTERED", "0", self.colors["danger"])
        
        # Center Console
        console_frame = tk.Frame(body, bg=self.colors["bg"])
        console_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Real-time Stream
        l_frame = tk.Frame(console_frame, bg=self.colors["panel"])
        l_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        tk.Label(l_frame, text=" LIVE NEURAL STREAM", font=("Segoe UI", 9, "bold"), fg=self.colors["accent"], bg=self.colors["panel"]).pack(anchor=tk.W, padx=10, pady=5)
        
        self.text_area = scrolledtext.ScrolledText(l_frame, bg="#000000", fg="#00ff00", font=("Consolas", 10), bd=0, padx=10)
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Threat Alert Table
        t_frame = tk.Frame(console_frame, bg=self.colors["panel"])
        t_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(t_frame, text=" RECENT THREAT IDENTIFICATIONS", font=("Segoe UI", 9, "bold"), fg=self.colors["danger"], bg=self.colors["panel"]).pack(anchor=tk.W, padx=10, pady=5)

        self.tree = ttk.Treeview(t_frame, columns=("Time", "Category", "Intensity", "Source"), show='headings')
        self.tree.heading("Time", text="TIME")
        self.tree.heading("Category", text="CLASSIFICATION")
        self.tree.heading("Intensity", text="INTENSITY")
        self.tree.heading("Source", text="TELEMETRY DATA")
        self.tree.column("Time", width=100)
        self.tree.column("Category", width=180)
        self.tree.column("Intensity", width=120)
        self.tree.column("Source", width=500)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Control Bar
        controls = tk.Frame(self.root, bg=self.colors["panel"], height=80)
        controls.pack(fill=tk.X)
        
        self.btn_run = tk.Button(controls, text="START MONITORING", command=self.toggle_engine, bg=self.colors["success"], fg="white", font=("Segoe UI", 11, "bold"), relief=tk.FLAT, padx=30, pady=10)
        self.btn_run.pack(side=tk.RIGHT, padx=40, pady=15)

    def create_gauge(self, parent):
        tk.Label(parent, text="BASELINE STABILITY", font=("Segoe UI", 10, "bold"), fg=self.colors["dim"], bg=self.colors["panel"]).pack(pady=(30, 10))
        self.canvas = tk.Canvas(parent, width=200, height=120, bg=self.colors["panel"], highlightthickness=0)
        self.canvas.pack()
        self.arc = self.canvas.create_arc(20, 20, 180, 180, start=0, extent=180, outline=self.colors["border"], width=15, style=tk.ARC)
        self.progress = self.canvas.create_arc(20, 20, 180, 180, start=180, extent=0, outline=self.colors["success"], width=15, style=tk.ARC)
        self.gauge_text = self.canvas.create_text(100, 90, text="100%", fill="white", font=("Segoe UI", 24, "bold"))

    def add_stat_box(self, parent, label, value, color):
        box = tk.Frame(parent, bg=self.colors["panel"], pady=20)
        box.pack(fill=tk.X, padx=20)
        tk.Label(box, text=label, font=("Segoe UI", 9, "bold"), fg=self.colors["dim"], bg=self.colors["panel"]).pack(anchor=tk.W)
        var = tk.StringVar(value=value)
        tk.Label(box, textvariable=var, font=("Segoe UI", 28, "bold"), fg=color, bg=self.colors["panel"]).pack(anchor=tk.W)
        return var

    def toggle_engine(self):
        if not self.monitoring:
            self.start_engine()
        else:
            self.stop_engine()

    def start_engine(self):
        self.monitoring = True
        self.btn_run.config(text="STOP ENGINE", bg=self.colors["danger"])
        self.engine_status.config(text="● NEURAL ARMOR ACTIVE", fg=self.colors["success"])
        threading.Thread(target=self.engine_loop, daemon=True).start()

    def stop_engine(self):
        self.monitoring = False
        self.btn_run.config(text="START MONITORING", bg=self.colors["success"])
        self.engine_status.config(text="● DEFENSE ENGINE INACTIVE", fg=self.colors["dim"])
        if self.process: self.process.terminate()

    def engine_loop(self):
        # Find paths
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        python_exec = os.path.join(project_root, 'venv', 'bin', 'python3')
        main_py = os.path.join(project_root, 'main.py')
        
        # Force /var/log/auth.log
        cmd = [python_exec, "-u", main_py, "detect", "--file", "/var/log/auth.log", "--live"]
        
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            # Non-blocking read
            while self.monitoring:
                line = self.process.stdout.readline()
                if not line: break
                
                self.root.after(0, self.process_output, line)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Engine Error", str(e)))

    def process_output(self, line):
        # Update Text Area
        if "[INIT]" in line or "HEARTBEAT" in line:
            pass # Keep console clean
        else:
            self.data_count += 1
            self.stat_total.set(str(self.data_count))
            self.text_area.insert(tk.END, f" {line}")
            self.text_area.see(tk.END)
            if self.data_count > 500: self.text_area.delete('1.0', '2.0')

        # Handle Alerts
        if "[ALERT -" in line:
            self.threat_count += 1
            self.stat_threats.set(str(self.threat_count))
            
            # Classification and Severity
            try:
                severity = line.split("-")[1].split("]")[0].strip()
                # The next lines from detect.py provide type
                self.root.after(0, self.add_alert_to_table, severity, line)
            except: pass

    def add_alert_to_table(self, severity, line):
        t = time.strftime('%H:%M:%S')
        # Placeholder for classified type until we parse it better from output
        c = "Potential Attack"
        if "Brute Force" in line: c = "Brute Force"
        elif "Unauthorized" in line: c = "Access Violation"
        
        self.tree.insert("", 0, values=(t, c, severity, line.strip()), tags=(severity,))
        self.tree.tag_configure("CRITICAL", foreground="#ff0000", font=("Segoe UI", 10, "bold"))
        self.tree.tag_configure("HIGH", foreground="#ff7b72")
        
        # update stability gauge randomly for effect or based on some metric
        stability = max(30, 100 - (self.threat_count * 5))
        self.update_gauge(stability)

    def update_gauge(self, value):
        extent = (value / 100) * 180
        self.canvas.itemconfig(self.progress, extent=extent)
        self.canvas.itemconfig(self.gauge_text, text=f"{value}%")
        color = self.colors["success"] if value > 80 else self.colors["warning"] if value > 50 else self.colors["danger"]
        self.canvas.itemconfig(self.progress, outline=color)

if __name__ == "__main__":
    root = tk.Tk()
    app = IDSGui(root)
    root.mainloop()
