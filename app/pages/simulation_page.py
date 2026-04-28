from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSlider, QProgressBar
from PySide6.QtCore import Qt, Signal

class SimulationPage(QWidget):
    # Signals for parent to handle
    toggle_sim = Signal(bool)
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Neural Attack Simulator")
        header.setStyleSheet("font-size: 26px; font-weight: bold; color: #f8fafc;")
        layout.addWidget(header)
        
        # Main Dashboard for Simulation
        main_frame = QFrame()
        main_frame.setStyleSheet("background: #111827; border-radius: 15px; border: 1px solid #1e293b;")
        main_layout = QHBoxLayout(main_frame)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left Side: Primary Controls
        left_box = QVBoxLayout()
        self.status_title = QLabel("CORE SIMULATOR")
        self.status_title.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        left_box.addWidget(self.status_title)
        
        self.status_label = QLabel("STATUS: IDLE")
        self.status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #64748b; margin: 10px 0;")
        left_box.addWidget(self.status_label)
        
        self.btn_toggle = QPushButton("INITIATE SEQUENCE")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; font-size: 16px; font-weight: bold;
                padding: 18px; border-radius: 10px; border: none;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_toggle.clicked.connect(self.on_toggle_clicked)
        left_box.addWidget(self.btn_toggle)
        main_layout.addLayout(left_box, 2)
        
        # Right Side: Gauges/Sliders
        right_box = QVBoxLayout()
        right_box.setSpacing(15)
        
        # Intensity Gauge
        right_box.addWidget(QLabel("STREAM INTENSITY"))
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(1, 10)
        self.intensity_slider.setValue(5)
        self.intensity_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: #1e293b; height: 6px; border-radius: 3px; }
            QSlider::handle:horizontal { background: #3b82f6; width: 18px; height: 18px; margin: -6px 0; border-radius: 9px; }
        """)
        right_box.addWidget(self.intensity_slider)
        
        # Threat Level Indicator
        right_box.addWidget(QLabel("THREAT MAGNITUDE"))
        self.threat_bar = QProgressBar()
        self.threat_bar.setValue(15)
        self.threat_bar.setMaximumHeight(10)
        self.threat_bar.setTextVisible(False)
        self.threat_bar.setStyleSheet("QProgressBar { background: #1e293b; border-radius: 5px; } QProgressBar::chunk { background: #ef4444; border-radius: 5px; }")
        right_box.addWidget(self.threat_bar)
        
        main_layout.addLayout(right_box, 3)
        layout.addWidget(main_frame)
        
        # Scenario Selection Grid
        grid_container = QFrame()
        grid_container.setStyleSheet("background: #0f172a; border-radius: 15px; padding: 20px; border: 1px solid #1e293b;")
        grid_layout = QVBoxLayout(grid_container)
        grid_layout.addWidget(QLabel("PRESET ATTACK SCENARIOS"))
        
        scenarios_layout = QHBoxLayout()
        scenarios = [
            ("SSH Brute Force", "#ef4444"),
            ("SQL Injection", "#f59e0b"),
            ("DDoS Flood", "#3b82f6"),
            ("Botnet C2", "#8b5cf6")
        ]
        
        for name, color in scenarios:
            s_btn = QPushButton(name)
            s_btn.setCursor(Qt.PointingHandCursor)
            s_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #1e293b; color: {color}; border: 1px solid {color};
                    padding: 15px; border-radius: 8px; font-weight: bold;
                }}
                QPushButton:hover {{ background: {color}; color: white; }}
            """)
            scenarios_layout.addWidget(s_btn)
            
        grid_layout.addLayout(scenarios_layout)
        layout.addWidget(grid_container)
        
        layout.addStretch()
        self.is_running = False

    def on_toggle_clicked(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_toggle.setText("ABORT SEQUENCE")
            self.btn_toggle.setStyleSheet("background-color: #ef4444; color: white; font-size: 16px; font-weight: bold; padding: 18px; border-radius: 10px;")
            self.status_label.setText("STATUS: ACTIVE")
            self.status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #ef4444;")
            self.threat_bar.setValue(85)
        else:
            self.btn_toggle.setText("INITIATE SEQUENCE")
            self.btn_toggle.setStyleSheet("background-color: #2563eb; color: white; font-size: 16px; font-weight: bold; padding: 18px; border-radius: 10px;")
            self.status_label.setText("STATUS: IDLE")
            self.status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #64748b;")
            self.threat_bar.setValue(15)
        
        self.toggle_sim.emit(self.is_running)



