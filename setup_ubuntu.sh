#!/bin/bash
echo "===================================================="
echo " NEURAL GUARDIAN | UBUNTU AUTO-SETUP"
echo "===================================================="

# 1. System Dependencies
echo "[*] Installing System UI Libraries..."
sudo apt update
sudo apt install python3-pip python3-venv libxcb-cursor0 -y

# 2. Virtual Environment
if [ ! -d "venv" ]; then
    echo "[*] Creating environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "[*] Installing Neural Engine & UI Components..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Model Verification
echo "[*] Verifying Neural Guardian Weights..."
if [ ! -f "model/production.joblib" ]; then
    echo "[!] WARNING: Production weights missing in model/."
fi

echo "===================================================="
echo " SETUP COMPLETE."
echo " Launch the Guardian with:"
echo " sudo ./venv/bin/python3 main.py"
echo "===================================================="
