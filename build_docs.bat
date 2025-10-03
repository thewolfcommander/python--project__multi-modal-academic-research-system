@echo off
REM Build MkDocs Documentation
REM This script builds the static documentation site

echo Building MkDocs documentation...
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

REM Clean previous build
if exist "site" (
    echo Removing previous build...
    rmdir /s /q site
)

REM Build documentation
echo Building site...
mkdocs build --strict

REM Check build status
if %errorlevel% equ 0 (
    echo.
    echo Documentation built successfully!
    echo Output directory: site\
    echo.
    echo To deploy to GitHub Pages, run:
    echo   mkdocs gh-deploy
) else (
    echo.
    echo Build failed. Check the errors above.
    exit /b 1
)

pause
