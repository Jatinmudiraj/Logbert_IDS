import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import sys
import time
import queue

# Import the detection engine directly for faster, more reliable Ubuntu integration
from scripts.detect import detect_anomalies

class NeuralArmorIDS:
    def __init__(self, root):
        self.root = root
        self.root.title("LOGBERT | Neural Cyber-Security Intelligence v5.0")
        self.root.geometry("1400x950")
        self.root.configure(bg="#010409")
        
        self.ui_colors = {
            "bg": "#010409", "hud": "#0d1117", "accent": "#00d4ff",
            "critical": "#ff3333", "warning": "#ffa657", "text": "#e6edf3",
            "dim": "#7d8590", "success": "#238636", "border": "#30363d"
        }

        self.setup_ui()
        self.monitoring = False
        self.msg_queue = queue.Queue()
        self.stats = {"logs": 0, "threats": 0}

        # Start the UI update loop
        self.root.after(100, self.update_loop)

    def setup_ui(self):
        # HUD
        hud = tk.Frame(self.root, bg="#161b22", height=90)
        hud.pack(fill=tk.X)
        hud.pack_propagate(False)
        tk.Label(hud, text="LOGBERT NEURAL ARMOR", font=("Helvetica", 24, "bold"), fg="white", bg="#161b22").pack(side=tk.LEFT, padx=30)
        self.status_msg = tk.Label(hud, text="[ STANDBY ]", font=("Consolas", 12, "bold"), fg=self.ui_colors["dim"], bg="#161b22")
        self.status_msg.pack(side=tk.RIGHT, padx=40)

        # Body
        body = tk.Frame(self.root, bg=self.ui_colors["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Sidebar
        left = tk.Frame(body, bg=self.ui_colors["hud"], width=300)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left.pack_propagate(False)

        tk.Label(left, text="CONTROLS", font=("Segoe UI", 10, "bold"), fg=self.ui_colors["dim"], bg=self.ui_colors["hud"]).pack(pady=20)
        self.src_var = tk.StringVar(value="/var/log/auth.log")
        s_menu = ttk.Combobox(left, textvariable=self.src_var, values=["/var/log/auth.log", "System Simulation"])
        s_menu.pack(fill=tk.X, padx=25, pady=10)

        self.btn_run = tk.Button(left, text="ENGAGE ARMOR", command=self.toggle, bg=self.ui_colors["success"], fg="white", font=("Segoe UI", 12, "bold"), relief=tk.FLAT, pady=15)
        self.btn_run.pack(fill=tk.X, padx=25, pady=20)

        self.logs_val = self.add_metric(left, "LOGS ANALYZED", "0", "white")
        self.threats_val = self.add_metric(left, "THREATS FOUND", "0", self.ui_colors["critical"])

        # Real-time Threat Score Graph
        tk.Label(left, text="NEURAL THREAT SCORE", font=("Segoe UI", 8, "bold"), fg=self.ui_colors["dim"], bg=self.ui_colors["hud"]).pack(pady=(20, 5))
        self.graph = tk.Canvas(left, width=280, height=120, bg="#000000", highlightthickness=0)
        self.graph.pack(pady=10)
        self.points = [100] * 50

        # Console
        center = tk.Frame(body, bg=self.ui_colors["bg"])
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.console = scrolledtext.ScrolledText(center, bg="#000000", fg="#00ff41", font=("Consolas", 10), bd=0, padx=15)
        self.console.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Attack Window
        win_frame = tk.Frame(center, bg=self.ui_colors["hud"], height=300)
        win_frame.pack(fill=tk.X)
        win_frame.pack_propagate(False)
        tk.Label(win_frame, text=" ATTACK SEQUENCE CONTEXT", font=("Consolas", 9, "bold"), fg=self.ui_colors["warning"], bg=self.ui_colors["hud"]).pack(anchor=tk.W, padx=20, pady=10)
        self.win_text = tk.Text(win_frame, bg="#0d1117", fg="#e6edf3", font=("Consolas", 9), bd=0, padx=15, pady=10)
        self.win_text.pack(fill=tk.BOTH, expand=True)

    def add_metric(self, parent, label, init, color):
        f = tk.Frame(parent, bg=self.ui_colors["hud"], pady=15)
        f.pack(fill=tk.X, padx=25)
        tk.Label(f, text=label, font=("Segoe UI", 8, "bold"), fg=self.ui_colors["dim"], bg=self.ui_colors["hud"]).pack(anchor=tk.W)
        v = tk.StringVar(value=init)
        tk.Label(f, textvariable=v, font=("Helvetica", 20, "bold"), fg=color, bg=self.ui_colors["hud"]).pack(anchor=tk.W)
        return v

    def toggle(self):
        if not self.monitoring:
            self.monitoring = True
            self.btn_run.config(text="STOP ENGINE", bg=self.ui_colors["critical"])
            self.status_msg.config(text="[ ARMOR ACTIVE ]", fg="#3fb950")
            threading.Thread(target=self.engine_service, daemon=True).start()
        else:
            self.monitoring = False
            self.btn_run.config(text="ENGAGE ARMOR", bg=self.ui_colors["success"])
            self.status_msg.config(text="[ STANDBY ]", fg=self.ui_colors["dim"])

    def engine_service(self):
        self.msg_queue.put("[GUI] Booting Neural Engine internally...\n")
        src = self.src_var.get()
        
        def gui_callback(msg):
            self.msg_queue.put(msg + "\n")

        try:
            if "Simulation" in src:
                # Run simulator in background
                sim_path = os.path.join(os.path.dirname(__file__), "sim_logs.py")
                subprocess.Popen([sys.executable, sim_path])
                detect_anomalies(log_file="data/sim.log", live=True, callback=gui_callback)
            else:
                detect_anomalies(log_file=src, live=True, callback=gui_callback)
        except Exception as e:
            self.msg_queue.put(f"[FATAL_ERR] {str(e)}\n")

    def update_loop(self):
        try:
            while True:
                line = self.msg_queue.get_nowait()
                if not line: continue
                
                if "CONFIDENCE:" in line:
                    try:
                        c = float(line.split(":")[1].split("%")[0].strip())
                        self.update_graph(c)
                    except: pass
                elif "[ANALYZING]" in line:
                    self.stats["logs"] += 1
                    self.logs_val.set(str(self.stats["logs"]))
                    self.console.insert(tk.END, f" {line}")
                    self.console.see(tk.END)
                elif "[DETECTED]" in line or ">>>" in line:
                    if "[DETECTED]" in line:
                        self.stats["threats"] += 1
                        self.threats_val.set(str(self.stats["threats"]))
                        self.console.insert(tk.END, line, "alert")
                        self.console.tag_configure("alert", foreground="#ff3333", font=("Consolas", 10, "bold"))
                    
                    if ">>>" in line:
                        self.win_text.delete("1.0", tk.END)
                        self.win_text.insert(tk.END, line, "hot")
                    else:
                        self.win_text.insert(tk.END, line)
                    self.win_text.tag_configure("hot", foreground="#ff0000", font=("Consolas", 10, "bold"))
                    self.win_text.see(tk.END)
                else:
                    self.console.insert(tk.END, line)
        except queue.Empty:
            pass
        self.root.after(50, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = NeuralArmorIDS(root)
    root.mainloop()
