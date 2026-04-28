from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QLineEdit, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor

class LiveLogsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with Search/Filter
        header_layout = QHBoxLayout()
        header_label = QLabel("Live Telemetry Stream")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter logs...")
        self.search_input.setFixedWidth(300)
        self.search_input.setStyleSheet("padding: 8px; border-radius: 6px; background: #0f172a; border: 1px solid #334155;")
        header_layout.addWidget(self.search_input)
        
        self.btn_clear = QPushButton("Clear Stream")
        self.btn_clear.setStyleSheet("background: #334155; padding: 8px 15px; border-radius: 6px;")
        self.btn_clear.clicked.connect(self.clear_logs)
        header_layout.addWidget(self.btn_clear)
        
        layout.addLayout(header_layout)
        
        # Log List
        self.log_list = QListWidget()
        self.log_list.setStyleSheet("""
            QListWidget {
                background-color: #020617;
                color: #94a3b8;
                border-radius: 12px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: 1px solid #1e293b;
            }
        """)
        layout.addWidget(self.log_list)
        
        # Status footer
        self.footer = QLabel("Connected to 2 sources | Streaming...")
        self.footer.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(self.footer)

    def add_log(self, text, is_alert=False):
        if self.search_input.text() and self.search_input.text().lower() not in text.lower():
            return
            
        self.log_list.insertItem(0, text)
        if is_alert:
            self.log_list.item(0).setForeground(QColor("#ef4444"))
            self.log_list.item(0).setBackground(QColor("#450a0a"))
            
        if self.log_list.count() > 500:
            self.log_list.takeItem(500)

    def clear_logs(self):
        self.log_list.clear()
