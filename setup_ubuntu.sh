#!/mbin/bash
echo "===================================================="
echo " LOGBERT IDS | UBUNTU AUTO-SETUP & REPAIR"
echo "===================================================="

# 1. Install missing system dependencies
echo "[*] Installing System Dependencies (tk, torch-deps)..."
sudo apt update
sudo apt install python3-tk python3-full -y

# 2. Fix Permissions
echo "[*] Configuring Permissions..."
chmod +x main.py
sudo chmod 644 /var/log/auth.log 2>/dev/null || echo "[!] Notice: Cannot modify auth.log directly. Will use sudo for reading."

# 3. Model Integrity Check
echo "[*] Verifying Neural Models..."
if [ ! -f "models/logbert_model.pth" ]; then
    echo "[ERROR] Neural Weights missing! Please download them to models/logbert_model.pth"
fi

if [ ! -f "models/parser_meta.json" ]; then
    echo "[ERROR] Metadata missing! Please ensure models/parser_meta.json exists."
fi

# 4. Environment Check
echo "[*] Checking Python environment..."
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "===================================================="
echo " SETUP COMPLETE. Run the HUB with:"
echo " sudo ./venv/bin/python3 main.py gui"
echo "===================================================="
