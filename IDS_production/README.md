# ADVANCED IDS — Advanced Security Suite

Professional Intrusion Detection System for autonomous threat monitoring.

## 🚀 Deployment Commands

### 🟢 Start IDS (Background)
Runs the IDS persistently and automatically restarts it if it crashes.
```bash
nohup /home/geeta/IDS/run_ids_forever.sh > /home/geeta/IDS/runner.log 2>&1 &
```

### 🔴 Stop IDS
Safely terminates all monitoring threads and background runners.
```bash
pkill -f run_ids_forever.sh && pkill -f cli.py
```

### 📊 Monitor Dashboard (Live)
View the professional real-time incident response log.
```bash
tail -f /home/geeta/IDS/ids_cli_final.log
```

## 🛠️ Simulation & Testing
To test the detection engine with simulated attacks:
1. **Start Simulator**: `nohup python3 /home/geeta/IDS/simulate_logs.py > /home/geeta/IDS/simulator.log 2>&1 &`
2. **Watch Alerts**: Check the dashboard log above.

## 📁 Directory Structure
- `cli.py`: Professional CLI Dashboard.
- `main.py`: Native GUI Dashboard (requires monitor/display).
- `detector.py`: AI Inference Engine (TF-IDF + Numeric).
- `monitor.py`: High-privilege log tailing system.
- `model/`: Production model snapshots.

---
*Created by Advanced AI*
