import sys
import os
import time
import json
import threading
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QPushButton, QFrame, QListWidget, QStackedWidget,
                             QSplitter, QProgressBar)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QIcon, QColor, QFont

from app.widgets.stat_card import StatCard
from core.detector_service import LogBERTDetectorService
from core.monitor import LogMonitor
from core.db import IDSDatabase
from core.simulator import LogSimulator

# Import Pages
from app.pages.dashboard_page import DashboardPage
from app.pages.live_logs_page import LiveLogsPage
from app.pages.history_page import ThreatHistoryPage
from app.pages.simulation_page import SimulationPage

class NeuralGuardianDashboard(QMainWindow):
    # Signal to handle logs from threads safely in UI
    log_received = Signal(str, str) # log_line, source
    window_analyzed = Signal(list, str, dict) # sequence, source, result

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEURAL GUARDIAN | Advanced LogBERT IDS")
        self.setMinimumSize(1280, 850)
        
        # Initialize Backend
        self.db = IDSDatabase()
        self.detector = LogBERTDetectorService()
        self.simulator = None
        
        self.total_logs = 0
        self.total_anomalies = 0
        
        self.setup_ui()
        
        # Connect Signals
        self.log_received.connect(self.update_log_feeds)
        self.window_analyzed.connect(self.on_anomaly_detected)
        
        # Monitor Thread
        self.monitor = LogMonitor(
            log_paths=["/var/log/auth.log", "data/sim.log"],
            callback=self.process_window,
            live_callback=self.process_live_log,
            window_size=10
        )
        self.monitor.start()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Navigation
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("background-color: #0f172a; border-right: 1px solid #1e293b;")
        sidebar_layout = QVBoxLayout(sidebar)
        
        logo = QLabel("🛡️ NEURAL GUARDIAN")
        logo.setStyleSheet("font-size: 20px; font-weight: bold; color: #60a5fa; margin: 25px 0;")
        sidebar_layout.addWidget(logo, alignment=Qt.AlignCenter)
        
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Live Logs", self.show_live_logs),
            ("Threat History", self.show_history),
            ("Simulation Control", self.show_simulation)
        ]
        
        for name, callback in nav_items:
            btn = QPushButton(f"  {name}")
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left; padding: 12px; border: none; border-radius: 8px; margin: 2px 10px;
                    color: #94a3b8;
                }
                QPushButton:hover { background-color: #1e293b; color: #f8fafc; }
                QPushButton#active { background-color: #2563eb; color: white; }
            """)
            btn.setFont(QFont("Segoe UI", 10))
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
            self.nav_buttons[name] = btn
        
        sidebar_layout.addStretch()
        
        # System Status in Sidebar
        status_box = QFrame()
        status_box.setStyleSheet("background-color: #1e293b; border-radius: 10px; margin: 10px; padding: 10px;")
        status_layout = QVBoxLayout(status_box)
        self.status_text = QLabel("SYSTEM: ACTIVE")
        self.status_text.setStyleSheet("color: #22c55e; font-weight: bold;")
        status_layout.addWidget(self.status_text)
        
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setValue(15)
        self.cpu_bar.setMaximumHeight(8)
        self.cpu_bar.setTextVisible(False)
        self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: #3b82f6; }")
        status_layout.addWidget(QLabel("Neural Load"))
        status_layout.addWidget(self.cpu_bar)
        
        sidebar_layout.addWidget(status_box)
        main_layout.addWidget(sidebar)

        # 2. Main Content Area (Stacked Widget)
        self.stack = QStackedWidget()
        
        self.page_dash = DashboardPage()
        self.page_live = LiveLogsPage()
        self.page_hist = ThreatHistoryPage(self.db)
        self.page_sim = SimulationPage()
        self.page_sim.toggle_sim.connect(self.handle_simulation_toggle)
        
        self.stack.addWidget(self.page_dash)
        self.stack.addWidget(self.page_live)
        self.stack.addWidget(self.page_hist)
        self.stack.addWidget(self.page_sim)
        
        main_layout.addWidget(self.stack)
        
        # Default Page
        self.show_dashboard()

    def set_active_button(self, name):
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.setObjectName("active")
            else:
                btn.setObjectName("")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.page_dash)
        self.set_active_button("Dashboard")

    def show_live_logs(self):
        self.stack.setCurrentWidget(self.page_live)
        self.set_active_button("Live Logs")

    def show_history(self):
        self.page_hist.refresh_data()
        self.stack.setCurrentWidget(self.page_hist)
        self.set_active_button("Threat History")

    def show_simulation(self):
        self.stack.setCurrentWidget(self.page_sim)
        self.set_active_button("Simulation Control")

    def handle_simulation_toggle(self, start):
        if start:
            self.simulator = LogSimulator(target_file="data/sim.log", interval=0.5)
            self.simulator.start()
        else:
            if self.simulator:
                self.simulator.stop()
                self.simulator = None

    def process_live_log(self, line, source):
        self.log_received.emit(line, source)

    def process_window(self, sequence, source):
        result = self.detector.analyze_sequence(sequence)
        self.window_analyzed.emit(sequence, source, result)

    @Slot(str, str)
    def update_log_feeds(self, line, source):
        self.total_logs += 1
        self.page_dash.update_stats(self.total_logs, self.total_anomalies)
        
        timestamp = time.strftime('%H:%M:%S')
        source_name = os.path.basename(source)
        item_text = f"[{timestamp}] [{source_name}] {line}"
        
        # Update Live Logs Page
        self.page_live.add_log(item_text)

    @Slot(list, str, dict)
    def on_anomaly_detected(self, sequence, source_path, result):
        if not result: return

        if result["is_anomaly"]:
            self.total_anomalies += 1
            self.page_dash.update_stats(self.total_logs, self.total_anomalies)
            self.status_text.setText("SYSTEM: THREAT DETECTED")
            self.status_text.setStyleSheet("color: #ef4444; font-weight: bold;")
            
            # Add to Live Logs with Alert styling
            alert_msg = f"!!! ANOMALY DETECTED: {result.get('attack_type')} !!!"
            self.page_live.add_log(alert_msg, is_alert=True)
            
            # Save to DB
            self.db.insert_anomaly(
                "localhost", source_path, result["last_raw"], "", 
                str(result["template_ids"][-1]), result["score"], 
                result["severity"], result.get("attack_type", "Neural Anomaly"), 
                result.get("reason", "LogBERT mismatch detected")
            )
            
            # If on history page, refresh
            if self.stack.currentWidget() == self.page_hist:
                self.page_hist.refresh_data()
        else:
            if self.total_anomalies > 0 and self.total_logs % 50 == 0:
                self.status_text.setText("SYSTEM: ACTIVE")
                self.status_text.setStyleSheet("color: #22c55e; font-weight: bold;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = NeuralGuardianDashboard()
    win.show()
    sys.exit(app.exec())

