from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QLineEdit, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor

class LiveLogsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Premium Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        title_box = QVBoxLayout()
        header_label = QLabel("NEURAL TELEMETRY")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        title_box.addWidget(header_label)
        
        self.status_dot = QLabel("● STREAMING LIVE")
        self.status_dot.setStyleSheet("color: #22c55e; font-size: 10px; font-weight: bold;")
        title_box.addWidget(self.status_dot)
        header_layout.addLayout(title_box)
        
        header_layout.addStretch()
        
        # Stylish Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filter telemetry stream...")
        self.search_input.setFixedWidth(350)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border-radius: 8px;
                background: #0f172a;
                border: 1px solid #334155;
                color: #f8fafc;
            }
            QLineEdit:focus { border: 1px solid #3b82f6; }
        """)
        header_layout.addWidget(self.search_input)
        
        self.btn_clear = QPushButton("Clear Stream")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background: #334155; color: #e2e8f0; padding: 10px 20px; 
                border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #475569; }
        """)
        self.btn_clear.clicked.connect(self.clear_logs)
        header_layout.addWidget(self.btn_clear)
        
        layout.addWidget(header_frame)
        
        # Log List with improved styling
        self.log_list = QListWidget()
        self.log_list.setStyleSheet("""
            QListWidget {
                background-color: #020617;
                color: #94a3b8;
                border-radius: 12px;
                padding: 10px;
                font-family: 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                border: 1px solid #1e293b;
                line-height: 1.5;
            }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #0f172a; }
            QListWidget::item:selected { background: #1e40af; color: white; border-radius: 4px; }
        """)
        layout.addWidget(self.log_list)
        
        self.footer = QLabel("Connected to Neural Engine | Monitoring 2 system logs")
        self.footer.setStyleSheet("color: #64748b; font-size: 11px; margin-left: 5px;")
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
