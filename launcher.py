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
    """Install PyTorch with CUDA GPU support."""
    print(f"{YELLOW}[GPU-PyTorch]{NC} Installing PyTorch with CUDA support...")

    # Try nightly CUDA 13.2 first (supports Blackwell/sm_120 RTX 50xx)
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
        print(f"{YELLOW}[WARN]{NC} CUDA 13.2 nightly failed, trying CUDA 12.4 nightly...")
        # Fallback to CUDA 12.4 nightly (supports up to sm_90)
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

    if result.returncode != 0:
        print(f"{YELLOW}[WARN]{NC} Nightly CUDA failed, trying stable CUDA 12.4...")
        result = subprocess.run(
            [
                pip_in_venv,
                "install",
                "torch",
                "torchvision",
                "torchaudio",
                "--index-url",
                "https://download.pytorch.org/whl/cu124",
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


def install_cpu_pytorch(pip_in_venv):
    """Install CPU-only PyTorch (fast)."""
    print(f"{GREEN}[CPU]{NC} Installing CPU-only PyTorch (fast)...")
    result = subprocess.run(
        [
            pip_in_venv,
            "install",
            "torch",
            "torchvision",
            "torchaudio",
            "--index-url",
            "https://download.pytorch.org/whl/cpu",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"{GREEN}[OK]{NC} CPU PyTorch installed")
        return True
    else:
        print(f"{YELLOW}[WARN]{NC} CPU index failed, using default...")
        result = subprocess.run(
            [pip_in_venv, "install", "torch", "torchvision", "torchaudio"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"{GREEN}[OK]{NC} PyTorch installed")
            return True
    return False


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(script_dir, "venv")
    app_path = os.path.join(script_dir, "app.py")
    req_file = os.path.join(script_dir, "requirements.txt")

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

    # Always install GPU PyTorch first - it auto-detects GPU at runtime
    print(f"{YELLOW}[2/4]{NC} Installing PyTorch...")
    # Force reinstall GPU PyTorch to ensure CUDA version is used
    print(f"{YELLOW}[INFO]{NC} Uninstalling existing PyTorch...")
    subprocess.run([pip_in_venv, "uninstall", "-y", "torch", "torchvision", "torchaudio"], capture_output=True)
    print(f"{YELLOW}[INFO]{NC} Installing GPU PyTorch...")
    installed_gpu = install_gpu_pytorch(pip_in_venv)
    if not installed_gpu:
        print(f"{YELLOW}[WARN]{NC} GPU PyTorch failed, falling back to CPU...")
        install_cpu_pytorch(pip_in_venv)
    print()

    # Install other requirements
    print(f"{YELLOW}[3/4]{NC} Installing dependencies...")
    result = subprocess.run([pip_in_venv, "install", "-r", req_file], capture_output=True, text=True)
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
