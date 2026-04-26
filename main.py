import sys
import os

# Add the project root to sys.path to allow imports from core and app
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from PySide6.QtWidgets import QApplication
from app.dashboard import NeuralGuardianDashboard

def main():
    app = QApplication(sys.argv)
    
    # Load Cyber-Defense Theme
    qss_path = os.path.join(project_root, "assets", "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    
    window = NeuralGuardianDashboard()
    window.show()
    
    print("[*] Neural Guardian Dashboard Started.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
