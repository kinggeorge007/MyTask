@echo off
setlocal
cd /d "%~dp0"
echo MiniTask - Windows EXE Builder
where py >nul 2>nul
if errorlevel 1 (echo Python was not found. Install it from https://www.python.org/downloads/windows/ and tick Add Python to PATH. & pause & exit /b 1)
py -m pip install --upgrade pyinstaller
if errorlevel 1 (echo PyInstaller install failed. Check internet and try again. & pause & exit /b 1)
py -m PyInstaller --noconfirm --clean --onefile --windowed --name MiniTask main.py
if errorlevel 1 (echo Build failed. Read the error above. & pause & exit /b 1)
echo Build complete: dist\MiniTask.exe
echo Copy the EXE to a permanent folder, run it, then right-click widget and enable Start with Windows.
pause
