@echo off
setlocal
cd /d "%~dp0"
echo Building MiniTask...
py -m pip install --upgrade pyinstaller
if errorlevel 1 goto failed
py -m PyInstaller --noconfirm --clean --onefile --windowed --name MiniTask main.py
if errorlevel 1 goto failed
echo.
echo Done. Your app is at dist\MiniTask.exe
pause
exit /b 0
:failed
echo Build failed. Confirm Python is installed and internet is available.
pause
exit /b 1
