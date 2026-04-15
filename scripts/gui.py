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
        self.root.title("LogBERT IDS | Ultra-Premium Security Hub")
        self.root.geometry("1200x850")
        self.root.configure(bg="#010409")
        
        self.colors = {
            "bg": "#010409", "panel": "#0d1117", "border": "#30363d",
            "text": "#c9d1d9", "dim": "#8b949e", "accent": "#58a6ff",
            "success": "#238636", "warning": "#ffa657", "danger": "#ff7b72"
        }

        self.setup_ui()
        self.monitoring = False
        self.process = None

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#161b22", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="NEURAL ARMOR", font=("Segoe UI", 24, "bold"), fg="white", bg="#161b22").pack(side=tk.LEFT, padx=30)
        
        # Main Layout
        content = tk.Frame(self.root, bg="#010409")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Config Panel
        config = tk.Frame(content, bg="#0d1117", width=300, bd=1, relief=tk.FLAT)
        config.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        config.pack_propagate(False)

        tk.Label(config, text="CONFIGURATION", font=("Segoe UI", 10, "bold"), fg="#8b949e", bg="#0d1117").pack(pady=20)
        
        tk.Label(config, text="Log Source", fg="white", bg="#0d1117").pack(anchor=tk.W, padx=20)
        self.source_var = tk.StringVar(value="journalctl (Modern)")
        source_menu = ttk.Combobox(config, textvariable=self.source_var, values=["/var/log/auth.log", "journalctl (Modern)", "Simulation Mode"])
        source_menu.pack(fill=tk.X, padx=20, pady=10)

        self.btn_toggle = tk.Button(config, text="ENGAGE ENGINE", command=self.toggle_engine, bg="#238636", fg="white", font=("Segoe UI", 11, "bold"), relief=tk.FLAT, pady=10)
        self.btn_toggle.pack(fill=tk.X, padx=20, pady=20)

        self.debug_btn = tk.Button(config, text="VIEW ENGINE ERRORS", command=self.show_debug, bg="#30363d", fg="white", relief=tk.FLAT)
        self.debug_btn.pack(fill=tk.X, padx=20, pady=5)

        # Right Console Panel
        right = tk.Frame(content, bg="#010409")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.console = scrolledtext.ScrolledText(right, bg="#000000", fg="#00ff00", font=("Consolas", 10), bd=0)
        self.console.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        self.tree = ttk.Treeview(right, columns=("Time", "Crit", "Type", "Log"), show='headings', height=10)
        self.tree.heading("Time", text="TIME")
        self.tree.heading("Crit", text="SEVERITY")
        self.tree.heading("Type", text="THREAT")
        self.tree.heading("Log", text="LOG ENTRY")
        self.tree.pack(fill=tk.X)

        self.debug_log = []

    def toggle_engine(self):
        if not self.monitoring:
            self.start_engine()
        else:
            self.stop_engine()

    def start_engine(self):
        self.monitoring = True
        self.btn_toggle.config(text="DISENGAGE", bg="#b62324")
        self.console.insert(tk.END, "[*] BOOTING NEURAL ENGINE...\n")
        threading.Thread(target=self.engine_worker, daemon=True).start()

    def stop_engine(self):
        self.monitoring = False
        if self.process: self.process.terminate()
        self.btn_toggle.config(text="ENGAGE ENGINE", bg="#238636")

    def engine_worker(self):
        proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        py_path = os.path.join(proj_root, 'venv', 'bin', 'python3')
        main_py = os.path.join(proj_root, 'main.py')
        
        mode = self.source_var.get()
        if "/var/log" in mode:
            cmd = [py_path, "-u", main_py, "detect", "--file", "/var/log/auth.log", "--live"]
        elif "journalctl" in mode:
            # Piped mode for reliability
            cmd = f"journalctl -n 20 -f | {py_path} -u {main_py} detect --stdin"
        else:
            cmd = [py_path, "-u", os.path.join(proj_root, "scripts", "sim_logs.py")]

        try:
            if "|" in str(cmd):
                self.process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            else:
                self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            for line in self.process.stdout:
                if not self.monitoring: break
                self.debug_log.append(line)
                self.root.after(0, self.update_console, line)
        except Exception as e:
            self.debug_log.append(f"CRITICAL ERROR: {str(e)}")

    def update_console(self, line):
        if "[ANALYZING]" in line:
            self.console.insert(tk.END, f" {line}")
            self.console.see(tk.END)
        if "[ALERT" in line:
            self.tree.insert("", 0, values=(time.strftime("%H:%M:%S"), "HIGH", "Anomaly", line.split("]")[1]))

    def show_debug(self):
        win = tk.Toplevel(self.root)
        win.title("Engine Telemetry / Error Log")
        win.geometry("800x600")
        t = scrolledtext.ScrolledText(win, bg="black", fg="white")
        t.pack(fill=tk.BOTH, expand=True)
        t.insert(tk.END, "".join(self.debug_log))

if __name__ == "__main__":
    root = tk.Tk()
    app = IDSGui(root)
    root.mainloop()
