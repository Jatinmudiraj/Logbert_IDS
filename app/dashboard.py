import sys
import os
import time
import json
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QPushButton, QFrame, QListWidget, QStackedWidget)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QIcon, QColor

from app.widgets.stat_card import StatCard
from core.detector_service import LogBERTDetectorService
from core.monitor import LogMonitor
from core.db import IDSDatabase

class NeuralGuardianDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEURAL GUARDIAN | Advanced LogBERT IDS")
        self.setMinimumSize(1200, 800)
        
        # Initialize Backend
        self.db = IDSDatabase()
        self.detector = LogBERTDetectorService()
        
        self.total_logs = 0
        self.total_anomalies = 0
        
        self.setup_ui()
        
        # Monitor Thread
        self.monitor = LogMonitor(
            log_paths=["/var/log/auth.log", "data/sim.log"],
            callback=self.on_anomaly_detected
        )
        self.monitor.start()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("background-color: #111827; border-right: 1px solid #1e293b;")
        sidebar_layout = QVBoxLayout(sidebar)
        
        logo = QLabel("NEURAL GUARDIAN")
        logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #3b82f6; margin: 20px 0;")
        sidebar_layout.addWidget(logo, alignment=Qt.AlignCenter)
        
        self.btn_dash = QPushButton("Dashboard")
        self.btn_logs = QPushButton("Live Logs")
        self.btn_threats = QPushButton("Threat History")
        self.btn_eval = QPushButton("Evaluation")
        self.btn_settings = QPushButton("Settings")
        
        for btn in [self.btn_dash, self.btn_logs, self.btn_threats, self.btn_eval, self.btn_settings]:
            btn.setStyleSheet("text-align: left; padding: 12px; border: none; border-radius: 5px;")
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # 2. Main Content Area
        content_area = QWidget()
        self.content_layout = QVBoxLayout(content_area)
        main_layout.addWidget(content_area)

        # Header Row (Title and Status)
        header = QHBoxLayout()
        self.page_title = QLabel("System Dashboard")
        self.page_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(self.page_title)
        header.addStretch()
        self.status_label = QLabel("🛡️ SYSTEM SECURE")
        self.status_label.setStyleSheet("color: #22c55e; font-weight: bold;")
        header.addWidget(self.status_label)
        self.content_layout.addLayout(header)

        # Stats Cards Row
        stats_row = QHBoxLayout()
        self.card_logs = StatCard("Logs Processed", "0", "#3b82f6")
        self.card_threats = StatCard("Anomalies", "0", "#ef4444")
        self.card_conf = StatCard("Neural Confidence", "99.8%", "#22c55e")
        self.card_latency = StatCard("Avg Latency", "12ms", "#eab308")
        
        stats_row.addWidget(self.card_logs)
        stats_row.addWidget(self.card_threats)
        stats_row.addWidget(self.card_conf)
        stats_row.addWidget(self.card_latency)
        self.content_layout.addLayout(stats_row)

        # Main Table / Feed Area
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Host", "Attack Type", "Score", "MITRE", "Reason", "Severity"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.content_layout.addWidget(self.table, 3)

        # Control Row
        controls = QHBoxLayout()
        self.btn_replay = QPushButton("▶️ Replay Attack (SSH)")
        self.btn_replay.setObjectName("ActionBtn")
        self.btn_replay.clicked.connect(self.replay_demo)
        controls.addWidget(self.btn_replay)
        controls.addStretch()
        self.content_layout.addLayout(controls)

        # Live Feed
        self.log_feed = QListWidget()
        self.content_layout.addWidget(QLabel("Live Telemetry Stream"))
        self.content_layout.addWidget(self.log_feed, 1)

    def replay_demo(self):
        scenario_path = "demo_scenarios/ssh_bruteforce.log"
        if os.path.exists(scenario_path):
            self.log_feed.insertItem(0, f"[*] REPLAY STARTED: {scenario_path}")
            with open(scenario_path, "r") as f:
                lines = f.readlines()
                # We'll simulate a window of 10 logs for the demo
                if len(lines) >= 10:
                    self.on_anomaly_detected(lines[:20], scenario_path)

    def on_anomaly_detected(self, sequence, source_path):
        self.total_logs += len(sequence)
        result = self.detector.analyze_sequence(sequence)
        
        self.card_logs.set_value(self.total_logs)
        
        log_entry = f"[{time.strftime('%H:%M:%S')}] Analyzed window ({len(sequence)} logs) from {os.path.basename(source_path)}"
        self.log_feed.insertItem(0, log_entry)
        if self.log_feed.count() > 50: self.log_feed.takeItem(50)

        if result and result["is_anomaly"]:
            self.total_anomalies += 1
            self.card_threats.set_value(self.total_anomalies)
            self.status_label.setText("⚠️ THREAT DETECTED")
            self.status_label.setStyleSheet("color: #ef4444; font-weight: bold;")
            
            # Add to table
            self.table.insertRow(0)
            self.table.setItem(0, 0, QTableWidgetItem(time.strftime('%H:%M:%S')))
            self.table.setItem(0, 1, QTableWidgetItem("localhost"))
            self.table.setItem(0, 2, QTableWidgetItem(result.get("attack_type", "Anomaly")))
            self.table.setItem(0, 3, QTableWidgetItem(f"{result['score']*100:.1f}%"))
            self.table.setItem(0, 4, QTableWidgetItem(result.get("mitre_technique", "T1059")))
            self.table.setItem(0, 5, QTableWidgetItem(result.get("reason", "Unknown")))
            self.table.setItem(0, 6, QTableWidgetItem(result["severity"]))
            
            # Save to DB
            self.db.insert_anomaly(
                "localhost", source_path, result["last_raw"], "", 
                str(result["template_ids"][-1]), result["score"], 
                result["severity"], result.get("attack_type", "Neural Anomaly"), 
                result.get("reason", "LogBERT mismatch detected")
            )

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Load style
    qss_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
            
    win = NeuralGuardianDashboard()
    win.show()
    sys.exit(app.exec())
