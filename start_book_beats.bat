@echo off
setlocal
cd /d "%~dp0"

set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" set "VENV_PYTHON=%~dp0.venv\bin\python.exe"

set "NEED_VENV=0"
if not exist "%VENV_PYTHON%" set "NEED_VENV=1"
if "%NEED_VENV%"=="0" (
    "%VENV_PYTHON%" --version >nul 2>nul
    if errorlevel 1 set "NEED_VENV=1"
)

if "%NEED_VENV%"=="1" (
    echo [Book Beats] Creating the virtual environment...
    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 -m venv --clear "%~dp0.venv"
    ) else (
        where python >nul 2>nul
        if errorlevel 1 (
            echo [Book Beats] Python was not found. Install Python 3.11 or newer, then run this file again.
            pause
            exit /b 1
        )
        python -m venv --clear "%~dp0.venv"
    )
    if errorlevel 1 (
        echo [Book Beats] Could not create the virtual environment.
        pause
        exit /b 1
    )
    if not exist "%VENV_PYTHON%" if exist "%~dp0.venv\Scripts\python.exe" set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"
    if not exist "%VENV_PYTHON%" if exist "%~dp0.venv\bin\python.exe" set "VENV_PYTHON=%~dp0.venv\bin\python.exe"
)

"%VENV_PYTHON%" -c "import flask, requests, dotenv" >nul 2>nul
if errorlevel 1 (
    echo [Book Beats] Installing required packages...
    "%VENV_PYTHON%" -m pip install -r "%~dp0requirements.txt"
    if errorlevel 1 (
        echo [Book Beats] Dependency installation failed. Check your network connection and try again.
        pause
        exit /b 1
    )
)

echo [Book Beats] Starting at http://127.0.0.1:5000
start "Book Beats server" /D "%~dp0" "%VENV_PYTHON%" "%~dp0main.py"
%SystemRoot%\System32\ping.exe 127.0.0.1 -n 3 >nul
start "" "http://127.0.0.1:5000"
endlocal
