from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class ThreatHistoryPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Neural Threat History")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Refresh History")
        self.btn_refresh.setStyleSheet("background: #2563eb; padding: 8px 15px; border-radius: 6px;")
        self.btn_refresh.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Host", "Attack Type", "Score", "Severity", "MITRE", "Source"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #111827;
                border-radius: 12px;
                border: 1px solid #1e293b;
            }
        """)
        layout.addWidget(self.table)
        
        self.refresh_data()

    def refresh_data(self):
        self.table.setRowCount(0)
        anomalies = self.db.get_latest_anomalies(100)
        
        for row_data in anomalies:
            # anomalies table: id, timestamp, host, source_file, raw_log, normalized_log, template_id, anomaly_score, severity, attack_type, reason
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(row_data[1]))) # timestamp
            self.table.setItem(row, 1, QTableWidgetItem(str(row_data[2]))) # host
            self.table.setItem(row, 2, QTableWidgetItem(str(row_data[9]))) # attack_type
            self.table.setItem(row, 3, QTableWidgetItem(f"{row_data[7]*100:.1f}%")) # score
            
            severity = str(row_data[8])
            sev_item = QTableWidgetItem(severity)
            if severity == "Critical": sev_item.setForeground(QColor("#ef4444"))
            elif severity == "High": sev_item.setForeground(QColor("#f97316"))
            else: sev_item.setForeground(QColor("#eab308"))
            self.table.setItem(row, 4, sev_item)
            
            self.table.setItem(row, 5, QTableWidgetItem("T1059")) # mitre placeholder
            self.table.setItem(row, 6, QTableWidgetItem(str(row_data[3]).split("/")[-1])) # source

    def add_anomaly_row(self, timestamp, host, attack, score, severity, source):
        self.table.insertRow(0)
        self.table.setItem(0, 0, QTableWidgetItem(timestamp))
        self.table.setItem(0, 1, QTableWidgetItem(host))
        self.table.setItem(0, 2, QTableWidgetItem(attack))
        self.table.setItem(0, 3, QTableWidgetItem(score))
        
        sev_item = QTableWidgetItem(severity)
        if severity == "Critical": sev_item.setForeground(QColor("#ef4444"))
        elif severity == "High": sev_item.setForeground(QColor("#f97316"))
        else: sev_item.setForeground(QColor("#eab308"))
        self.table.setItem(0, 4, sev_item)
        
        self.table.setItem(0, 5, QTableWidgetItem("T1059"))
        self.table.setItem(0, 6, QTableWidgetItem(source.split("/")[-1]))
