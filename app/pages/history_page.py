from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class ThreatHistoryPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Professional Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        header_label = QLabel("NEURAL THREAT ARCHIVE")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Filter history...")
        self.search_bar.setFixedWidth(250)
        self.search_bar.setStyleSheet("padding: 8px; border-radius: 6px; background: #0f172a; border: 1px solid #334155;")
        self.search_bar.textChanged.connect(self.filter_table)
        header_layout.addWidget(self.search_bar)
        
        self.btn_refresh = QPushButton("🔄 Sync Database")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background: #2563eb; color: white; padding: 10px 20px; 
                border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        self.btn_refresh.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.btn_refresh)
        
        layout.addWidget(header_frame)
        
        # Advanced Table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Host", "Attack Type", "Score", "Severity", "MITRE", "Source"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0f172a;
                alternate-background-color: #1e293b;
                border-radius: 12px;
                border: 1px solid #1e293b;
                color: #e2e8f0;
            }
            QHeaderView::section {
                background-color: #334155;
                color: #f8fafc;
                padding: 12px;
                font-weight: bold;
                border: none;
            }
        """)
        layout.addWidget(self.table)
        
        self.refresh_data()

    def filter_table(self, text):
        for i in range(self.table.rowCount()):
            match = False
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(i, not match)


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
