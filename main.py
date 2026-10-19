import json
import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path

APP_NAME = "MiniTask"
BG_KEY = "#ff00ff"  # Windows transparent-color key for the floating window
ACCENT = "#62d6a8"
TRACK = "#39414d"
TEXT = "#f4f6f8"
MUTED = "#aeb7c2"
PANEL = "#202630"
ROW = "#2a323e"


def data_file():
    """Store tasks in the user's AppData folder, not beside the program."""
    if os.name == "nt":
        folder = Path(os.environ.get("APPDATA", str(Path.home()))) / APP_NAME
    else:
        folder = Path.home() / f".{APP_NAME.lower()}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "tasks.json"


class MiniTask:
    def __init__(self):
        self.path = data_file()
        self.tasks = self.load_tasks()
        self.panel = None
        self.task_list_frame = None
        self.count_label = None
        self.progress_canvas = None
        self.widget_size = 78
        self.drag_origin = None

        self.floating = tk.Tk()
        self.floating.title(APP_NAME)
        self.floating.overrideredirect(True)
        self.floating.attributes("-topmost", True)
        self.floating.configure(bg=BG_KEY)

        # On Windows, hide the transparent-color pixels around the circular widget.
        if sys.platform == "win32":
            try:
                self.floating.wm_attributes("-transparentcolor", BG_KEY)
            except tk.TclError:
                pass

        screen_w = self.floating.winfo_screenwidth()
        screen_h = self.floating.winfo_screenheight()
        self.floating.geometry(f"{self.widget_size}x{self.widget_size}+{screen_w - 115}+{screen_h // 2}")

        self.canvas = tk.Canvas(
            self.floating, width=self.widget_size, height=self.widget_size,
            bg=BG_KEY, highlightthickness=0, bd=0
        )
        self.canvas.pack()
        self.draw_floating_button()
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)
        self.canvas.bind("<Button-3>", self.show_context_menu)

        self.menu = tk.Menu(self.floating, tearoff=0)
        self.menu.add_command(label="Open tasks", command=self.open_panel)
        self.menu.add_command(label="Add task", command=self.add_task_dialog)
        self.menu.add_separator()
        self.menu.add_command(label="Quit MiniTask", command=self.quit)

        self.floating.mainloop()

    def load_tasks(self):
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, list):
                return [
                    {"title": str(item.get("title", "Untitled task")),
                     "done": bool(item.get("done", False))}
                    for item in data if isinstance(item, dict)
                ]
        except (OSError, json.JSONDecodeError):
            pass
        return []

    def save_tasks(self):
        try:
            with self.path.open("w", encoding="utf-8") as file:
                json.dump(self.tasks, file, indent=2, ensure_ascii=False)
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not save tasks:\n{exc}")

    def draw_floating_button(self):
        c = self.canvas
        c.delete("all")
        size = self.widget_size
        pad = 7
        c.create_oval(pad, pad, size-pad, size-pad, fill=TRACK, outline="")
        total = len(self.tasks)
        done = sum(1 for task in self.tasks if task["done"])
        ratio = (done / total) if total else 0
        # Arc starts at 12 o'clock and grows clockwise.
        if total:
            c.create_arc(
                pad, pad, size-pad, size-pad, start=90, extent=-359.9 * ratio,
                style="arc", outline=ACCENT, width=5
            )
        else:
            c.create_oval(pad+2, pad+2, size-pad-2, size-pad-2,
                          outline=ACCENT, width=3)
        c.create_oval(15, 15, size-15, size-15, fill=PANEL, outline="")
        remaining = total - done
        c.create_text(size/2, size/2-3, text=str(remaining), fill=TEXT,
                      font=("Segoe UI", 19, "bold"))
        c.create_text(size/2, size/2+18, text="TASKS", fill=MUTED,
                      font=("Segoe UI", 7, "bold"))
        self.floating.update_idletasks()

    def start_drag(self, event):
        self.drag_origin = (event.x_root, event.y_root,
                            self.floating.winfo_x(), self.floating.winfo_y())

    def drag(self, event):
        if not self.drag_origin:
            return
        x0, y0, win_x, win_y = self.drag_origin
        dx, dy = event.x_root - x0, event.y_root - y0
        self.floating.geometry(f"+{win_x + dx}+{win_y + dy}")

    def end_drag(self, event):
        if not self.drag_origin:
            return
        x0, y0, _, _ = self.drag_origin
        moved = abs(event.x_root - x0) + abs(event.y_root - y0)
        self.drag_origin = None
        if moved < 5:
            self.open_panel()

    def show_context_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def open_panel(self):
        if self.panel and self.panel.winfo_exists():
            self.panel.deiconify()
            self.panel.lift()
            self.panel.focus_force()
            self.refresh_task_list()
            return

        self.panel = tk.Toplevel(self.floating)
        self.panel.title("MiniTask — My Tasks")
        self.panel.geometry("360x470")
        self.panel.minsize(320, 380)
        self.panel.configure(bg=PANEL)
        self.panel.attributes("-topmost", True)
        self.panel.protocol("WM_DELETE_WINDOW", self.panel.withdraw)

        header = tk.Frame(self.panel, bg=PANEL, padx=18, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="My Tasks", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        self.count_label = tk.Label(header, text="", bg=PANEL, fg=MUTED,
                                    font=("Segoe UI", 9))
        self.count_label.pack(anchor="w", pady=(3, 0))

        add_row = tk.Frame(self.panel, bg=PANEL, padx=18)
        add_row.pack(fill="x", pady=(0, 12))
        self.new_task_entry = tk.Entry(
            add_row, bg=ROW, fg=TEXT, insertbackground=TEXT,
            relief="flat", font=("Segoe UI", 10)
        )
        self.new_task_entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        self.new_task_entry.bind("<Return>", lambda _event: self.add_task_from_entry())
        tk.Button(add_row, text="＋", command=self.add_task_from_entry,
                  bg=ACCENT, fg="#14221c", activebackground=ACCENT,
                  relief="flat", font=("Segoe UI", 13, "bold"), width=3,
                  cursor="hand2").pack(side="right")

        self.task_list_frame = tk.Frame(self.panel, bg=PANEL, padx=18)
        self.task_list_frame.pack(fill="both", expand=True)

        footer = tk.Frame(self.panel, bg=PANEL, padx=18, pady=12)
        footer.pack(fill="x")
        tk.Button(footer, text="Clear completed", command=self.clear_completed,
                  bg=ROW, fg=TEXT, activebackground=ROW, activeforeground=TEXT,
                  relief="flat", padx=10, pady=7, cursor="hand2").pack(side="left")
        tk.Label(footer, text="Saved on this PC", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8)).pack(side="right")

        self.refresh_task_list()
        self.new_task_entry.focus_set()

    def add_task_dialog(self):
        title = simpledialog.askstring(APP_NAME, "What do you need to do?", parent=self.floating)
        if title and title.strip():
            self.tasks.append({"title": title.strip(), "done": False})
            self.save_tasks()
            self.draw_floating_button()
            self.refresh_task_list()

    def add_task_from_entry(self):
        if not self.panel or not self.panel.winfo_exists():
            return
        title = self.new_task_entry.get().strip()
        if not title:
            return
        self.tasks.append({"title": title, "done": False})
        self.new_task_entry.delete(0, "end")
        self.save_tasks()
        self.draw_floating_button()
        self.refresh_task_list()

    def toggle_task(self, index):
        self.tasks[index]["done"] = not self.tasks[index]["done"]
        self.save_tasks()
        self.draw_floating_button()
        self.refresh_task_list()

    def delete_task(self, index):
        del self.tasks[index]
        self.save_tasks()
        self.draw_floating_button()
        self.refresh_task_list()

    def clear_completed(self):
        self.tasks = [task for task in self.tasks if not task["done"]]
        self.save_tasks()
        self.draw_floating_button()
        self.refresh_task_list()

    def refresh_task_list(self):
        if not self.panel or not self.panel.winfo_exists() or not self.task_list_frame:
            return
        for child in self.task_list_frame.winfo_children():
            child.destroy()

        total = len(self.tasks)
        done = sum(1 for task in self.tasks if task["done"])
        if self.count_label and self.count_label.winfo_exists():
            self.count_label.config(text=f"{done} of {total} completed  •  {total-done} remaining")

        if not self.tasks:
            tk.Label(self.task_list_frame, text="No tasks yet.\nAdd one above to get started.",
                     bg=PANEL, fg=MUTED, justify="center",
                     font=("Segoe UI", 10)).pack(expand=True, pady=35)
            return

        for index, task in enumerate(self.tasks):
            row = tk.Frame(self.task_list_frame, bg=ROW, padx=8, pady=7)
            row.pack(fill="x", pady=4)
            checked = tk.BooleanVar(value=task["done"])
            cb = tk.Checkbutton(
                row, variable=checked, command=lambda i=index: self.toggle_task(i),
                bg=ROW, activebackground=ROW, selectcolor=PANEL,
                fg=ACCENT, activeforeground=ACCENT, relief="flat",
                highlightthickness=0
            )
            cb.pack(side="left")
            title_color = MUTED if task["done"] else TEXT
            title_font = ("Segoe UI", 9, "overstrike") if task["done"] else ("Segoe UI", 9)
            label = tk.Label(row, text=task["title"], bg=ROW, fg=title_color,
                             font=title_font, anchor="w", justify="left", wraplength=230)
            label.pack(side="left", fill="x", expand=True, padx=(4, 5))
            tk.Button(row, text="×", command=lambda i=index: self.delete_task(i),
                      bg=ROW, fg=MUTED, activebackground=ROW, activeforeground=TEXT,
                      relief="flat", font=("Segoe UI", 12), cursor="hand2").pack(side="right")

    def quit(self):
        if messagebox.askyesno(APP_NAME, "Close MiniTask? Your tasks are saved on this PC."):
            self.floating.destroy()


if __name__ == "__main__":
    MiniTask()
