from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSlider, QProgressBar
from PySide6.QtCore import Qt, Signal

class SimulationPage(QWidget):
    # Signals for parent to handle
    toggle_sim = Signal(bool)
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Simulation Control Center")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #f8fafc; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Main Control Card
        control_card = QFrame()
        control_card.setStyleSheet("background-color: #1e293b; border-radius: 12px; padding: 25px; border: 1px solid #334155;")
        control_layout = QVBoxLayout(control_card)
        
        self.status_label = QLabel("STATUS: IDLE")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #94a3b8;")
        control_layout.addWidget(self.status_label)
        
        self.btn_toggle = QPushButton("START FULL SIMULATION")
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                margin-top: 15px;
            }
            QPushButton:hover { background-color: #16a34a; }
        """)
        self.btn_toggle.clicked.connect(self.on_toggle_clicked)
        control_layout.addWidget(self.btn_toggle)
        
        # Parameters
        param_layout = QVBoxLayout()
        param_layout.setContentsMargins(0, 20, 0, 0)
        
        param_layout.addWidget(QLabel("Simulation Intensity (Log Rate)"))
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(1, 10)
        self.intensity_slider.setValue(5)
        param_layout.addWidget(self.intensity_slider)
        
        param_layout.addWidget(QLabel("Attack Frequency"))
        self.attack_bar = QProgressBar()
        self.attack_bar.setValue(15)
        self.attack_bar.setStyleSheet("QProgressBar::chunk { background-color: #ef4444; }")
        param_layout.addWidget(self.attack_bar)
        
        control_layout.addLayout(param_layout)
        layout.addWidget(control_card)
        
        # Scenarios List
        scenarios_label = QLabel("Available Scenarios")
        scenarios_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #94a3b8; margin-top: 20px;")
        layout.addWidget(scenarios_label)
        
        scenarios_box = QHBoxLayout()
        for s in ["SSH Brute Force", "SQL Injection", "DDoS Burst", "Zero Day"]:
            btn = QPushButton(s)
            btn.setStyleSheet("background: #334155; padding: 10px; border-radius: 6px;")
            scenarios_box.addWidget(btn)
        layout.addLayout(scenarios_box)
        
        layout.addStretch()
        
        self.is_running = False

    def on_toggle_clicked(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_toggle.setText("STOP SIMULATION")
            self.btn_toggle.setStyleSheet("background-color: #ef4444; color: white; font-size: 16px; font-weight: bold; padding: 15px; border-radius: 8px; margin-top: 15px;")
            self.status_label.setText("STATUS: SIMULATING TRAFFIC")
            self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #22c55e;")
        else:
            self.btn_toggle.setText("START FULL SIMULATION")
            self.btn_toggle.setStyleSheet("background-color: #22c55e; color: white; font-size: 16px; font-weight: bold; padding: 15px; border-radius: 8px; margin-top: 15px;")
            self.status_label.setText("STATUS: IDLE")
            self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #94a3b8;")
        
        self.toggle_sim.emit(self.is_running)
