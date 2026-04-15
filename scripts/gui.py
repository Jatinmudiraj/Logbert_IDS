import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import os
import time

class CyberIDS:
    def __init__(self, root):
        self.root = root
        self.root.title("LOGBERT | Neural Cyber-Security Intelligence")
        self.root.geometry("1400x900")
        self.root.configure(bg="#0b0e14")
        
        self.colors = {
            "bg": "#0b0e14", "card": "#151921", "accent": "#00d4ff",
            "critical": "#ff3e3e", "high": "#ff9f1c", "text": "#e0e0e0",
            "dim": "#707880", "success": "#2ecc71"
        }

        self.setup_ui()
        self.monitoring = False
        self.process = None
        self.log_count = 0
        self.threat_count = 0

    def setup_ui(self):
        # Header / HUD
        hud = tk.Frame(self.root, bg="#1a202c", height=100)
        hud.pack(fill=tk.X)
        hud.pack_propagate(False)

        tk.Label(hud, text="LOGBERT", font=("Impact", 36), fg=self.colors["accent"], bg="#1a202c").pack(side=tk.LEFT, padx=40)
        tk.Label(hud, text="NEURAL DEFENSE COMMAND", font=("Arial", 12, "bold"), fg=self.colors["dim"], bg="#1a202c").pack(side=tk.LEFT, pady=(20, 0))

        self.sys_status = tk.Label(hud, text="● ENGINE STANDBY", font=("Consolas", 14, "bold"), fg=self.colors["dim"], bg="#1a202c")
        self.sys_status.pack(side=tk.RIGHT, padx=40)

        # Body Layout
        body = tk.Frame(self.root, bg=self.colors["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Left Column (Metrics & Controls)
        left = tk.Frame(body, bg=self.colors["bg"], width=300)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left.pack_propagate(False)

        self.create_control_panel(left)
        self.create_metrics_panel(left)

        # Center Column (Live Feed)
        center = tk.Frame(body, bg=self.colors["bg"])
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Live Feed Panel
        feed_frame = tk.Frame(center, bg=self.colors["card"], bd=1, relief=tk.FLAT)
        feed_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        tk.Label(feed_frame, text=" LIVE NEURAL TELEMETRY", font=("Consolas", 10, "bold"), fg=self.colors["accent"], bg=self.colors["card"]).pack(anchor=tk.W, padx=15, pady=10)
        
        self.console = scrolledtext.ScrolledText(feed_frame, bg="#000000", fg="#00ff41", font=("Consolas", 10), bd=0, padx=15, pady=10)
        self.console.pack(fill=tk.BOTH, expand=True)

        # Window View (Context)
        window_frame = tk.Frame(center, bg=self.colors["card"], height=250)
        window_frame.pack(fill=tk.X)
        window_frame.pack_propagate(False)
        tk.Label(window_frame, text=" DETECTED ATTACK WINDOW (SLIDING-10 CONTEXT)", font=("Consolas", 10, "bold"), fg=self.colors["high"], bg=self.colors["card"]).pack(anchor=tk.W, padx=15, pady=5)
        
        self.window_text = tk.Text(window_frame, bg="#0d1117", fg="#c9d1d9", font=("Consolas", 9), bd=0, padx=15, pady=10)
        self.window_text.pack(fill=tk.BOTH, expand=True)

        # Right Column (Threat Vault)
        right = tk.Frame(body, bg=self.colors["card"], width=400)
        right.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 0))
        right.pack_propagate(False)

        tk.Label(right, text=" THREAT INTELLIGENCE LOG", font=("Consolas", 10, "bold"), fg=self.colors["critical"], bg=self.colors["card"]).pack(anchor=tk.W, padx=15, pady=15)
        
        style = ttk.Style()
        style.configure("Custom.Treeview", background="#1a202c", foreground="white", fieldbackground="#1a202c", rowheight=30)
        self.tree = ttk.Treeview(right, columns=("ID", "Type"), show='headings', style="Custom.Treeview")
        self.tree.heading("ID", text="TIME")
        self.tree.heading("Type", text="THREAT CLASS")
        self.tree.column("ID", width=100)
        self.tree.column("Type", width=250)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_control_panel(self, parent):
        cp = tk.Frame(parent, bg=self.colors["card"], pady=20)
        cp.pack(fill=tk.X)
        
        tk.Label(cp, text="ENGINE SELECTION", fg=self.colors["dim"], bg=self.colors["card"], font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=20)
        self.source_var = tk.StringVar(value="journalctl (Live)")
        s_menu = ttk.Combobox(cp, textvariable=self.source_var, values=["/var/log/auth.log", "journalctl (Live)", "Simulation Mode"])
        s_menu.pack(fill=tk.X, padx=20, pady=10)

        self.btn_run = tk.Button(cp, text="ENGAGE ARMOR", command=self.toggle, bg=self.colors["success"], fg="white", font=("Arial", 12, "bold"), relief=tk.FLAT, pady=12)
        self.btn_run.pack(fill=tk.X, padx=20, pady=10)

    def create_metrics_panel(self, parent):
        mp = tk.Frame(parent, bg=self.colors["card"], pady=20)
        mp.pack(fill=tk.X, pady=20)

        self.logs_var = self.add_metric(mp, "LOGS ANALYZED", "0", self.colors["text"])
        self.threats_var = self.add_metric(mp, "THREATS NEUTERED", "0", self.colors["critical"])
        
        # Confidence Gauge
        tk.Label(mp, text="NEURAL CONFIDENCE", fg=self.colors["dim"], bg=self.colors["card"], font=("Arial", 9, "bold")).pack(pady=(20, 5))
        self.gauge = tk.Canvas(mp, width=200, height=100, bg=self.colors["card"], highlightthickness=0)
        self.gauge.pack()
        self.gauge.create_arc(20, 20, 180, 180, start=0, extent=180, outline="#333", width=10, style=tk.ARC)
        self.conf_bar = self.gauge.create_arc(20, 20, 180, 180, start=180, extent=0, outline=self.colors["accent"], width=10, style=tk.ARC)
        self.conf_val = self.gauge.create_text(100, 80, text="--%", fill="white", font=("Arial", 16, "bold"))

    def add_metric(self, parent, label, val, color):
        f = tk.Frame(parent, bg=self.colors["card"], pady=10)
        f.pack(fill=tk.X, padx=20)
        tk.Label(f, text=label, font=("Arial", 8, "bold"), fg=self.colors["dim"], bg=self.colors["card"]).pack(anchor=tk.W)
        v = tk.StringVar(value=val)
        tk.Label(f, textvariable=v, font=("Arial", 22, "bold"), fg=color, bg=self.colors["card"]).pack(anchor=tk.W)
        return v

    def toggle(self):
        if not self.monitoring:
            self.monitoring = True
            self.btn_run.config(text="DISENGAGE", bg=self.colors["critical"])
            self.sys_status.config(text="● DEFENSE ACTIVE", fg=self.colors["success"])
            threading.Thread(target=self.engine, daemon=True).start()
        else:
            self.monitoring = False
            self.btn_run.config(text="ENGAGE ARMOR", bg=self.colors["success"])
            self.sys_status.config(text="● ENGINE STANDBY", fg=self.colors["dim"])
            if self.process: self.process.terminate()

    def engine(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        py = os.path.join(root_dir, 'venv', 'bin', 'python3')
        main = os.path.join(root_dir, 'main.py')
        
        src = self.source_var.get()
        if "journalctl" in src:
            cmd = f"journalctl -f | {py} -u {main} detect --stdin"
        elif "/var/log" in src:
            cmd = [py, "-u", main, "detect", "--file", "/var/log/auth.log", "--live"]
        else:
            cmd = [py, "-u", os.path.join(root_dir, "scripts", "sim_logs.py")]

        self.process = subprocess.Popen(cmd, shell=(isinstance(cmd, str)), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        in_window = False
        window_lines = []

        for line in self.process.stdout:
            if not self.monitoring: break
            
            # 1. Update Confidence
            if "CONFIDENCE:" in line:
                try:
                    c = float(line.split("CONFIDENCE:")[1].split("%")[0].strip())
                    self.root.after(0, self.update_gauge, c)
                    self.log_count += 1
                    self.logs_var.set(str(self.log_count))
                    self.console.insert(tk.END, line)
                    self.console.see(tk.END)
                except: pass

            # 2. Update Attack Windows
            if "ATTACK WINDOW:" in line:
                in_window = True
                window_lines = []
                continue
            
            if in_window:
                if "---" in line:
                    in_window = False
                    self.root.after(0, self.update_window, window_lines)
                else:
                    window_lines.append(line)
            
            # 3. Update Intelligence Vault
            if "[DETECTED]" in line:
                self.threat_count += 1
                self.threats_var.set(str(self.threat_count))
                self.root.after(0, self.update_vault, line)

    def update_gauge(self, val):
        extent = (val / 100) * 180
        self.gauge.itemconfig(self.conf_bar, extent=extent)
        self.gauge.itemconfig(self.conf_val, text=f"{int(val)}%")
        color = self.colors["success"] if val > 80 else self.colors["high"] if val > 50 else self.colors["critical"]
        self.gauge.itemconfig(self.conf_bar, outline=color)

    def update_window(self, lines):
        self.window_text.delete('1.0', tk.END)
        for l in lines:
            if ">>>" in l:
                self.window_text.insert(tk.END, l, "danger")
            else:
                self.window_text.insert(tk.END, l)
        self.window_text.tag_configure("danger", foreground=self.colors["critical"], font=("Consolas", 9, "bold"))
        self.root.after(100, lambda: self.window_text.configure(bg="#2d1d1d"))
        self.root.after(500, lambda: self.window_text.configure(bg="#0d1117"))

    def update_vault(self, line):
        t = time.strftime("%H:%M:%S")
        cls = line.split("THREAT:")[1].strip() if "THREAT:" in line else "Anomalous Op"
        self.tree.insert("", 0, values=(t, cls))
        self.flash_screen()

    def flash_screen(self):
        orig = self.sys_status.cget("bg")
        self.sys_status.config(bg=self.colors["critical"])
        self.root.after(200, lambda: self.sys_status.config(bg=orig))

if __name__ == "__main__":
    root = tk.Tk()
    app = CyberIDS(root)
    root.mainloop()
