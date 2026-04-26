from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class StatCard(QFrame):
    def __init__(self, title, value="0", color="#f8fafc"):
        super().__init__()
        self.setObjectName("StatCard")
        self.setMinimumWidth(180)
        self.setMinimumHeight(100)
        
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("StatTitle")
        
        self.value_label = QLabel(value)
        self.value_label.setObjectName("StatValue")
        self.value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label, alignment=Qt.AlignCenter)

    def set_value(self, value):
        self.value_label.setText(str(value))
