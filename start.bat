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
    pip install flask flask-cors torch torchaudio qwen-tts soundfile transformers accelerate sentencepiece
)
echo [3/4] Dependencies ready
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
