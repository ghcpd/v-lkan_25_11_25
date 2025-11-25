@echo off
REM KGEB Test Runner Script for Windows
REM One-click script to run all tests

echo ==========================================
echo KGEB Test Suite Runner
echo ==========================================

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo Warning: Virtual environment not activated!
    echo Please run: venv\Scripts\activate
    exit /b 1
)

REM Create test results directory
if not exist test_results mkdir test_results

REM Run tests with coverage
echo.
echo Running tests with coverage...
pytest test_kgeb.py -v --cov=. --cov-report=html --cov-report=term --cov-report=json --junitxml=test_results/junit.xml --html=test_results/report.html --self-contained-html

REM Check if tests passed
if %ERRORLEVEL% EQU 0 (
    echo.
    echo All tests passed!
    echo.
    echo Test reports generated:
    echo    - HTML Report: test_results\report.html
    echo    - Coverage Report: htmlcov\index.html
    echo    - JUnit XML: test_results\junit.xml
    echo    - Coverage JSON: coverage.json
) else (
    echo.
    echo Tests failed!
    exit /b 1
)

echo.
echo ==========================================
echo Test run complete!
echo ==========================================
