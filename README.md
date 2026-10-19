# MiniTask Desktop v3

A visual polish pass for the floating widget. Existing task-panel functions, local storage, Windows startup toggle, and EXE build process are retained.

## Run from source
Install Python from https://www.python.org/downloads/windows/ and enable **Add python.exe to PATH**. Open this folder in File Explorer, type `cmd` in the address bar, then run `python main.py`.

## Widget
- Left-click to open tasks; drag to move; right-click for the menu.
- Ring shows completed-task percentage; center number shows tasks remaining.
- Right-click → Start with Windows enables/disables startup.

## Build EXE
Double-click `build_exe.bat`. Output: `dist\MiniTask.exe`. The free PyInstaller install requires internet for the initial build.

Enable Windows startup only after copying the EXE to a permanent folder. Tasks remain at `%APPDATA%\MiniTask\tasks.json`.
