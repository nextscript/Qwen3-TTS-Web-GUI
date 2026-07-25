#!/usr/bin/env python3
"""Launcher for Qwen3-TTS Web GUI - Auto-detects NVIDIA, AMD, Intel GPUs"""

import os
import subprocess
import sys

GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def has_nvidia_gpu():
    """Detect NVIDIA GPU without PyTorch."""
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["reg", "query", r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10316}\0000", "/v", "DriverDesc"],
                capture_output=True, text=True, timeout=5
            )
            if "NVIDIA" in result.stdout:
                return True
        except Exception:
            pass
        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    else:
        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False


def has_amd_gpu():
    """Detect AMD GPU without PyTorch."""
    if os.name == "nt":
        # Windows: check Device Manager registry for AMD GPUs
        try:
            result = subprocess.run(
                ["reg", "query", r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10316}", "/s", "/v", "DriverDesc"],
                capture_output=True, text=True, timeout=5
            )
            if "AMD" in result.stdout or "Radeon" in result.stdout or "Radeon" in result.stdout:
                return True
        except Exception:
            pass
        # Check for AMD Vulkan driver
        try:
            result = subprocess.run(["vulkaninfo", "--summary"], capture_output=True, timeout=5)
            if "AMD" in result.stdout:
                return True
        except Exception:
            pass
        return False
    else:
        # Linux: check for AMDGPU
        try:
            result = subprocess.run(["lspci"], capture_output=True, text=True, timeout=5)
            if "amd" in result.stdout.lower() or "radeon" in result.stdout.lower() or "advanced micro devices" in result.stdout.lower():
                return True
        except Exception:
            pass
        # Check for ROCm
        try:
            result = subprocess.run(["rocm-smi"], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            pass
        return False


def has_intel_gpu():
    """Detect Intel GPU without PyTorch."""
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["reg", "query", r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10316}\0000", "/v", "DriverDesc"],
                capture_output=True, text=True, timeout=5
            )
            if "Intel" in result.stdout or "UHD" in result.stdout or "Iris" in result.stdout:
                return True
        except Exception:
            pass
        return False
    else:
        try:
            result = subprocess.run(["lspci"], capture_output=True, text=True, timeout=5)
            if "intel" in result.stdout.lower():
                return True
        except Exception:
            pass
        return False


def install_gpu_pytorch(pip_in_venv, gpu_type="nvidia"):
    """Install PyTorch with GPU support automatically."""
    if gpu_type == "nvidia":
        print(f"{YELLOW}[GPU-PyTorch]{NC} Installing PyTorch with NVIDIA CUDA support...")
        # Try CUDA 13.2 first (RTX 50xx series)
        cuda_index = "https://download.pytorch.org/whl/nightly/cu132"
        result = subprocess.run(
            [pip_in_venv, "install", "--pre", "torch", "torchvision", "torchaudio", "--index-url", cuda_index],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"{YELLOW}[WARN]{NC} CUDA 13.2 failed, trying CUDA 12.4...")
            result = subprocess.run(
                [pip_in_venv, "install", "--pre", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/nightly/cu124"],
                capture_output=True, text=True,
            )
        if result.returncode == 0:
            print(f"{GREEN}[OK]{NC} CUDA PyTorch installed")
            return True
    elif gpu_type == "amd":
        print(f"{YELLOW}[GPU-PyTorch]{NC} Installing PyTorch with Vulkan support for AMD...")
        # PyTorch 2.6+ has experimental Vulkan support
        result = subprocess.run(
            [pip_in_venv, "install", "torch", "torchvision", "torchaudio"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print(f"{GREEN}[OK]{NC} Vulkan PyTorch installed")
            return True
    elif gpu_type == "intel":
        print(f"{YELLOW}[GPU-PyTorch]{NC} Installing PyTorch with Intel GPU (Vulkan) support...")
        result = subprocess.run(
            [pip_in_venv, "install", "torch", "torchvision", "torchaudio"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print(f"{GREEN}[OK]{NC} Intel GPU PyTorch installed")
            return True
    return False


def install_cpu_pytorch(pip_in_venv):
    """Install CPU-only PyTorch (fast)."""
    print(f"{GREEN}[CPU]{NC} Installing CPU-only PyTorch (fast)...")
    result = subprocess.run(
        [pip_in_venv, "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cpu"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f"{GREEN}[OK]{NC} CPU PyTorch installed")
        return True
    else:
        print(f"{YELLOW}[WARN]{NC} CPU index failed, using default...")
        result = subprocess.run(
            [pip_in_venv, "install", "torch", "torchvision", "torchaudio"],
            capture_output=True, text=True,
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

    # Auto-detect GPU and install appropriate PyTorch
    print(f"{YELLOW}[2/4]{NC} Detecting GPU...")
    if has_nvidia_gpu():
        print(f"{GREEN}[OK]{NC} NVIDIA GPU found — installing CUDA PyTorch")
        install_gpu_pytorch(pip_in_venv, gpu_type="nvidia")
    elif has_amd_gpu():
        print(f"{GREEN}[OK]{NC} AMD GPU found — installing Vulkan PyTorch")
        install_gpu_pytorch(pip_in_venv, gpu_type="amd")
    elif has_intel_gpu():
        print(f"{GREEN}[OK]{NC} Intel GPU found — installing Vulkan PyTorch")
        install_gpu_pytorch(pip_in_venv, gpu_type="intel")
    else:
        print(f"{YELLOW}[INFO]{NC} No GPU found — installing CPU PyTorch")
        install_cpu_pytorch(pip_in_venv)
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
