@echo off
REM KGEB Runtime Script for Windows
REM Executes the complete KGEB pipeline with one command

setlocal enabledelayedexpansion

echo.
echo ========================================
echo KGEB - Knowledge Graph Extraction
echo ========================================
echo.

REM Check if input file is provided
set INPUT_FILE=documents.txt
if not "%1"=="" (
    set INPUT_FILE=%1
)

REM Check if input file exists
if not exist "!INPUT_FILE!" (
    echo Error: Input file '!INPUT_FILE!' not found
    exit /b 1
)

REM Get current timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set TIMESTAMP=!mydate!_!mytime!

echo Input file: !INPUT_FILE!
echo Timestamp: !TIMESTAMP!
echo.

REM Run tests first
echo Step 1: Running tests...
python tests\test_kgeb.py
if errorlevel 1 (
    echo Tests failed
    exit /b 1
)
echo Tests passed

echo.
echo Step 2: Running extraction and evaluation pipeline...
python src\pipeline.py "!INPUT_FILE!" "KGEB-!TIMESTAMP!"

echo.
echo ========================================
echo Pipeline completed successfully!
echo ========================================
echo.
echo Output files:
echo   - output\entities_output.json
echo   - output\relations_output.json
echo   - output\evaluation_report.json
echo.
