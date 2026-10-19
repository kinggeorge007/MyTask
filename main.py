import json, os, sys, tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path

APP_NAME = "MiniTask"
ACCENT = "#72E6BD"
TRACK = "#354251"
TEXT = "#F5F7FB"
MUTED = "#A8B5C4"
PANEL = "#1E2631"
ROW = "#293442"
TRANSPARENT_KEY = "#FF00FF"

def app_data_dir():
    root = Path(os.environ.get("APPDATA", str(Path.home()))) if os.name == "nt" else Path.home()
    folder = root / ("MiniTask" if os.name == "nt" else ".minitask")
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def startup_dir():
    appdata = os.environ.get("APPDATA")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" if appdata else None

def launch_command():
    if getattr(sys, "frozen", False):
        return f'"{Path(sys.executable).resolve()}"'
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    runner = pythonw if pythonw.exists() else Path(sys.executable)
    return f'"{runner.resolve()}" "{Path(__file__).resolve()}"'

def startup_path():
    folder = startup_dir()
    return folder / "MiniTask Startup.vbs" if folder else None

def startup_enabled():
    path = startup_path()
    return bool(path and path.exists())

def set_startup(enabled):
    path = startup_path()
    if not path:
        raise RuntimeError("Windows Startup folder could not be found.")
    if enabled:
        path.parent.mkdir(parents=True, exist_ok=True)
        command = launch_command().replace('"', '""')
        path.write_text('Set shell = CreateObject("WScript.Shell")\\n' + f'shell.Run "{command}", 0, False\\n', encoding="utf-8")
    elif path.exists():
        path.unlink()

class MiniTask:
    def __init__(self):
        self.path = app_data_dir() / "tasks.json"
        self.tasks = self.load_tasks()
        self.panel = None
        self.task_list_frame = None
        self.count_label = None
        self.drag_origin = None
        self.drag_moved = False
        self.hovered = False
        self.size = 88

        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=TRANSPARENT_KEY)
        self.root.resizable(False, False)
        if sys.platform == "win32":
            try:
                self.root.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
            except tk.TclError:
                pass

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{self.size}x{self.size}+{sw-124}+{max(32, sh//2)}")
        self.canvas = tk.Canvas(self.root, width=self.size, height=self.size, bg=TRANSPARENT_KEY, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_widget()
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.show_menu)
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Open tasks", command=self.open_panel)
        self.menu.add_command(label="Add task", command=self.add_task_dialog)
        self.menu.add_separator()
        self.startup_var = tk.BooleanVar(value=startup_enabled())
        self.menu.add_checkbutton(label="Start with Windows", variable=self.startup_var, command=self.toggle_startup)
        self.menu.add_separator()
        self.menu.add_command(label="Quit MiniTask", command=self.quit)
        self.root.mainloop()

    def load_tasks(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [{"title": str(x.get("title", "Untitled task")), "done": bool(x.get("done", False))}
                        for x in data if isinstance(x, dict)]
        except (OSError, json.JSONDecodeError, TypeError):
            pass
        return []

    def save_tasks(self):
        try:
            self.path.write_text(json.dumps(self.tasks, indent=2, ensure_ascii=False), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not save your tasks:\\n{exc}")

    def on_enter(self, _event):
        self.hovered = True
        self.draw_widget()

    def on_leave(self, _event):
        self.hovered = False
        self.draw_widget()

    def draw_widget(self):
        c, s = self.canvas, self.size
        c.delete("all")
        center = s / 2
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task["done"])
        remaining = total - completed
        c.create_oval(10, 12, s-6, s-4, fill="#111820", outline="")
        c.create_oval(7, 7, s-7, s-7, fill="#25303D", outline="#526274" if self.hovered else "#354251", width=1)
        box = (10, 10, s-10, s-10)
        c.create_arc(*box, start=90, extent=-359.9, style="arc", outline=TRACK, width=5)
        if total and completed:
            c.create_arc(*box, start=90, extent=-359.9 * (completed / total), style="arc", outline=ACCENT, width=5)
        c.create_oval(17, 17, s-17, s-17, fill="#202A36", outline="#3B4B5C" if self.hovered else "#2D3A49", width=1)
        c.create_text(center, center-5, text=str(remaining), fill=TEXT, font=("Segoe UI", 20, "bold"))
        c.create_text(center, center+16, text="LEFT", fill=MUTED, font=("Segoe UI", 7, "bold"))
        if total and remaining == 0:
            c.create_oval(s-25, 12, s-13, 24, fill="#9AF5D7", outline="#202A36", width=2)
        if self.hovered:
            c.create_rectangle(20, s-2, s-20, s+12, fill="#202A36", outline="#354251")
            c.create_text(center, s+5, text="MINITASK", fill=TEXT, font=("Segoe UI", 6, "bold"))

    def on_press(self, event):
        self.drag_origin = (event.x_root, event.y_root, self.root.winfo_x(), self.root.winfo_y())
        self.drag_moved = False

    def on_motion(self, event):
        if not self.drag_origin:
            return
        x0, y0, wx, wy = self.drag_origin
        dx, dy = event.x_root-x0, event.y_root-y0
        if abs(dx)+abs(dy) > 5:
            self.drag_moved = True
        if self.drag_moved:
            sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.root.geometry(f"+{min(max(0, wx+dx), max(0, sw-self.size))}+{min(max(0, wy+dy), max(0, sh-self.size))}")

    def on_release(self, _event):
        moved = self.drag_moved
        self.drag_origin = None
        self.drag_moved = False
        if not moved:
            self.open_panel()

    def show_menu(self, event):
        self.startup_var.set(startup_enabled())
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def toggle_startup(self):
        enabled = bool(self.startup_var.get())
        try:
            set_startup(enabled)
        except Exception as exc:
            self.startup_var.set(not enabled)
            messagebox.showerror(APP_NAME, f"Could not update Windows startup:\\n{exc}")
            return
        self.startup_var.set(startup_enabled())

    def open_panel(self):
        if self.panel and self.panel.winfo_exists():
            self.panel.deiconify()
            self.panel.lift()
            self.panel.focus_force()
            self.refresh_task_list()
            return
        self.panel = tk.Toplevel(self.root)
        self.panel.title("MiniTask — My Tasks")
        self.panel.geometry("380x500")
        self.panel.minsize(320, 380)
        self.panel.configure(bg=PANEL)
        self.panel.attributes("-topmost", True)
        self.panel.protocol("WM_DELETE_WINDOW", self.panel.withdraw)
        header = tk.Frame(self.panel, bg=PANEL, padx=18, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="My Tasks", bg=PANEL, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        self.count_label = tk.Label(header, text="", bg=PANEL, fg=MUTED, font=("Segoe UI", 9))
        self.count_label.pack(anchor="w", pady=(3, 0))
        add_row = tk.Frame(self.panel, bg=PANEL, padx=18)
        add_row.pack(fill="x", pady=(0, 12))
        self.new_task_entry = tk.Entry(add_row, bg=ROW, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10))
        self.new_task_entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        self.new_task_entry.bind("<Return>", lambda _e: self.add_task_from_entry())
        tk.Button(add_row, text="+", command=self.add_task_from_entry, bg=ACCENT, fg="#14221c", activebackground=ACCENT, relief="flat", font=("Segoe UI", 13, "bold"), width=3, cursor="hand2").pack(side="right")
        self.task_list_frame = tk.Frame(self.panel, bg=PANEL, padx=18)
        self.task_list_frame.pack(fill="both", expand=True)
        footer = tk.Frame(self.panel, bg=PANEL, padx=18, pady=12)
        footer.pack(fill="x")
        tk.Button(footer, text="Clear completed", command=self.clear_completed, bg=ROW, fg=TEXT, activebackground=ROW, activeforeground=TEXT, relief="flat", padx=10, pady=7).pack(side="left")
        tk.Label(footer, text="Saved on this PC", bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(side="right")
        self.refresh_task_list()
        self.new_task_entry.focus_set()

    def add_task_dialog(self):
        title = simpledialog.askstring(APP_NAME, "What do you need to do?", parent=self.root)
        if title and title.strip():
            self.tasks.append({"title": title.strip(), "done": False})
            self.save_tasks(); self.draw_widget(); self.refresh_task_list()

    def add_task_from_entry(self):
        if not self.panel or not self.panel.winfo_exists():
            return
        title = self.new_task_entry.get().strip()
        if title:
            self.tasks.append({"title": title, "done": False})
            self.new_task_entry.delete(0, "end")
            self.save_tasks(); self.draw_widget(); self.refresh_task_list()

    def toggle_task(self, index):
        self.tasks[index]["done"] = not self.tasks[index]["done"]
        self.save_tasks(); self.draw_widget(); self.refresh_task_list()

    def delete_task(self, index):
        del self.tasks[index]
        self.save_tasks(); self.draw_widget(); self.refresh_task_list()

    def clear_completed(self):
        self.tasks = [task for task in self.tasks if not task["done"]]
        self.save_tasks(); self.draw_widget(); self.refresh_task_list()

    def refresh_task_list(self):
        if not self.panel or not self.panel.winfo_exists() or self.task_list_frame is None:
            return
        for child in self.task_list_frame.winfo_children():
            child.destroy()
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task["done"])
        if self.count_label and self.count_label.winfo_exists():
            self.count_label.config(text=f"{completed} of {total} completed  •  {total-completed} remaining")
        if not self.tasks:
            tk.Label(self.task_list_frame, text="No tasks yet.\\nAdd one above to get started.", bg=PANEL, fg=MUTED, justify="center", font=("Segoe UI", 10)).pack(expand=True, pady=35)
            return
        for index, task in enumerate(self.tasks):
            row = tk.Frame(self.task_list_frame, bg=ROW, padx=8, pady=7)
            row.pack(fill="x", pady=4)
            checked = tk.BooleanVar(value=task["done"])
            tk.Checkbutton(row, variable=checked, command=lambda i=index: self.toggle_task(i), bg=ROW, activebackground=ROW, selectcolor=PANEL, fg=ACCENT, activeforeground=ACCENT, relief="flat", highlightthickness=0).pack(side="left")
            color = MUTED if task["done"] else TEXT
            font = ("Segoe UI", 9, "overstrike") if task["done"] else ("Segoe UI", 9)
            tk.Label(row, text=task["title"], bg=ROW, fg=color, font=font, anchor="w", justify="left", wraplength=245).pack(side="left", fill="x", expand=True, padx=(4, 5))
            tk.Button(row, text="×", command=lambda i=index: self.delete_task(i), bg=ROW, fg=MUTED, activebackground=ROW, activeforeground=TEXT, relief="flat", font=("Segoe UI", 12)).pack(side="right")

    def quit(self):
        if messagebox.askyesno(APP_NAME, "Close MiniTask? Your tasks are saved on this PC."):
            self.root.destroy()

if __name__ == "__main__":
    MiniTask()
