@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   Qwen3-TTS Web GUI
echo ============================================================
echo.

:: Find Python
set PYTHON=py
where py >nul 2>&1 || (
    where python >nul 2>&1 && set PYTHON=python || (
        echo [ERROR] Python not found!
        echo Please install Python from https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

!PYTHON! --version
echo.

:: Create virtual environment if not exists
if not exist "venv" (
    echo [1/4] Creating virtual environment...
    !PYTHON! -m venv venv
) else (
    echo [1/4] Virtual environment already exists
)

:: Activate venv
echo [2/4] Installing dependencies...
call venv\Scripts\activate.bat

:: Install requirements
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [WARNING] Installation failed. Trying individual packages...
    pip install flask flask-cors qwen-tts soundfile transformers accelerate sentencepiece
)
echo [OK] Dependencies installed
echo.

:: Install GPU PyTorch (always, to ensure CUDA support)
echo [3/4] Installing GPU PyTorch...
echo [INFO] Uninstalling existing PyTorch...
pip uninstall -y torch torchvision torchaudio >nul 2>&1
echo [INFO] Installing CUDA PyTorch (nightly for RTX 50xx support)...
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu132 >nul 2>&1
if errorlevel 1 (
    echo [WARN] CUDA 13.2 nightly failed, trying CUDA 12.4 nightly...
    pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu124 >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Nightly CUDA failed, trying stable CUDA 12.4...
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 >nul 2>&1
        if errorlevel 1 (
            echo [WARN] CUDA PyTorch failed, trying CPU version...
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu >nul 2>&1
        )
    )
)
echo [OK] PyTorch installed
echo.

echo [4/4] Starting server...
echo.
echo ============================================================
echo   Web-GUI: http://localhost:5000
echo   Press CTRL+C to stop
echo ============================================================
echo.

:: Use py to start the server (python command may point to Windows Store stub)
py app.py
