# MiniTask Desktop (Windows)

A small, free floating task widget for Windows. It uses Python's built-in Tkinter library and stores tasks locally on your PC.

## Features in this first version

- Floating always-on-top button
- Number of unfinished tasks displayed on the button
- Circular progress ring showing completed-task percentage
- Click and drag the widget to move it
- Add, complete, and delete tasks
- Tasks saved locally between launches
- Right-click menu for opening tasks, adding a task, or quitting

## Requirements

- Windows 10 or Windows 11
- Python 3.10+ (Python 3.12 or 3.13 is fine)
- No paid service, server, API key, or third-party Python package

## Run it

1. Install Python from https://www.python.org/downloads/windows/
2. During setup, tick **Add python.exe to PATH**.
3. Download this repository as a ZIP or clone it.
4. Open the project folder in File Explorer.
5. Click the address bar, type `cmd`, and press Enter.
6. In the terminal, run:

   ```bat
   python main.py
   ```

   If that command is not recognized, try:

   ```bat
   py main.py
   ```

The floating widget should appear on your desktop. Left-click it to open the task panel; drag it to move it. Right-click it for the menu.

## Where are tasks saved?

On Windows, tasks are stored at:

`%APPDATA%\MiniTask\tasks.json`

This is normally a path like `C:\Users\YourName\AppData\Roaming\MiniTask\tasks.json`.

The task file is local to your Windows user account and is not uploaded anywhere.

## Put the files on GitHub

1. Create a free GitHub repository, for example `minitask-desktop`.
2. Choose **Add file → Upload files**.
3. Upload `main.py`, `README.md`, and `.gitignore` from this project.
4. Click **Commit changes**.

Do not upload your personal `tasks.json` file if you later find one; it contains your private task list.

## Troubleshooting

- **Python is not recognized:** reinstall Python and tick **Add python.exe to PATH**, or use `py main.py`.
- **Widget appears as a square:** Windows transparency support can vary by desktop setup. The app still works; right-click the widget if clicking is difficult.
- **Widget does not open:** run it from Command Prompt with `python main.py` so you can see any error message.
- **Closing:** right-click the floating widget and choose **Quit MiniTask**.

## Next improvements (after the first version works)

- Start automatically when Windows starts
- Settings and theme choices
- Reminders and due dates
- Package as a standalone `.exe` so Python does not need to be installed on the target PC
