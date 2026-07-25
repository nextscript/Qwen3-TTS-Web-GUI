#!/bin/bash

# Qwen3-TTS Web GUI - Start Script (Linux/Mac)

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  Qwen3-TTS Web GUI${NC}"
echo -e "${CYAN}============================================================${NC}"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[Fehler] Python3 ist nicht installiert.${NC}"
    echo "Bitte installiere Python 3.10+ von https://www.python.org/"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Python3 gefunden: $(python3 --version 2>&1)"
echo

# Check/create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[1/3]${NC} Virtuelle Umgebung wird erstellt..."
    python3 -m venv venv
    echo -e "${GREEN}[OK]${NC} Virtuelle Umgebung erstellt"
else
    echo -e "${GREEN}[OK]${NC} Virtuelle Umgebung vorhanden"
fi
echo

# Activate venv
echo -e "${YELLOW}[2/3]${NC} Abhängigkeiten werden installiert..."
source venv/bin/activate

# Install requirements
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}[Fehler] requirements.txt nicht gefunden!${NC}"
    exit 1
fi

pip install -r requirements.txt --quiet 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[Warnung]${NC} Einige Pakete konnten nicht automatisch installiert werden."
    echo "Versuche manuell..."
    pip install flask flask-cors torch torchaudio qwen-tts soundfile transformers accelerate sentencepiece
fi
echo -e "${GREEN}[OK]${NC} Abhängigkeiten installiert"
echo

echo -e "${YELLOW}[3/3]${NC} Starte Server..."
echo
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  Web-GUI ist unter http://localhost:5000 erreichbar${NC}"
echo -e "${CYAN}  Drücke STRG+C zum Beenden${NC}"
echo -e "${CYAN}============================================================${NC}"
echo

python app.py
