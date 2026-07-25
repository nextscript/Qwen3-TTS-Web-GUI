#!/usr/bin/env python3
"""Launcher for Qwen3-TTS Web GUI"""

import os
import subprocess
import sys

GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def install_gpu_pytorch(pip_in_venv):
    """Install PyTorch with GPU support automatically."""
    print(f"{YELLOW}[GPU-PyTorch]{NC} Installing PyTorch with GPU support...")

    # Try CUDA 13.2 first (RTX 50xx series)
    cuda_index = "https://download.pytorch.org/whl/nightly/cu132"

    result = subprocess.run(
        [
            pip_in_venv,
            "install",
            "--pre",
            "torch",
            "torchvision",
            "torchaudio",
            "--index-url",
            cuda_index,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"{YELLOW}[WARN]{NC} CUDA 13.2 failed, trying CUDA 12.4...")
        # Fallback to CUDA 12.4
        result = subprocess.run(
            [
                pip_in_venv,
                "install",
                "--pre",
                "torch",
                "torchvision",
                "torchaudio",
                "--index-url",
                "https://download.pytorch.org/whl/nightly/cu124",
            ],
            capture_output=True,
            text=True,
        )

    if result.returncode == 0:
        print(f"{GREEN}[OK]{NC} GPU PyTorch installed")
        return True
    else:
        print(f"{RED}[ERROR]{NC} GPU PyTorch could not be installed")
        return False


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(script_dir, "venv")
    app_path = os.path.join(script_dir, "app.py")
    req_file = os.path.join(script_dir, "requirements.txt")

    # Get venv python
    if os.name == "nt":
        python_in_venv = os.path.join(venv_path, "Scripts", "python.exe")
        pip_in_venv = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        python_in_venv = os.path.join(venv_path, "bin", "python")
        pip_in_venv = os.path.join(venv_path, "bin", "pip")

    print(f"{CYAN}============================================================{NC}")
    print(f"{CYAN}  Qwen3-TTS Web GUI{NC}")
    print(f"{CYAN}============================================================{NC}")
    print()

    # Check/create venv
    if not os.path.exists(python_in_venv):
        print(f"{YELLOW}[1/4]{NC} Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        print(f"{GREEN}[OK]{NC} Virtual environment created")
    else:
        print(f"{GREEN}[OK]{NC} Virtual environment exists")
    print()

    # Install GPU PyTorch first
    print(f"{YELLOW}[2/4]{NC} Installing GPU PyTorch...")
    install_gpu_pytorch(pip_in_venv)
    print()

    # Install other requirements
    print(f"{YELLOW}[3/4]{NC} Installing dependencies...")
    result = subprocess.run(
        [pip_in_venv, "install", "-r", req_file], capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"{RED}[ERROR]{NC} Installation failed:")
        print(result.stderr)
        sys.exit(1)
    print(f"{GREEN}[OK]{NC} Dependencies installed")
    print()

    # Start app
    print(f"{YELLOW}[4/4]{NC} Starting server...")
    print()
    print(f"{CYAN}============================================================{NC}")
    print(f"{CYAN}  Web GUI is available at http://localhost:5000{NC}")
    print(f"{CYAN}  Press CTRL+C to stop{NC}")
    print(f"{CYAN}============================================================{NC}")
    print()

    subprocess.run([python_in_venv, app_path])


if __name__ == "__main__":
    main()
