@echo off
setlocal enabledelayedexpansion
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)
python -m pytest -q
