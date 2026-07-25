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
    echo -e "${RED}[ERROR] Python3 is not installed.${NC}"
    echo "Please install Python 3.10+ from https://www.python.org/"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Python3 found: $(python3 --version 2>&1)"
echo

# Check/create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[1/4]${NC} Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}[OK]${NC} Virtual environment created"
else
    echo -e "${GREEN}[OK]${NC} Virtual environment already exists"
fi
echo

# Activate venv
echo -e "${YELLOW}[2/4]${NC} Installing dependencies..."
source venv/bin/activate

# Check requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}[ERROR] requirements.txt not found!${NC}"
    exit 1
fi

# Check if requirements are already installed
MISSING=$(pip check 2>/dev/null || true)
if [ -z "$MISSING" ]; then
    echo -e "${GREEN}[OK]${NC} All dependencies already installed"
else
    pip install -r requirements.txt --quiet 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}[WARNING]${NC} Some packages could not be installed automatically."
        echo "Trying manually..."
        pip install flask flask-cors torch torchaudio qwen-tts soundfile transformers accelerate sentencepiece
    fi
    echo -e "${GREEN}[OK]${NC} Dependencies installed"
fi
echo

echo -e "${YELLOW}[3/4]${NC} Dependencies ready"
echo

echo -e "${YELLOW}[4/4]${NC} Starting server..."
echo
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  Web-GUI: http://localhost:5000${NC}"
echo -e "${CYAN}  Press CTRL+C to stop${NC}"
echo -e "${CYAN}============================================================${NC}"
echo

python app.py
