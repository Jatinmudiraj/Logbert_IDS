#!/bin/bash
echo "==========================================================="
echo "        ADVANCED IDS - INITIALIZATION SCRIPT            "
echo "==========================================================="

# Detect if we have python3
if ! command -v python3 &> /dev/null; then
    echo "[!] Error: python3 is not installed. Please install it with: sudo apt update && sudo apt install python3"
    exit 1
fi

echo "[*] Step 1: Ensuring pip is installed..."
# Many lean Ubuntu systems don't have pip installed by default
if ! python3 -m pip --version &> /dev/null; then
    echo "[*] pip not found. Attempting to install python3-pip..."
    sudo apt update && sudo apt install -y python3-pip
fi

echo "[*] Step 2: Installing Required Python Dependencies..."
# Using --break-system-packages if needed (for Ubuntu 23.04+ environments)
python3 -m pip install --upgrade pip
python3 -m pip install rich joblib pandas scikit-learn numpy scipy PySide6 --break-system-packages 2>/dev/null || \
python3 -m pip install rich joblib pandas scikit-learn numpy scipy PySide6

echo ""
echo "[*] Dependencies installed successfully!"
echo "[*] Step 3: Launching the Real-Time Threat Dashboard..."
echo "Note: The IDS natively requires 'sudo' privileges to read securely restricted authentication logs (/var/log/auth.log)."

# Launch the IDS CLI Dashboard
sudo python3 cli.py
