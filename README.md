# MiniTask Desktop v2 (Windows)

Free floating task widget for Windows 10/11. It uses Python's built-in Tkinter and stores tasks locally.

## Run from source
1. Install Python from https://www.python.org/downloads/windows/ and tick **Add python.exe to PATH**.
2. Open this folder in File Explorer, type `cmd` in the address bar, press Enter.
3. Run `python main.py` (or `py main.py`).

## Controls
- Left-click widget: open task panel.
- Drag widget: move it around the screen.
- Right-click widget: menu.
- Center number: unfinished tasks.
- Green circular arc: percentage of tasks completed.
- Right-click → **Start with Windows** toggles automatic startup.

## Build standalone EXE
1. Python and internet are needed for the one-time build.
2. Double-click `build_exe.bat`.
3. The result is `dist\MiniTask.exe`.
4. Copy the EXE to a permanent folder, such as `Documents\MiniTask\MiniTask.exe`.
5. Run it and right-click the widget → **Start with Windows**. Do not move/delete the EXE after enabling startup unless you disable and re-enable the setting.

PyInstaller is free. The finished EXE does not require Python on the target PC.

## Data
Tasks are stored locally at `%APPDATA%\MiniTask\tasks.json`. Nothing is uploaded online.

Upload `main.py`, `build_exe.bat`, `README.md`, and `.gitignore` to GitHub. Do not upload personal task data or build output.
