@echo off
REM Install Python dependencies and run create_cookie.py

REM Change to script directory using pushd (supports UNC paths)
pushd "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed, please install Python3 first
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ===== Upgrading pip =====
python -m pip install --upgrade pip

REM Install dependencies
echo ===== Installing Python dependencies =====
pip install -r requirements.txt

if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo Dependencies installed successfully

REM Run create_cookie.py
echo ===== Running create_cookie.py =====
python create_cookie.py

echo ===== Execution completed =====
popd
pause