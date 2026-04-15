import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='LogBERT IDS - Management Hub')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Detect Command
    detect_parser = subparsers.add_parser('detect', help='Start anomaly detection')
    detect_parser.add_argument('--file', type=str, required=True, help='Log file to monitor')
    detect_parser.add_argument('--live', action='store_true', help='Live monitoring mode')
    detect_parser.add_argument('--dist', type=float, default=2.0, help='Distance threshold')

    # Calibrate Command
    calibrate_parser = subparsers.add_parser('calibrate', help='Calibrate model to local system')
    calibrate_parser.add_argument('--file', type=str, required=True, help='Sample normal log file')

    # Dashboard Command
    dashboard_parser = subparsers.add_parser('dashboard', help='Open the web dashboard')

    # GUI Command (Native Desktop)
    gui_parser = subparsers.add_parser('gui', help='Launch the Desktop GUI application')

    args = parser.parse_args()

    if args.command == 'detect':
        from scripts.detect import detect_anomalies
        detect_anomalies(args.file, live=args.live, distance_threshold=args.dist)

    elif args.command == 'calibrate':
        from scripts.calibrate import calibrate_on_local
        calibrate_on_local(args.file)

    elif args.command == 'dashboard':
        dashboard_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dashboard', 'index.html'))
        print(f"[*] Dashboard available at: file://{dashboard_path}")
        print("[*] Please open this in your browser to view the real-time IDS.")

    elif args.command == 'gui':
        print("[*] Launching Desktop GUI...")
        import scripts.gui as gui
        import tkinter as tk
        root = tk.Tk()
        app = gui.IDSGui(root)
        root.mainloop()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
