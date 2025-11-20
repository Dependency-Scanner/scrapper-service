@echo off
echo ========================================
echo Dependency Scanner - Setup Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Trying 'py' command...
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

echo Python found!
echo.

REM Create virtual environment
echo Creating virtual environment...
%PYTHON_CMD% -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created successfully!
echo.

REM Activate virtual environment and install dependencies
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To use the scanner:
echo   1. Activate the virtual environment: venv\Scripts\activate.bat
echo   2. Run: python scanner.py <url>
echo.
pause

