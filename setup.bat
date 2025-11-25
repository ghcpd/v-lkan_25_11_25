@echo off
REM Enterprise Knowledge Graph Extraction Benchmark (KGEB)
REM Setup script for Windows

echo ==========================================
echo KGEB Setup Script
echo ==========================================

REM Check Python version
echo Checking Python version...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python not found. Please install Python 3.10 or higher.
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to create virtual environment.
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install requirements.
    exit /b 1
)

REM Download spaCy model
echo Downloading spaCy language model...
python -m spacy download en_core_web_sm
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Failed to download spaCy model. You may need to run this manually.
)

REM Create output directories
echo Creating output directories...
if not exist output mkdir output
if not exist logs mkdir logs
if not exist test_results mkdir test_results

echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo To activate the environment, run:
echo   venv\Scripts\activate
echo.
echo To run the benchmark, use:
echo   python main.py --help
echo.
pause
