# LogBERT IDS | Neural Anomaly Detection

A state-of-the-art Intrusion Detection System (IDS) based on the BERT transformer architecture. This system uses Masked Log Key Prediction (MLKP) and Volume of Hypersphere Minimization (VHM) to identify sophisticated cyber threats in system logs.

## 🚀 Key Features
- **Neural Detection:** Powered by a Transformer-based BERT model.
- **Local Calibration:** Fine-tune the model to your specific Linux environment for maximum accuracy.
- **Live Dashboard:** Real-time visualization of log streams and high-confidence alerts.
- **Tiered Severity:** Anomalies are categorized into CRITICAL, HIGH, and MEDIUM tiers.

## 📂 Project Structure
- `main.py`: Centralized management hub (CLI).
- `core/`: Core neural engine, dataset handlers, and log parsers.
- `scripts/`: Operational scripts for detection, calibration, and training.
- `dashboard/`: Premium Web UI for monitoring.
- `models/`: Trained model weights and metadata.

## 🛠️ Getting Started

### 1. Calibrate the Baseline
Teach the model what "Normal" looks like on your machine to reduce false positives.
```bash
python main.py calibrate --file /path/to/normal/auth.log
```

### 2. Start Live Detection
Monitor your system logs in real-time with neural analysis.
```bash
python main.py detect --file /var/log/auth.log --live
```

### 3. Open the Dashboard
To visualize the alerts in a premium UI, open the following file in your browser:
`dashboard/index.html`

## 📊 Confidence Metrics
- **Probability:** Calculated via MLKP head.
- **Spatial Distance:** Measures the deviation from the "Normal Center" in the hypersphere.
- **EMA Smoothing:** Statistical filtering to ensure alerts are persistent and reliable.
