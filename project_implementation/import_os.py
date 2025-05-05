import os
import sys
import subprocess
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# -------------------- STYLED & UPGRADED FILE TYPE PRIORITIES --------------------
file_type_priority = {
    '.pdf': 1,             # High Priority - Documents
    '.doc': 2, '.docx': 2, # Medium-High Priority - Documents
    '.xls': 3, '.xlsx': 3, # Medium Priority - Spreadsheets
    '.txt': 4,             # Medium-Low Priority - Text Files
    '.odt': 5,             # Low Priority - OpenOffice Documents
    '.ods': 6,             # Low Priority - OpenOffice Spreadsheets
    '.mp4': 7,             # Very Low Priority - Videos
    '.avi': 8,             # Very Low Priority - Videos
    '.zip': 9, '.rar': 9   # Very Low Priority - Archives
}

current_directory = None
burst_times_cache = {}

# -------------------- SCHEDULING ALGORITHMS (No changes needed, already efficient) --------------------
def fifo(processes):
    order = []
    time = 0
    for process in processes:
        time += process[1]
        order.append((process[0], time))
    return order

def sjf(processes):
    processes_sorted = sorted(processes, key=lambda x: x[1])
    order = []
    time = 0
    for process in processes_sorted:
        time += process[1]
        order.append((process[0], time))
    return order

def priority_schedule(processes):
    def get_priority(filename):
        ext = os.path.splitext(filename)[1].lower()
        return file_type_priority.get(ext, 10)
    processes_sorted = sorted(processes, key=lambda x: (get_priority(x[0]), x[0]))
    order = []
    time = 0
    for process in processes_sorted:
        time += process[1]
        order.append((process[0], time))
    return order

def get_file_processes():
    global burst_times_cache
    if not current_directory or not os.path.isdir(current_directory):
        messagebox.showerror("Error", "No valid directory selected.")
        return []

    files = os.listdir(current_directory)
    files.sort(key=lambda x: os.path.getctime(os.path.join(current_directory, x)))
    processes = []

    for file in files:
        if file not in burst_times_cache:
            burst_times_cache[file] = random.randint(1, 10)
        burst_time = burst_times_cache[file]
        processes.append((file, burst_time))

    return processes

def display_schedule(order):
    result = "Process Completion Order:\n\n"
    start_time = 0
    for process, finish_time in order:
        burst_time = finish_time - start_time
        result += f"{process}: Burst Time = {burst_time}, Finish Time = {finish_time}\n"
        start_time = finish_time
    messagebox.showinfo("Scheduling Result", result)

def draw_gantt_chart(order):
    fig, gnt = plt.subplots(figsize=(8, 4)) # Improved figure size
    gnt.set_title("Gantt Chart", fontsize=14, fontweight='bold') # Stylish title
    gnt.set_xlabel("Time", fontsize=12)
    gnt.set_ylabel("Processes", fontsize=12)
    gnt.set_yticks([10 * i for i in range(1, len(order) + 1)])
    gnt.set_yticklabels([p[0] for p in order], fontsize=10)
    gnt.grid(True, linestyle='--', alpha=0.7) # Improved grid

    start_time = 0
    colors = plt.cm.get_cmap('viridis', len(order)) # More visually appealing colormap
    for i, (process, finish_time) in enumerate(order):
        burst_time = finish_time - start_time
        gnt.broken_barh([(start_time, burst_time)], (10 * (i + 1) - 3, 6), # Adjusted bar height and spacing
                        facecolors=colors(i), edgecolor='black', linewidth=0.5) # Added edgecolor
        start_time = finish_time

    plt.tight_layout()
    plt.show()

def run_fifo():
    processes = get_file_processes()
    if not processes:
        return
    order = fifo(processes)
    display_schedule(order)
    draw_gantt_chart(order)

def run_sjf():
    processes = get_file_processes()
    if not processes:
        return
    order = sjf(processes)
    display_schedule(order)
    draw_gantt_chart(order)

def run_priority():
    processes = get_file_processes()
    if not processes:
        return
    order = priority_schedule(processes)
    display_schedule(order)
    draw_gantt_chart(order)

# -------------------- STYLED & UPGRADED FILE MANAGEMENT FUNCTIONS --------------------
def update_file_list():
    file_list.delete(0, tk.END)
    if current_directory and os.path.isdir(current_directory):
        files = os.listdir(current_directory)
        files.sort() # Sort files alphabetically for better presentation
        for file in files:
            file_list.insert(tk.END, file)

def list_files():
    global current_directory, burst_times_cache
    directory = filedialog.askdirectory(title="Select Directory") # More descriptive title
    if directory:
        current_directory = directory
        burst_times_cache = {}
        update_file_list()

def create_file():
    global current_directory
    if not current_directory:
        messagebox.showerror("Error", "Please select a directory first using 'Browse Directory'.") # Updated text
        return
    file_path = filedialog.asksaveasfilename(
        initialdir=current_directory,
        defaultextension=".txt",
        title="Create New File", # More descriptive title
        filetypes=[("Text files", ".txt"), ("All files", ".*")]
    )
    if file_path:
        try:
            with open(file_path, 'w') as file:
                file.write("")
            messagebox.showinfo("Success", f"File '{os.path.basename(file_path)}' created successfully") # More informative message
            update_file_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not create file: {str(e)}") # More informative error

def delete_file():
    global current_directory
    if not current_directory:
        messagebox.showerror("Error", "Please select a directory first using 'Browse Directory'.") # Updated text
        return
    file_path = filedialog.askopenfilename(initialdir=current_directory, title="Select File to Delete") # More descriptive title
    if file_path and os.path.exists(file_path):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{os.path.basename(file_path)}'?") # More specific confirmation
        if confirm:
            try:
                os.remove(file_path)
                messagebox.showinfo("Success", f"File '{os.path.basename(file_path)}' deleted successfully") # More informative message
                update_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file: {str(e)}") # More informative error

def rename_file():
    global current_directory
    if not current_directory:
        messagebox.showerror("Error", "Please select a directory first using 'Browse Directory'.") # Updated text
        return
    old_path = filedialog.askopenfilename(initialdir=current_directory, title="Select File to Rename") # More descriptive title
    if old_path:
        new_path = filedialog.asksaveasfilename(
            initialdir=current_directory,
            initialfile=os.path.basename(old_path), # Suggest current filename
            title="Rename File As", # More descriptive title
        )
        if new_path:
            try:
                os.rename(old_path, new_path)
                messagebox.showinfo("Success", f"File '{os.path.basename(old_path)}' renamed to '{os.path.basename(new_path)}' successfully") # More informative message
                update_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename file: {str(e)}") # More informative error

def play_video():
    global current_directory
    selected = file_list.curselection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a video file from the list to play.") # More specific warning
        return

    filename = file_list.get(selected[0])
    filepath = os.path.join(current_directory, filename)

    if not os.path.isfile(filepath):
        messagebox.showerror("Error", "Selected file not found.") # More specific error
        return

    video_extensions = ('.mp4', '.avi', '.mkv', '.mov', '.wmv') # Added more common extensions
    if not filename.lower().endswith(video_extensions):
        messagebox.showerror("Unsupported Format", f"File '{filename}' is not a supported video format ({', '.join(video_extensions)}).") # More informative error
        return

    try:
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', filepath))
    except Exception as e:
        messagebox.showerror("Error", f"Could not open '{filename}': {str(e)}") # More informative error

# -------------------- STYLED & UPGRADED GUI SETUP --------------------
root = tk.Tk()
root.title("Advanced Process Scheduler & File Manager") # More sophisticated title
root.geometry("950x650") # Slightly larger default size
root.configure(bg="#e0f2f7") # Modern, light blue background

style = ttk.Style()
style.theme_use('clam') # Modern theme


style.configure("TButton",
                font=("Segoe UI", 10, 'bold'),
                padding=8,
                relief='raised',
                borderwidth=2,
                background="#81d4fa", # Light blue button
                foreground="black")
style.map("TButton",
          background=[('active', '#4fc3f7'), ('disabled', '#b3e5fc')])


style.configure("TNotebook", tabposition='n', background="#e0f2f7")
style.configure("TNotebook.Tab",
                font=("Segoe UI", 11),
                padding=(15, 7),
                background="#b3e5fc",
                foreground="black")
style.map("TNotebook.Tab",
          background=[('selected', '#81d4fa')])

# Improved label style
style.configure("TLabel", background="#e0f2f7", font=("Segoe UI", 12))
style.configure("TEntry", font=("Segoe UI", 11))
style.configure("TListbox", font=("Segoe UI", 10))

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=15, pady=15)

# --- STYLED & UPGRADED FILE MANAGER TAB ---
file_tab = ttk.Frame(notebook)
notebook.add(file_tab, text=" 📂 File Manager") # Added icon

file_btn_frame = ttk.Frame(file_tab)
file_btn_frame.pack(pady=20, padx=20, fill='x') # Centered buttons

file_buttons_config = [
    ("Browse Directory", list_files), # More intuitive name
    ("Create New File", create_file), # More intuitive name
    ("Delete Selected File", delete_file), # More specific
    ("Rename Selected File", rename_file), # More specific
    ("Play Video File", play_video) # More specific
]

for i, (text, cmd) in enumerate(file_buttons_config):
    ttk.Button(file_btn_frame, text=text, command=cmd).pack(side='left', padx=5, fill='x', expand=True) # Evenly spaced buttons

file_list_frame = ttk.Frame(file_tab)
file_list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20)) # Padding

scrollbar = ttk.Scrollbar(file_list_frame, orient=tk.VERTICAL)
file_list = tk.Listbox(file_list_frame, height=15, yscrollcommand=scrollbar.set, font=("Segoe UI", 10), selectbackground="#4fc3f7", selectforeground="black") # Improved listbox
scrollbar.config(command=file_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


schedule_tab = ttk.Frame(notebook)
notebook.add(schedule_tab, text=" ⏱️ Scheduling Algorithms") # Added icon

sched_label = ttk.Label(schedule_tab, text="Select a Scheduling Algorithm to Simulate:", font=("Segoe UI", 12, 'bold')) # Improved label
sched_label.pack(pady=25)

sched_btn_frame = ttk.Frame(schedule_tab)
sched_btn_frame.pack(pady=10)

ttk.Button(sched_btn_frame, text="FIFO (First-In, First-Out)", command=run_fifo).pack(pady=8, fill='x', padx=20) # More descriptive text
ttk.Button(sched_btn_frame, text="SJF (Shortest Job First)", command=run_sjf).pack(pady=8, fill='x', padx=20) # More descriptive text
ttk.Button(sched_btn_frame, text="Priority Scheduling", command=run_priority).pack(pady=8, fill='x', padx=20) # More descriptive text

root.mainloop()