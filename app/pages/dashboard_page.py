from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PySide6.QtCore import Qt
from app.widgets.stat_card import StatCard

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Neural Guardian | Overview")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #f8fafc; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Stats Grid
        stats_layout = QGridLayout()
        self.card_logs = StatCard("Logs Processed", "0", "#3b82f6")
        self.card_threats = StatCard("Total Anomalies", "0", "#ef4444")
        self.card_uptime = StatCard("System Uptime", "00:00:00", "#22c55e")
        self.card_conf = StatCard("Neural Confidence", "99.8%", "#6366f1")
        
        stats_layout.addWidget(self.card_logs, 0, 0)
        stats_layout.addWidget(self.card_threats, 0, 1)
        stats_layout.addWidget(self.card_uptime, 1, 0)
        stats_layout.addWidget(self.card_conf, 1, 1)
        layout.addLayout(stats_layout)
        
        # Bottom area: Health Status
        health_frame = QFrame()
        health_frame.setStyleSheet("background-color: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155;")
        health_layout = QVBoxLayout(health_frame)
        
        health_title = QLabel("System Health & Neural Engine Status")
        health_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #94a3b8;")
        health_layout.addWidget(health_title)
        
        self.engine_status = QLabel("● LogBERT Model: LOADED (v1.2.0)")
        self.engine_status.setStyleSheet("color: #22c55e; margin-top: 10px;")
        health_layout.addWidget(self.engine_status)
        
        self.db_status = QLabel("● Database Connection: STABLE")
        self.db_status.setStyleSheet("color: #22c55e;")
        health_layout.addWidget(self.db_status)
        
        self.monitor_status = QLabel("● Log Monitors: ACTIVE (2 sources)")
        self.monitor_status.setStyleSheet("color: #22c55e;")
        health_layout.addWidget(self.monitor_status)
        
        layout.addWidget(health_frame)
        layout.addStretch()

    def update_stats(self, logs, threats):
        self.card_logs.set_value(logs)
        self.card_threats.set_value(threats)
