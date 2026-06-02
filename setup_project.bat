@echo off
REM ============================================================
REM  setup_project.bat
REM  Bluestock Fintech – Mutual Fund Analytics Platform
REM  Windows one-click setup script
REM ============================================================

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   Bluestock MF Capstone – Project Setup         ║
echo  ╚══════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
echo [OK] Python found.

REM Create virtual environment
IF NOT EXIST "venv\" (
    echo [INFO] Creating virtual environment ...
    python -m venv venv
)
echo [OK] Virtual environment ready.

REM Activate and install
echo [INFO] Installing dependencies ...
call venv\Scripts\activate.bat
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo [OK] Dependencies installed.

REM Create logs directory
IF NOT EXIST "logs\" mkdir logs
echo [OK] Logs directory created.

REM Run ETL pipeline
echo.
echo [INFO] Running ETL Pipeline ...
python scripts\run_pipeline.py
echo [OK] ETL complete.

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   Setup COMPLETE! Launch Jupyter:               ║
echo  ║   > venv\Scripts\jupyter notebook notebooks\    ║
echo  ╚══════════════════════════════════════════════════╝
echo.
pause
