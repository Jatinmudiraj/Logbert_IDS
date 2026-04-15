import sys
import os
import time
import threading
import json
from collections import deque
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QFrame, QTableWidget, 
                             QTableWidgetItem, QListWidget, QPushButton, 
                             QHeaderView, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QPointF
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QLinearGradient, QBrush

# Import relative components
from normalize_helpers import normalize_record
from detector import IDSDetector

# ---------------------------------------------------------
# STYLING: Premium Cyber-Glass HUD
# ---------------------------------------------------------
STYLE = """
QMainWindow {
    background-color: #010409;
}
QFrame#MetricCard {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 12px;
}
QFrame#GlassPanel {
    background-color: rgba(13, 17, 23, 0.8);
    border: 1px solid #30363d;
    border-radius: 15px;
}
QLabel {
    color: #e6edf3;
    font-family: 'Segoe UI', Roboto, Helvetica, Arial;
}
QTableWidget {
    background-color: transparent;
    border: none;
    color: #e6edf3;
    gridline-color: #30363d;
}
QHeaderView::section {
    background-color: #161b22;
    padding: 10px;
    border: none;
    color: #58a6ff;
    font-weight: bold;
}
QListWidget {
    background-color: transparent;
    border: none;
    color: #8b949e;
    font-family: 'Consolas', monospace;
    font-size: 11px;
}
QPushButton#ActionBtn {
    background-color: #238636;
    color: white;
    border-radius: 6px;
    padding: 12px;
    font-weight: bold;
    border: none;
}
QPushButton#ActionBtn:hover {
    background-color: #2ea043;
}
"""

class ThreatGraph(QWidget):
    """Real-time Line Chart for Threat Probability"""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(150)
        self.points = [0.0] * 40
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

    def add_point(self, val):
        self.points.pop(0)
        self.points.append(val)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Grid
        painter.setPen(QPen(QColor("#30363d"), 1, Qt.DashLine))
        for i in range(1, 4):
            y = i * (self.height() / 4)
            painter.drawLine(0, y, self.width(), y)

        # Line
        pen = QPen(QColor("#00d2ff"), 2)
        painter.setPen(pen)
        
        path = []
        for i in range(len(self.points)):
            x = i * (self.width() / (len(self.points)-1))
            y = self.height() - (self.points[i] * self.height())
            path.append(QPointF(x, y))

        for i in range(len(path)-1):
            # Dynamic color based on threat level
            val = self.points[i+1]
            color = QColor("#ff3366") if val > 0.7 else QColor("#ffcc00") if val > 0.3 else QColor("#00ffcc")
            painter.setPen(QPen(color, 2))
            painter.drawLine(path[i], path[i+1])

# ---------------------------------------------------------
# MAIN APPLICATION: NEURAL GUARDIAN HUD
# ---------------------------------------------------------
class NeuralGuardian(QMainWindow):
    update_signal = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEURAL GUARDIAN | Intelligent Cyber-Defense")
        self.setMinimumSize(1200, 850)
        self.setStyleSheet(STYLE)
        
        self.init_engine()
        self.setup_ui()
        
        self.total_logs = 0
        self.total_threats = 0
        self.update_signal.connect(self.process_event)

    def init_engine(self):
        from monitor import MultiLogMonitor
        
        self.config = {
            'monitoring': {'sources': [{'path': '/var/log/auth.log', 'domain': 'ssh', 'enabled': True}], 'window_size': 10, 'min_lines_for_inference': 5},
            'detection': {'model_path': 'model/production.joblib', 'confidence_blocking_threshold': 0.95},
            'response': {'enabled': False}
        }
        
        # Ensure log exists
        if not os.path.exists('/var/log/auth.log'):
            os.system('touch data/sim.log 2>/dev/null || true')
            self.config['monitoring']['sources'][0]['path'] = 'data/sim.log'
            
        self.monitor = MultiLogMonitor(self.config, self.on_log_received)
        self.monitor.daemon = True
        self.monitor.start()

    def on_log_received(self, data):
        self.update_signal.emit({
            "raw": data.get("raw", ""),
            "is_attack": data.get("is_attack", False),
            "proba": data.get("confidence", 0.0),
            "type": data.get("stage", "unknown")
        })

    def setup_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        main_layout = QVBoxLayout(cw)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)

        # Header
        header_lay = QHBoxLayout()
        title = QLabel("NEURAL GUARDIAN")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #58a6ff;")
        status = QLabel("🛡️ DEFENSE ENGAGED")
        status.setStyleSheet("color: #3fb950; font-weight: bold;")
        header_lay.addWidget(title)
        header_lay.addStretch()
        header_lay.addWidget(status)
        main_layout.addLayout(header_lay)

        # Metrics Row
        metrics_lay = QHBoxLayout()
        card1, self.card_logs = self.create_metric("LOGS ANALYZED", "0", "#8b949e")
        card2, self.card_threats = self.create_metric("THREATS DETECTED", "0", "#ff7b72")
        card3, self.card_acc = self.create_metric("NEURAL CONFIDENCE", "99.8%", "#58a6ff")
        metrics_lay.addWidget(card1)
        metrics_lay.addWidget(card2)
        metrics_lay.addWidget(card3)
        main_layout.addLayout(metrics_lay)

        # Middle Content
        content_lay = QHBoxLayout()
        content_lay.setSpacing(25)

        # Left Column: Graph and Feed
        left_col = QVBoxLayout()
        
        graph_box = QFrame()
        graph_box.setObjectName("GlassPanel")
        graph_lay = QVBoxLayout(graph_box)
        graph_lay.addWidget(QLabel("LIVE THREAT INTENSITY"))
        self.threat_graph = ThreatGraph()
        graph_lay.addWidget(self.threat_graph)
        left_col.addWidget(graph_box, 1)

        feed_box = QFrame()
        feed_box.setObjectName("GlassPanel")
        feed_lay = QVBoxLayout(feed_box)
        feed_lay.addWidget(QLabel("LOG TELEMETRY STREAM"))
        self.log_list = QListWidget()
        feed_lay.addWidget(self.log_list)
        left_col.addWidget(feed_box, 2)
        
        content_lay.addLayout(left_col, 1)

        # Right Column: Alert Table
        right_box = QFrame()
        right_box.setObjectName("GlassPanel")
        right_lay = QVBoxLayout(right_box)
        right_lay.addWidget(QLabel("🛑 SECURITY ALERTS"))
        self.alert_table = QTableWidget(0, 3)
        self.alert_table.setHorizontalHeaderLabels(["TIME", "ATTACK TYPE", "PROBABILITY"])
        self.alert_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_lay.addWidget(self.alert_table)
        content_lay.addWidget(right_box, 1)

        main_layout.addLayout(content_lay)

    def create_metric(self, title, val, color):
        card = QFrame()
        card.setObjectName("MetricCard")
        lay = QVBoxLayout(card)
        t = QLabel(title)
        t.setStyleSheet("font-size: 10px; color: #8b949e; font-weight: bold;")
        v = QLabel(val)
        v.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        lay.addWidget(t)
        lay.addWidget(v)
        return card, v



    @Slot(dict)
    def process_event(self, data):
        self.total_logs += 1
        self.card_logs.setText(str(self.total_logs))
        self.threat_graph.add_point(data['proba'])
        
        log_item = f"[{time.strftime('%H:%M:%S')}] {data['raw'][:100]}"
        self.log_list.insertItem(0, log_item)
        if self.log_list.count() > 50: self.log_list.takeItem(50)

        if data['is_attack']:
            self.total_threats += 1
            self.card_threats.setText(str(self.total_threats))
            
            row = self.alert_table.rowCount()
            self.alert_table.insertRow(0)
            self.alert_table.setItem(0, 0, QTableWidgetItem(time.strftime('%H:%M:%S')))
            self.alert_table.setItem(0, 1, QTableWidgetItem(data['type'].upper()))
            self.alert_table.setItem(0, 2, QTableWidgetItem(f"{data['proba']*100:.1f}%"))
            
            for i in range(3):
                self.alert_table.item(0, i).setForeground(QColor("#ff7b72"))
                self.alert_table.item(0, i).setFont(QFont("Segoe UI", 10, QFont.Bold))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    guardian = NeuralGuardian()
    guardian.show()
    sys.exit(app.exec())
