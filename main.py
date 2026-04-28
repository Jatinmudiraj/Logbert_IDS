import sys
import os

# Add the project root to sys.path to allow imports from core and app
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from PySide6.QtWidgets import QApplication
from app.dashboard import NeuralGuardianDashboard

def main():
    # Environment Diagnostics
    if os.geteuid() == 0:
        print("[!] Warning: Running as root/sudo. This often causes Qt/DBus theme issues.")
        print("[!] If the UI looks strange or fails, try running as a normal user.")
        # Attempt to fix common sudo/Qt issues
        if "DBUS_SESSION_BUS_ADDRESS" not in os.environ:
            os.environ["DBUS_SESSION_BUS_ADDRESS"] = ""

    app = QApplication(sys.argv)
    
    # Load Cyber-Defense Theme
    qss_path = os.path.join(project_root, "assets", "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    
    print("[*] Initializing Neural Guardian...")
    window = NeuralGuardianDashboard()
    window.show()
    
    print("[*] Neural Guardian Dashboard Started.")
    print("[*] Note: If no logs appear, use the 'Start Simulation' button in the dashboard.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
