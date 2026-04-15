import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import os
import sys
import json
import time
import queue

class NeuralArmorIDS:
    def __init__(self, root):
        self.root = root
        self.root.title("LOGBERT | Neural Cyber-Security Intelligence v3.0")
        self.root.geometry("1400x950")
        self.root.configure(bg="#010409")
        
        # Cyberpunk Theme Colors
        self.ui_colors = {
            "bg": "#010409", "hud": "#0d1117", "accent": "#00d4ff",
            "critical": "#ff3333", "warning": "#ffa657", "text": "#e6edf3",
            "dim": "#7d8590", "success": "#238636", "border": "#30363d"
        }

        self.setup_ui()
        self.monitoring = False
        self.process = None
        self.msg_queue = queue.Queue()
        self.stats = {"logs": 0, "threats": 0, "conf": 100}

        # Start the UI update loop
        self.root.after(100, self.update_loop)

    def setup_ui(self):
        # 1. TOP HUD / COMMAND BAR
        hud = tk.Frame(self.root, bg="#161b22", height=90, bd=0)
        hud.pack(fill=tk.X)
        hud.pack_propagate(False)

        title_box = tk.Frame(hud, bg="#161b22")
        title_box.pack(side=tk.LEFT, padx=30)
        tk.Label(title_box, text="NEURAL ARMOR", font=("Helvetica", 24, "bold"), fg="white", bg="#161b22").pack(side=tk.LEFT)
        tk.Label(title_box, text="IDS", font=("Helvetica", 24, "bold"), fg=self.ui_colors["accent"], bg="#161b22").pack(side=tk.LEFT, padx=10)

        self.status_msg = tk.Label(hud, text="[ SYSTEM OFFLINE ]", font=("Consolas", 12, "bold"), fg=self.ui_colors["dim"], bg="#161b22")
        self.status_msg.pack(side=tk.RIGHT, padx=40)

        # 2. MAIN LAYOUT
        body = tk.Frame(self.root, bg=self.ui_colors["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # LEFT COMMAND CENTER
        left = tk.Frame(body, bg=self.ui_colors["hud"], width=320, bd=1, relief=tk.FLAT)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left.pack_propagate(False)

        tk.Label(left, text="CONTROL CENTER", font=("Segoe UI", 10, "bold"), fg=self.ui_colors["dim"], bg=self.ui_colors["hud"]).pack(pady=20)
        
        self.src_var = tk.StringVar(value="journalctl (Modern)")
        s_menu = ttk.Combobox(left, textvariable=self.src_var, values=["journalctl (Modern)", "/var/log/auth.log", "Self-Test / Simulation"])
        s_menu.pack(fill=tk.X, padx=25, pady=10)

        self.btn_run = tk.Button(left, text="ENGAGE SHIELD", command=self.toggle, bg=self.ui_colors["success"], fg="white", font=("Segoe UI", 12, "bold"), relief=tk.FLAT, pady=15)
        self.btn_run.pack(fill=tk.X, padx=25, pady=20)

        # METRICS
        self.logs_val = self.create_metric_widget(left, "TOTAL SCANNED LOGS", "0", "white")
        self.threats_val = self.create_metric_widget(left, "NEUTARLIZED THREATS", "0", self.ui_colors["critical"])
        
        # CENTER INTELLIGENCE STREAM
        center = tk.Frame(body, bg=self.ui_colors["bg"])
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Live Console
        console_frame = tk.Frame(center, bg=self.ui_colors["hud"])
        console_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        tk.Label(console_frame, text=" LIVE TELEMETRY LOG", font=("Consolas", 9, "bold"), fg=self.ui_colors["accent"], bg=self.ui_colors["hud"]).pack(anchor=tk.W, padx=20, pady=10)
        
        self.console = scrolledtext.ScrolledText(console_frame, bg="#000000", fg="#00ff41", font=("Consolas", 10), bd=0, padx=15)
        self.console.pack(fill=tk.BOTH, expand=True)

        # Context Window
        win_frame = tk.Frame(center, bg=self.ui_colors["hud"], height=280, bd=1, relief=tk.RIDGE)
        win_frame.pack(fill=tk.X)
        win_frame.pack_propagate(False)
        tk.Label(win_frame, text=" NEURAL ATTACK WINDOW (10-LOG SEQUENCE ANALYSIS)", font=("Consolas", 9, "bold"), fg=self.ui_colors["warning"], bg=self.ui_colors["hud"]).pack(anchor=tk.W, padx=20, pady=10)
        
        self.window_view = tk.Text(win_frame, bg="#0d1117", fg="#e6edf3", font=("Consolas", 9), bd=0, padx=15, pady=10)
        self.window_view.pack(fill=tk.BOTH, expand=True)

        # RIGHT THREAT VAULT
        right = tk.Frame(body, bg=self.ui_colors["hud"], width=350)
        right.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 0))
        right.pack_propagate(False)
        
        tk.Label(right, text=" THREAT INTELLIGENCE", font=("Segoe UI", 10, "bold"), fg=self.ui_colors["critical"], bg=self.ui_colors["hud"]).pack(pady=20)
        
        self.tree = ttk.Treeview(right, columns=("T", "C"), show='headings', height=15)
        self.tree.heading("T", text="TIME")
        self.tree.heading("C", text="THREAT CLASS")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_metric_widget(self, parent, label, init, color):
        f = tk.Frame(parent, bg=self.ui_colors["hud"], pady=15)
        f.pack(fill=tk.X, padx=25)
        tk.Label(f, text=label, font=("Segoe UI", 8, "bold"), fg=self.ui_colors["dim"], bg=self.ui_colors["hud"]).pack(anchor=tk.W)
        v = tk.StringVar(value=init)
        tk.Label(f, textvariable=v, font=("Helvetica", 22, "bold"), fg=color, bg=self.ui_colors["hud"]).pack(anchor=tk.W)
        return v

    def toggle(self):
        if not self.monitoring:
            self.start()
        else:
            self.stop()

    def start(self):
        self.monitoring = True
        self.btn_run.config(text="STOP ENGINE", bg=self.ui_colors["critical"])
        self.status_msg.config(text="[ SHIELD ACTIVE ]", fg="#3fb950")
        self.console.insert(tk.END, "[*] INITIALIZING NEURAL COMPONENTS...\n")
        
        threading.Thread(target=self.reader_thread, daemon=True).start()

    def stop(self):
        self.monitoring = False
        self.btn_run.config(text="ENGAGE SHIELD", bg=self.ui_colors["success"])
        self.status_msg.config(text="[ SYSTEM OFFLINE ]", fg=self.ui_colors["dim"])
        if self.process: self.process.terminate()

    def reader_thread(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # ALWAYS use sys.executable to ensure we use exactly the same environment
        py = sys.executable
        main = os.path.join(root, 'main.py')
        
        src = self.src_var.get()
        if "journalctl" in src:
            cmd = f"journalctl -f | {py} -u {main} detect --stdin"
        elif "/var/log" in src:
            cmd = [py, "-u", main, "detect", "--file", "/var/log/auth.log", "--live"]
        else:
            cmd = [py, "-u", os.path.join(root, "scripts", "sim_logs.py")]

        try:
            self.process = subprocess.Popen(cmd, shell=(isinstance(cmd, str)), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in iter(self.process.stdout.readline, ""):
                if not self.monitoring: break
                self.msg_queue.put(line)
        except Exception as e:
            self.msg_queue.put(f"[FATAL_UI_ERROR] {str(e)}")

    def update_loop(self):
        while not self.msg_queue.empty():
            line = self.msg_queue.get()
            self.handle_line(line)
        self.root.after(50, self.update_loop)

    def handle_line(self, line):
        # Console Updates
        if "[ANALYZING]" in line:
            self.stats["logs"] += 1
            self.logs_val.set(str(self.stats["logs"]))
            self.console.insert(tk.END, f" {line}")
            self.console.see(tk.END)
            if self.stats["logs"] > 1000: self.console.delete("1.0", "2.0")

        # Threat Detection Highlights
        if "[DETECTED]" in line:
            self.stats["threats"] += 1
            self.threats_val.set(str(self.stats["threats"]))
            cls = line.split("THREAT:")[1].strip() if "THREAT:" in line else "Anomaly"
            self.tree.insert("", 0, values=(time.strftime("%H:%M:%S"), cls))
            self.flash_hud()

        # Window View Handling
        if ">>>" in line or "   " in line:
            if ">>>" in line:
                self.window_view.insert(tk.END, f"[! DETECTED TRACE] {line.strip()}\n", "hot")
            else:
                self.window_view.insert(tk.END, f"  {line}")
            self.window_view.see(tk.END)
            self.window_view.tag_configure("hot", foreground="#ff0000", font=("Consolas", 10, "bold"))
            
        if "---" in line:
            self.window_view.insert(tk.END, "\n" + "-"*50 + "\n")

    def flash_hud(self):
        self.status_msg.config(bg=self.ui_colors["critical"])
        self.root.after(300, lambda: self.status_msg.config(bg="#161b22"))

if __name__ == "__main__":
    root = tk.Tk()
    app = NeuralArmorIDS(root)
    root.mainloop()
