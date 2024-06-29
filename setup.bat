@echo off

:: Check for Python 3.8.x
python --version 2>nul | findstr /r "Python 3\.8\.[0-9]*"
if %errorlevel% neq 0 (
    echo Please install Python 3.8.x before running this script.
    pause
    exit /b
)

:: Check if venv directory exists
if not exist "venv\Scripts\activate" (
    echo Virtual environment not found. Creating a new one...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

:: Check if dependencies are installed
pip freeze > current_requirements.txt
fc requirements.txt current_requirements.txt > nul
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    del current_requirements.txt
)

@REM echo Running project...
@REM python main_script.py

pause
