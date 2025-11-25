@echo off
REM KGEB Setup Script for Windows
REM Sets up the development environment for KGEB

setlocal enabledelayedexpansion

echo.
echo ========================================
echo KGEB - Setup Environment (Windows)
echo ========================================
echo.

REM Check Python version
echo [1/4] Checking Python version...
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Create virtual environment (optional)
if "%1"=="--venv" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Virtual environment created and activated
) else (
    echo [2/4] Skipping virtual environment (use --venv flag to create one)
)

REM Install dependencies
echo [3/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)
echo Dependencies installed

REM Create necessary directories
echo [4/4] Creating directories...
if not exist data mkdir data
if not exist output mkdir output
if not exist logs mkdir logs
echo Directories created

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the pipeline, use:
echo   python src\pipeline.py documents.txt
echo.
echo To run tests, use:
echo   python tests\test_kgeb.py
echo.
