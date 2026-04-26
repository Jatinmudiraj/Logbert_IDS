# Current System Analysis - Logbert_IDS

| Parameter | Value |
| :--- | :--- |
| **Dataset (Train)** | Variable (passed to scripts/train.py) |
| **Dataset (Test)** | data/test_labeled.json (used in evaluate.py) |
| **Sequence Length (Window Size)** | 10 |
| **Masking Ratio** | 0.15 |
| **Number of Layers** | 4 |
| **Number of Attention Heads** | 8 |
| **Hidden Dimension (d_model)** | 256 |
| **Anomaly Threshold** | Mismatches > 1 (within Top-5 predictions) |
| **Current Performance** | 936 anomalies in 28528 sequences (from result.txt) |
| **UI Entry Point** | main.py |

## Observations
- The system uses a joblib model (`model/production.joblib`) for real-time monitoring in `main.py`, but the core research scripts (`train.py`, `evaluate.py`) use a PyTorch-based LogBERT model.
- Thresholding is currently based on a fixed mismatch count in masked token prediction.
- UI in `main.py` is a neural-themed dashboard but doesn't share the same comprehensive feature set as the standard IDS dashboard.
