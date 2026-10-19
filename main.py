import json, os, sys, tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog
APP='MiniTask'; KEY='#ff00ff'; GREEN='#63e6be'; TRACK='#465362'; TEXT='#f5f7fa'; MUTED='#aeb9c6'; PANEL='#1e2631'; ROW='#293442'
def appdir():
    p=Path(os.environ.get('APPDATA',str(Path.home()))) / ('MiniTask' if os.name=='nt' else '.minitask'); p.mkdir(parents=True,exist_ok=True); return p
def startup_path():
    a=os.environ.get('APPDATA')
    return Path(a)/'Microsoft/Windows/Start Menu/Programs/Startup/MiniTask Startup.vbs' if a else None
def frozen(): return bool(getattr(sys,'frozen',False))
def startup_command():
    if frozen(): return f'"{Path(sys.executable).resolve()}"'
    p=Path(sys.executable).with_name('pythonw.exe')
    if not p.exists(): p=Path(sys.executable)
    return f'"{p.resolve()}" "{Path(__file__).resolve()}"'
def set_startup(on):
    p=startup_path()
    if not p: raise RuntimeError('Windows Startup folder could not be found.')
    if on:
        p.parent.mkdir(parents=True,exist_ok=True); cmd=startup_command().replace('"','""')
        p.write_text('Set shell = CreateObject("WScript.Shell")\n' + f'shell.Run "{cmd}", 0, False\n',encoding='utf-8')
    elif p.exists(): p.unlink()
class MiniTask:
 def __init__(self):
    self.file=appdir()/'tasks.json'; self.tasks=self.load(); self.panel=None; self.frame=None; self.drag=None; self.moved=False; self.size=84
    self.root=tk.Tk(); self.root.title(APP); self.root.overrideredirect(True); self.root.attributes('-topmost',True); self.root.configure(bg=KEY); self.root.resizable(False,False)
    if sys.platform=='win32':
     try: self.root.wm_attributes('-transparentcolor',KEY)
     except tk.TclError: pass
    sw,sh=self.root.winfo_screenwidth(),self.root.winfo_screenheight(); self.root.geometry(f'{self.size}x{self.size}+{sw-125}+{max(25,sh//2)}')
    self.canvas=tk.Canvas(self.root,width=self.size,height=self.size,bg=KEY,highlightthickness=0,bd=0); self.canvas.pack(); self.draw()
    self.canvas.bind('<ButtonPress-1>',self.press); self.canvas.bind('<B1-Motion>',self.motion); self.canvas.bind('<ButtonRelease-1>',self.release); self.canvas.bind('<Button-3>',self.menu)
    self.m=tk.Menu(self.root,tearoff=0); self.m.add_command(label='Open tasks',command=self.open); self.m.add_command(label='Add task',command=self.add_dialog); self.m.add_separator(); self.start_var=tk.BooleanVar(value=bool(startup_path() and startup_path().exists())); self.m.add_checkbutton(label='Start with Windows',variable=self.start_var,command=self.start_toggle); self.m.add_separator(); self.m.add_command(label='Quit MiniTask',command=self.quit)
    self.root.mainloop()
 def load(self):
    try:
     d=json.loads(self.file.read_text(encoding='utf-8')); return [{'title':str(x.get('title','Untitled task')),'done':bool(x.get('done',False))} for x in d if isinstance(x,dict)] if isinstance(d,list) else []
    except (OSError,ValueError,TypeError): return []
 def save(self):
    try: self.file.write_text(json.dumps(self.tasks,indent=2,ensure_ascii=False),encoding='utf-8')
    except OSError as e: messagebox.showerror(APP,f'Could not save tasks:\n{e}')
 def draw(self):
    c=self.canvas;c.delete('all');s=self.size;pad=7;box=(pad,pad,s-pad,s-pad);total=len(self.tasks);done=sum(t['done'] for t in self.tasks);left=total-done
    c.create_oval(*box,fill='#293440',outline='')
    c.create_arc(*box,start=90,extent=-359.9,style='arc',outline=TRACK,width=5)
    if total and done: c.create_arc(*box,start=90,extent=-359.9*done/total,style='arc',outline=GREEN,width=5)
    if not total: c.create_oval(pad+3,pad+3,s-pad-3,s-pad-3,outline=GREEN,width=2)
    c.create_oval(16,16,s-16,s-16,fill=PANEL,outline='')
    c.create_text(s/2,s/2-5,text=str(left),fill=TEXT,font=('Segoe UI',19,'bold'))
    c.create_text(s/2,s/2+16,text='LEFT',fill=MUTED,font=('Segoe UI',7,'bold'))
    if total and left==0: c.create_oval(s-24,10,s-12,22,fill=GREEN,outline=PANEL,width=2)
 def press(self,e): self.drag=(e.x_root,e.y_root,self.root.winfo_x(),self.root.winfo_y());self.moved=False
 def motion(self,e):
    if not self.drag:return
    x0,y0,wx,wy=self.drag;dx=e.x_root-x0;dy=e.y_root-y0
    if abs(dx)+abs(dy)>5:self.moved=True
    if self.moved:
     sw,sh=self.root.winfo_screenwidth(),self.root.winfo_screenheight();x=max(0,min(sw-self.size,wx+dx));y=max(0,min(sh-self.size,wy+dy));self.root.geometry(f'+{x}+{y}')
 def release(self,e):
    was=self.moved;self.drag=None;self.moved=False
    if not was:self.open()
 def menu(self,e):
    self.start_var.set(bool(startup_path() and startup_path().exists()))
    try:self.m.tk_popup(e.x_root,e.y_root)
    finally:self.m.grab_release()
 def start_toggle(self):
    on=bool(self.start_var.get())
    try:set_startup(on)
    except Exception as e:self.start_var.set(not on);messagebox.showerror(APP,f'Could not change startup setting:\n{e}')
    self.start_var.set(bool(startup_path() and startup_path().exists()))
 def open(self):
    if self.panel and self.panel.winfo_exists():self.panel.deiconify();self.panel.lift();self.refresh();return
    self.panel=tk.Toplevel(self.root);self.panel.title('MiniTask — My Tasks');self.panel.geometry('380x500');self.panel.minsize(320,380);self.panel.configure(bg=PANEL);self.panel.attributes('-topmost',True);self.panel.protocol('WM_DELETE_WINDOW',self.panel.withdraw)
    head=tk.Frame(self.panel,bg=PANEL,padx=18,pady=16);head.pack(fill='x');tk.Label(head,text='My Tasks',bg=PANEL,fg=TEXT,font=('Segoe UI',18,'bold')).pack(anchor='w');self.count=tk.Label(head,text='',bg=PANEL,fg=MUTED,font=('Segoe UI',9));self.count.pack(anchor='w',pady=(3,0))
    add=tk.Frame(self.panel,bg=PANEL,padx=18);add.pack(fill='x',pady=(0,12));self.entry=tk.Entry(add,bg=ROW,fg=TEXT,insertbackground=TEXT,relief='flat',font=('Segoe UI',10));self.entry.pack(side='left',fill='x',expand=True,ipady=9,padx=(0,8));self.entry.bind('<Return>',lambda e:self.add_entry());tk.Button(add,text='+',command=self.add_entry,bg=GREEN,fg='#14221c',relief='flat',font=('Segoe UI',13,'bold'),width=3).pack(side='right')
    self.frame=tk.Frame(self.panel,bg=PANEL,padx=18);self.frame.pack(fill='both',expand=True);foot=tk.Frame(self.panel,bg=PANEL,padx=18,pady=12);foot.pack(fill='x');tk.Button(foot,text='Clear completed',command=self.clear,bg=ROW,fg=TEXT,relief='flat',padx=10,pady=7).pack(side='left');tk.Label(foot,text='Saved on this PC',bg=PANEL,fg=MUTED,font=('Segoe UI',8)).pack(side='right');self.refresh();self.entry.focus_set()
 def add_dialog(self):
    title=simpledialog.askstring(APP,'What do you need to do?',parent=self.root)
    if title and title.strip():self.tasks.append({'title':title.strip(),'done':False});self.save();self.draw();self.refresh()
 def add_entry(self):
    title=self.entry.get().strip()
    if title:self.tasks.append({'title':title,'done':False});self.entry.delete(0,'end');self.save();self.draw();self.refresh()
 def toggle(self,i):self.tasks[i]['done']=not self.tasks[i]['done'];self.save();self.draw();self.refresh()
 def delete(self,i):del self.tasks[i];self.save();self.draw();self.refresh()
 def clear(self):self.tasks=[t for t in self.tasks if not t['done']];self.save();self.draw();self.refresh()
 def refresh(self):
    if not self.panel or not self.panel.winfo_exists():return
    for w in self.frame.winfo_children():w.destroy()
    total=len(self.tasks);done=sum(t['done'] for t in self.tasks);self.count.config(text=f'{done} of {total} completed  •  {total-done} remaining')
    if not total:tk.Label(self.frame,text='No tasks yet.\nAdd one above to get started.',bg=PANEL,fg=MUTED,justify='center').pack(expand=True,pady=35);return
    for i,t in enumerate(self.tasks):
     row=tk.Frame(self.frame,bg=ROW,padx=8,pady=7);row.pack(fill='x',pady=4);v=tk.BooleanVar(value=t['done']);tk.Checkbutton(row,variable=v,command=lambda j=i:self.toggle(j),bg=ROW,activebackground=ROW,selectcolor=PANEL,fg=GREEN,relief='flat',highlightthickness=0).pack(side='left');color=MUTED if t['done'] else TEXT;font=('Segoe UI',9,'overstrike') if t['done'] else ('Segoe UI',9);tk.Label(row,text=t['title'],bg=ROW,fg=color,font=font,anchor='w',justify='left',wraplength=240).pack(side='left',fill='x',expand=True,padx=(4,5));tk.Button(row,text='×',command=lambda j=i:self.delete(j),bg=ROW,fg=MUTED,relief='flat',font=('Segoe UI',12)).pack(side='right')
 def quit(self):
    if messagebox.askyesno(APP,'Close MiniTask? Your tasks are saved on this PC.'):self.root.destroy()
if __name__=='__main__':MiniTask()
