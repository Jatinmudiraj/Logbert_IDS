from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QListWidget, QSplitter)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from app.widgets.stat_card import StatCard
import time
import os

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Row
        header = QHBoxLayout()
        self.page_title = QLabel("Threat Detection Overview")
        self.page_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #f8fafc;")
        header.addWidget(self.page_title)
        header.addStretch()
        layout.addLayout(header)

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
        layout.addLayout(stats_row)

        # Splitter for Table and Live Feed
        splitter = QSplitter(Qt.Vertical)
        
        # Detection Table
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_label = QLabel("DETECTED ANOMALIES (LogBERT Windows)")
        table_label.setStyleSheet("color: #94a3b8; font-weight: bold; margin-top: 10px;")
        table_layout.addWidget(table_label)
        
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Host", "Attack Type", "Score", "MITRE", "Reason", "Severity"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QTableWidget { border-radius: 8px; background-color: #111827; }")
        table_layout.addWidget(self.table)
        splitter.addWidget(table_container)

        # Live Feed
        feed_container = QWidget()
        feed_layout = QVBoxLayout(feed_container)
        feed_label = QLabel("LIVE TELEMETRY STREAM")
        feed_label.setStyleSheet("color: #94a3b8; font-weight: bold; margin-top: 10px;")
        feed_layout.addWidget(feed_label)
        
        self.log_feed = QListWidget()
        self.log_feed.setStyleSheet("background-color: #020617; color: #94a3b8; border-radius: 8px;")
        feed_layout.addWidget(self.log_feed)
        splitter.addWidget(feed_container)

        layout.addWidget(splitter)

    def update_stats(self, logs, threats):
        self.card_logs.set_value(logs)
        self.card_threats.set_value(threats)

    def add_live_log(self, text, is_alert=False):
        self.log_feed.insertItem(0, text)
        if is_alert:
            self.log_feed.item(0).setForeground(QColor("#ef4444"))
            self.log_feed.item(0).setBackground(QColor("#450a0a"))
        if self.log_feed.count() > 100:
            self.log_feed.takeItem(100)

    def add_anomaly_to_table(self, result):
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

