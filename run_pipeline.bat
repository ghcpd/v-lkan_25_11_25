@echo off
REM KGEB Full Pipeline Runner for Windows

echo ==========================================
echo KGEB Full Pipeline
echo ==========================================

REM Default parameters
set DOCUMENTS=documents.txt
set METHOD=KGEB Baseline Method
set OUTPUT_DIR=output

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :run_pipeline
if "%~1"=="-d" (
    set DOCUMENTS=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--documents" (
    set DOCUMENTS=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-m" (
    set METHOD=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--method" (
    set METHOD=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-o" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--output" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--help" goto :show_help
if "%~1"=="-h" goto :show_help

echo Unknown option: %~1
echo Use --help for usage information
exit /b 1

:show_help
echo Usage: run_pipeline.bat [OPTIONS]
echo.
echo Options:
echo   -d, --documents PATH    Path to documents file (default: documents.txt)
echo   -m, --method NAME       Method name (default: KGEB Baseline Method)
echo   -o, --output DIR        Output directory (default: output)
echo   -h, --help              Show this help message
exit /b 0

:run_pipeline
REM Check if documents file exists
if not exist "%DOCUMENTS%" (
    echo Error: Documents file not found: %DOCUMENTS%
    exit /b 1
)

REM Create output directory
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist logs mkdir logs

REM Display configuration
echo.
echo Configuration:
echo    Documents: %DOCUMENTS%
echo    Method: %METHOD%
echo    Output: %OUTPUT_DIR%
echo.

REM Run pipeline
python main.py run --documents "%DOCUMENTS%" --method "%METHOD%" --output-dir "%OUTPUT_DIR%"

REM Check if pipeline succeeded
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Pipeline completed successfully!
    echo.
    echo Results:
    echo    - Entities: %OUTPUT_DIR%\entities_output.json
    echo    - Relations: %OUTPUT_DIR%\relations_output.json
    echo    - Evaluation: %OUTPUT_DIR%\evaluation_report.json
) else (
    echo.
    echo Pipeline failed!
    exit /b 1
)
