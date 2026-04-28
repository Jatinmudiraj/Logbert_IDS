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
        self.log_received.connect(self.update_live_feed)
        self.window_analyzed.connect(self.on_anomaly_detected)
        
        # Monitor Thread
        # We monitor both a system log and our simulation log
        self.monitor = LogMonitor(
            log_paths=["/var/log/auth.log", "data/sim.log"],
            callback=self.process_window,
            live_callback=self.process_live_log,
            window_size=10 # Smaller window for faster feedback
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
        sidebar.setStyleSheet("background-color: #0f172a; border-right: 1px solid #1e293b;")
        sidebar_layout = QVBoxLayout(sidebar)
        
        logo = QLabel("🛡️ NEURAL GUARDIAN")
        logo.setStyleSheet("font-size: 20px; font-weight: bold; color: #60a5fa; margin: 25px 0;")
        sidebar_layout.addWidget(logo, alignment=Qt.AlignCenter)
        
        self.btn_dash = QPushButton("  Dashboard")
        self.btn_logs = QPushButton("  Live Logs")
        self.btn_threats = QPushButton("  Threat History")
        self.btn_sim = QPushButton("  Simulation Control")
        
        for btn in [self.btn_dash, self.btn_logs, self.btn_threats, self.btn_sim]:
            btn.setStyleSheet("text-align: left; padding: 12px; border: none; border-radius: 8px; margin: 2px 10px;")
            btn.setFont(QFont("Segoe UI", 10))
            sidebar_layout.addWidget(btn)
        
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

        # 2. Main Content Area
        content_area = QWidget()
        self.content_layout = QVBoxLayout(content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(content_area)

        # Header Row
        header = QHBoxLayout()
        self.page_title = QLabel("Threat Detection Overview")
        self.page_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #f8fafc;")
        header.addWidget(self.page_title)
        header.addStretch()
        
        self.sim_status = QLabel("Simulation: OFF")
        self.sim_status.setStyleSheet("color: #94a3b8; padding-right: 20px;")
        header.addWidget(self.sim_status)
        
        self.btn_toggle_sim = QPushButton("Start Simulation")
        self.btn_toggle_sim.setObjectName("ActionBtn")
        self.btn_toggle_sim.clicked.connect(self.toggle_simulation)
        header.addWidget(self.btn_toggle_sim)
        self.content_layout.addLayout(header)

        # Stats Cards Row
        stats_row = QHBoxLayout()
        self.card_logs = StatCard("Logs Processed", "0", "#3b82f6")
        self.card_threats = StatCard("Anomalies", "0", "#ef4444")
        self.card_conf = StatCard("Neural Confidence", "99.8%", "#22c55e")
        self.card_latency = StatCard("Analysis Latency", "8ms", "#eab308")
        
        stats_row.addWidget(self.card_logs)
        stats_row.addWidget(self.card_threats)
        stats_row.addWidget(self.card_conf)
        stats_row.addWidget(self.card_latency)
        self.content_layout.addLayout(stats_row)

        # Splitter for Table and Live Feed
        splitter = QSplitter(Qt.Vertical)
        
        # Detection Table
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.addWidget(QLabel("DETECTED ANOMALIES (LogBERT Windows)"))
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Host", "Attack Type", "Score", "MITRE", "Reason", "Severity"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QTableWidget { border-radius: 8px; }")
        table_layout.addWidget(self.table)
        splitter.addWidget(table_container)

        # Live Feed
        feed_container = QWidget()
        feed_layout = QVBoxLayout(feed_container)
        feed_layout.addWidget(QLabel("LIVE TELEMETRY STREAM"))
        self.log_feed = QListWidget()
        self.log_feed.setStyleSheet("background-color: #020617; color: #94a3b8; border-radius: 8px;")
        feed_layout.addWidget(self.log_feed)
        splitter.addWidget(feed_container)

        self.content_layout.addWidget(splitter)

    def toggle_simulation(self):
        if self.simulator and self.simulator.running:
            self.simulator.stop()
            self.simulator = None
            self.btn_toggle_sim.setText("Start Simulation")
            self.sim_status.setText("Simulation: OFF")
            self.sim_status.setStyleSheet("color: #94a3b8;")
        else:
            self.simulator = LogSimulator(target_file="data/sim.log", interval=0.5)
            self.simulator.start()
            self.btn_toggle_sim.setText("Stop Simulation")
            self.sim_status.setText("Simulation: RUNNING")
            self.sim_status.setStyleSheet("color: #22c55e; font-weight: bold;")

    def process_live_log(self, line, source):
        self.log_received.emit(line, source)

    def process_window(self, sequence, source):
        result = self.detector.analyze_sequence(sequence)
        self.window_analyzed.emit(sequence, source, result)

    @Slot(str, str)
    def update_live_feed(self, line, source):
        self.total_logs += 1
        self.card_logs.set_value(self.total_logs)
        
        timestamp = time.strftime('%H:%M:%S')
        source_name = os.path.basename(source)
        item_text = f"[{timestamp}] [{source_name}] {line}"
        
        self.log_feed.insertItem(0, item_text)
        if self.log_feed.count() > 100:
            self.log_feed.takeItem(100)
            
        # Subtle highlight for lines that look like attacks even before analysis
        if any(word in line.lower() for word in ["fail", "error", "attack", "unauthorized"]):
            self.log_feed.item(0).setForeground(QColor("#f87171"))

    @Slot(list, str, dict)
    def on_anomaly_detected(self, sequence, source_path, result):
        if not result: return

        if result["is_anomaly"]:
            self.total_anomalies += 1
            self.card_threats.set_value(self.total_anomalies)
            self.status_text.setText("SYSTEM: THREAT DETECTED")
            self.status_text.setStyleSheet("color: #ef4444; font-weight: bold;")
            
            # Add to table
            self.table.insertRow(0)
            self.table.setItem(0, 0, QTableWidgetItem(time.strftime('%H:%M:%S')))
            self.table.setItem(0, 1, QTableWidgetItem("localhost"))
            self.table.setItem(0, 2, QTableWidgetItem(result.get("attack_type", "Anomaly")))
            self.table.setItem(0, 3, QTableWidgetItem(f"{result['score']*100:.1f}%"))
            self.table.setItem(0, 4, QTableWidgetItem(result.get("mitre_technique", "T1059")))
            self.table.setItem(0, 5, QTableWidgetItem(result.get("reason", "LogBERT mismatch")))
            
            severity = result["severity"]
            sev_item = QTableWidgetItem(severity)
            if severity == "Critical": sev_item.setForeground(QColor("#ef4444"))
            elif severity == "High": sev_item.setForeground(QColor("#f97316"))
            else: sev_item.setForeground(QColor("#eab308"))
            self.table.setItem(0, 6, sev_item)
            
            # Highlight the anomaly in the live feed too
            alert_msg = f"!!! ANOMALY DETECTED in window of {len(sequence)} logs !!!"
            self.log_feed.insertItem(0, alert_msg)
            self.log_feed.item(0).setForeground(QColor("#ef4444"))
            self.log_feed.item(0).setBackground(QColor("#450a0a"))
            
            # Save to DB
            self.db.insert_anomaly(
                "localhost", source_path, result["last_raw"], "", 
                str(result["template_ids"][-1]), result["score"], 
                result["severity"], result.get("attack_type", "Neural Anomaly"), 
                result.get("reason", "LogBERT mismatch detected")
            )
        else:
            # Revert status if things are calm
            if self.total_anomalies > 0 and self.total_logs % 50 == 0:
                self.status_text.setText("SYSTEM: ACTIVE")
                self.status_text.setStyleSheet("color: #22c55e; font-weight: bold;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = NeuralGuardianDashboard()
    win.show()
    sys.exit(app.exec())

