@echo off
REM ============================================================================
REM Dual N-Back Game - Auto Installer and Launcher
REM This script will:
REM   1. Check if Python is installed, if not - install it
REM   2. Install required dependencies
REM   3. Launch the game
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo           DUAL N-BACK GAME - Installer and Launcher
echo ============================================================================
echo.

REM Set colors for better visibility
color 0A

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [INFO] Script directory: %SCRIPT_DIR%
echo.

REM ============================================================================
REM CHECK FOR PYTHON
REM ============================================================================

echo [STEP 1/3] Checking for Python installation...
echo.

REM Try to find Python
set "PYTHON_CMD="

REM Check 'python' command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Found Python !PYTHON_VERSION! using 'python' command
    goto :python_found
)

REM Check 'python3' command
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3"
    for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Found Python !PYTHON_VERSION! using 'python3' command
    goto :python_found
)

REM Check 'py' launcher
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    for /f "tokens=2" %%i in ('py --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Found Python !PYTHON_VERSION! using 'py' launcher
    goto :python_found
)

REM Python not found - need to install
echo [WARNING] Python is not installed or not in PATH.
echo.
echo [INFO] Python is required to run this game.
echo [INFO] Would you like to download and install Python automatically?
echo.

choice /C YN /M "Install Python now"
if %errorlevel% equ 2 (
    echo.
    echo [INFO] Installation cancelled. Please install Python manually from:
    echo        https://www.python.org/downloads/
    echo [INFO] Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

REM Download and install Python
echo.
echo [INFO] Downloading Python installer...
echo.

REM Create temp directory if needed
if not exist "%TEMP%\nback_install" mkdir "%TEMP%\nback_install"

REM Set Python installer URL (Python 3.11.x - stable and widely compatible)
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
set "PYTHON_INSTALLER=%TEMP%\nback_install\python_installer.exe"

REM Try to download using PowerShell
echo [INFO] Downloading from: %PYTHON_URL%
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing}" 2>nul

if not exist "%PYTHON_INSTALLER%" (
    REM Try with curl if PowerShell failed
    echo [INFO] Trying alternative download method...
    curl -L -o "%PYTHON_INSTALLER%" "%PYTHON_URL%" 2>nul
)

if not exist "%PYTHON_INSTALLER%" (
    echo.
    echo [ERROR] Failed to download Python installer.
    echo [INFO] Please download Python manually from:
    echo        https://www.python.org/downloads/
    echo [INFO] Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Installing Python...
echo [INFO] This may take a few minutes. Please wait...
echo [INFO] A UAC prompt may appear - please allow the installation.
echo.

REM Install Python silently with pip and add to PATH
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_tcltk=1

if %errorlevel% neq 0 (
    echo [WARNING] Silent installation failed. Launching interactive installer...
    echo [INFO] Please make sure to:
    echo        1. Check "Add Python to PATH" at the bottom of the first screen
    echo        2. Click "Install Now"
    echo.
    start /wait "" "%PYTHON_INSTALLER%"
)

REM Clean up installer
del "%PYTHON_INSTALLER%" 2>nul

REM Refresh environment variables
echo.
echo [INFO] Refreshing environment variables...

REM Force PATH refresh using PowerShell
for /f "tokens=*" %%a in ('powershell -Command "[System.Environment]::GetEnvironmentVariable('Path', 'User')"') do (
    set "USER_PATH=%%a"
)
for /f "tokens=*" %%a in ('powershell -Command "[System.Environment]::GetEnvironmentVariable('Path', 'Machine')"') do (
    set "MACHINE_PATH=%%a"
)
set "PATH=%USER_PATH%;%MACHINE_PATH%"

REM Check Python again
timeout /t 2 /nobreak >nul

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    echo [OK] Python installed successfully!
    goto :python_found
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    echo [OK] Python installed successfully!
    goto :python_found
)

echo.
echo [WARNING] Python was installed but may require a restart.
echo [INFO] Please restart your computer and run this script again.
echo [INFO] Or manually run: python "%SCRIPT_DIR%dual_nback.py"
echo.
pause
exit /b 1

:python_found

REM ============================================================================
REM CHECK/INSTALL DEPENDENCIES
REM ============================================================================

echo.
echo [STEP 2/3] Checking dependencies...
echo.

REM The game uses tkinter which comes with Python by default
REM Check if tkinter is available
%PYTHON_CMD% -c "import tkinter" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] tkinter is not available.
    echo [INFO] tkinter should come with Python by default on Windows.
    echo [INFO] If you installed Python from source, you may need to reinstall with Tk support.
    echo.
    pause
    exit /b 1
)

echo [OK] All dependencies are available!

REM ============================================================================
REM LAUNCH THE GAME
REM ============================================================================

echo.
echo [STEP 3/3] Launching Dual N-Back Game...
echo.
echo ============================================================================
echo           GAME CONTROLS
echo ============================================================================
echo   [A] key     - Position Match
echo   [L] key     - String Match  
echo   [SPACE]     - Pause/Resume
echo   [ESC]       - End Game
echo ============================================================================
echo.

REM Check if game file exists
if not exist "%SCRIPT_DIR%dual_nback.py" (
    echo [ERROR] Game file not found: %SCRIPT_DIR%dual_nback.py
    echo [INFO] Please ensure dual_nback.py is in the same directory as this script.
    pause
    exit /b 1
)

REM Launch the game
echo [INFO] Starting game...
echo [INFO] (You can close this window after the game starts)
echo.

%PYTHON_CMD% "%SCRIPT_DIR%dual_nback.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Game exited with an error.
    echo [INFO] Please check that all files are present and try again.
    pause
    exit /b 1
)

echo.
echo [INFO] Game closed. Thanks for playing!
echo.

REM Keep window open briefly
timeout /t 3 /nobreak >nul

exit /b 0

