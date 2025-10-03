@echo off
REM Serve MkDocs Documentation
REM This script starts the MkDocs development server with live reload

echo Starting MkDocs documentation server...
echo Documentation will be available at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if MkDocs is installed
mkdocs --version >nul 2>&1
if %errorlevel% neq 0 (
    echo MkDocs not found. Installing...
    pip install -r requirements.txt
)

REM Serve documentation
mkdocs serve --dev-addr=127.0.0.1:8000

pause
