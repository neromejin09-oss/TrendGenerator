import os
import shutil
import sys
import subprocess
import platform
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Project Directory Configuration
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
CONVERT_DIR = BASE_DIR / "convert"
EXTRACT_DIR = BASE_DIR / "extract"
BOARD_DIR = BASE_DIR / "board"

# Automatically create required directories
for folder in [INPUT_DIR, CONVERT_DIR, EXTRACT_DIR, BOARD_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


class MainAppController:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Automation Pipeline Control Panel")
        self.root.geometry("680x660")
        self.root.resizable(True, True)

        # Thread and process interruption control
        self.stop_event = threading.Event()
        self.current_process = None
        self.process_lock = threading.Lock()

        self.setup_ui()

    def setup_ui(self):
        # 1. Header Section
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill=tk.X)

        ttk.Label(
            header_frame, 
            text="📁 Data Automation Processing Pipeline", 
            font=("Segoe UI", 14, "bold")
        ).pack(anchor=tk.W)

        ttk.Label(
            header_frame, 
            text="Selected files will automatically route (.csv ➔ input | .xlsx ➔ convert). Run steps individually or execute full pipeline.",
            font=("Segoe UI", 9),
            foreground="gray"
        ).pack(anchor=tk.W, pady=(2, 0))

        # 2. File Import & Display Section
        file_frame = ttk.LabelFrame(self.root, text=" Import Files ", padding=10)
        file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        btn_bar = ttk.Frame(file_frame)
        btn_bar.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(btn_bar, text="+ Add Files (CSV / XLSX)", command=self.add_files).pack(side=tk.LEFT)
        ttk.Button(btn_bar, text="Clear List", command=self.clear_list).pack(side=tk.RIGHT)

        list_scroll = ttk.Scrollbar(file_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            file_frame, 
            yscrollcommand=list_scroll.set, 
            selectmode=tk.EXTENDED,
            font=("Consolas", 9)
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.file_listbox.yview)

        # 3. Actions Section
        action_frame = ttk.LabelFrame(self.root, text=" Execution Options ", padding=10)
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        action_frame.columnconfigure(2, weight=1)

        # Row 1: Single Step Buttons
        self.btn_step1 = ttk.Button(
            action_frame, 
            text="1. Run convert_data\n(CSV to XLSX)", 
            command=lambda: self.start_single_script_thread("convert_data.py", CONVERT_DIR)
        )
        self.btn_step1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_step2 = ttk.Button(
            action_frame, 
            text="2. Run extract_clean_data\n(Extract & Clean Data)", 
            command=lambda: self.start_single_script_thread("extract_clean_data.py", EXTRACT_DIR)
        )
        self.btn_step2.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.btn_step3 = ttk.Button(
            action_frame, 
            text="3. Run run_dashboard\n(Generate Dashboard)", 
            command=lambda: self.start_single_script_thread("run_dashboard.py", BOARD_DIR)
        )
        self.btn_step3.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Row 2: Pipeline & Interruption Control
        btn_pipeline_frame = ttk.Frame(action_frame)
        btn_pipeline_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=(10, 5), sticky="ew")
        btn_pipeline_frame.columnconfigure(0, weight=3)
        btn_pipeline_frame.columnconfigure(1, weight=1)

        self.btn_run_all = ttk.Button(
            btn_pipeline_frame, 
            text="🚀 Run Full Pipeline (All Steps + Open Dashboard Folder)", 
            command=self.start_pipeline_thread
        )
        self.btn_run_all.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_stop = ttk.Button(
            btn_pipeline_frame,
            text="⏹️ Stop Execution",
            state=tk.DISABLED,
            command=self.stop_execution
        )
        self.btn_stop.grid(row=0, column=1, sticky="ew")

        # 4. Progress & Status Section
        progress_frame = ttk.Frame(self.root, padding=(10, 5, 10, 10))
        progress_frame.pack(fill=tk.X)

        self.status_label = ttk.Label(progress_frame, text="Status: Ready to execute...", font=("Segoe UI", 9))
        self.status_label.pack(anchor=tk.W, pady=(0, 2))

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill=tk.X)

    def set_buttons_state(self, running: bool):
        state = tk.DISABLED if running else tk.NORMAL
        stop_state = tk.NORMAL if running else tk.DISABLED

        self.btn_step1.config(state=state)
        self.btn_step2.config(state=state)
        self.btn_step3.config(state=state)
        self.btn_run_all.config(state=state)
        self.btn_stop.config(state=stop_state)

    def stop_execution(self):
        self.stop_event.set()
        with self.process_lock:
            if self.current_process and self.current_process.poll() is None:
                try:
                    self.current_process.terminate()
                except Exception as e:
                    print(f"Process termination exception: {e}")
        self.update_progress(0, "⏹️ Interrupting execution...")

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Data Files",
            filetypes=[("Supported Files", "*.csv;*.xlsx"), ("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")]
        )
        if not files:
            return

        for file_path in files:
            path = Path(file_path)
            ext = path.suffix.lower()
            try:
                if ext == ".csv":
                    target_dir = INPUT_DIR
                    label = "[CSV ➔ input]"
                elif ext == ".xlsx":
                    target_dir = CONVERT_DIR
                    label = "[XLSX ➔ convert]"
                else:
                    continue

                shutil.copy2(path, target_dir / path.name)
                self.file_listbox.insert(tk.END, f"{label} {path.name}")
            except Exception as e:
                messagebox.showerror("File Copy Error", f"Failed to import {path.name}: {e}")

    def clear_list(self):
        self.file_listbox.delete(0, tk.END)

    def get_script_path(self, script_name):
        script_path = BASE_DIR / script_name
        if not script_path.exists():
            alt_path = BASE_DIR / script_name.replace(".py", ".txt")
            if alt_path.exists():
                script_path = alt_path
        return script_path if script_path.exists() else None

    def open_folder(self, target_dir):
        try:
            if not target_dir.exists():
                target_dir.mkdir(parents=True, exist_ok=True)
            
            system_name = platform.system()
            if system_name == "Windows":
                os.startfile(target_dir)
            elif system_name == "Darwin":
                subprocess.Popen(["open", str(target_dir)])
            else:
                subprocess.Popen(["xdg-open", str(target_dir)])
        except Exception as e:
            messagebox.showerror("Folder Error", f"Unable to open directory:\n{e}")

    def update_progress(self, value, text):
        self.progress_bar['value'] = value
        self.status_label.config(text=text)

    def _execute_subprocess(self, script_path):
        with self.process_lock:
            self.current_process = subprocess.Popen([sys.executable, str(script_path)], cwd=str(BASE_DIR))
        
        while True:
            if self.stop_event.is_set():
                with self.process_lock:
                    if self.current_process and self.current_process.poll() is None:
                        self.current_process.terminate()
                return -1
            
            retcode = self.current_process.poll()
            if retcode is not None:
                return retcode
            self.root.after(100)

    def start_single_script_thread(self, script_name, output_dir):
        self.stop_event.clear()
        self.set_buttons_state(True)
        thread = threading.Thread(target=self._run_single_script_worker, args=(script_name, output_dir), daemon=True)
        thread.start()

    def _run_single_script_worker(self, script_name, output_dir):
        script_path = self.get_script_path(script_name)
        if not script_path:
            self.root.after(0, lambda: messagebox.showerror("Missing Script", f"Script file not found: {script_name}"))
            self.root.after(0, lambda: self.set_buttons_state(False))
            return

        self.root.after(0, self.update_progress, 30, f"⏳ Executing {script_name}...")

        try:
            retcode = self._execute_subprocess(script_path)
            if self.stop_event.is_set() or retcode == -1:
                self.root.after(0, self.update_progress, 0, "⏹️ Execution interrupted by user.")
            elif retcode == 0:
                self.root.after(0, self.update_progress, 100, f"✅ {script_name} completed. Opening folder...")
                self.root.after(0, lambda: self.open_folder(output_dir))
            else:
                self.root.after(0, self.update_progress, 0, f"❌ {script_name} execution failed.")
                self.root.after(0, lambda: messagebox.showerror("Execution Error", f"Script {script_name} encountered an error."))
        except Exception as e:
            self.root.after(0, self.update_progress, 0, f"❌ Error: {script_name}")
            self.root.after(0, lambda: messagebox.showerror("Execution Error", f"Failed to run script {script_name}:\n{e}"))
        finally:
            self.root.after(0, lambda: self.set_buttons_state(False))

    def start_pipeline_thread(self):
        self.stop_event.clear()
        self.set_buttons_state(True)
        thread = threading.Thread(target=self._run_all_pipeline_worker, daemon=True)
        thread.start()

    def _run_all_pipeline_worker(self):
        scripts = [
            ("convert_data.py", "Step 1/3: Converting CSV to XLSX format..."),
            ("extract_clean_data.py", "Step 2/3: Extracting and cleaning data..."),
            ("run_dashboard.py", "Step 3/3: Generating Excel dashboard...")
        ]

        total_steps = len(scripts)

        for idx, (script_name, status_msg) in enumerate(scripts):
            if self.stop_event.is_set():
                break

            progress_val = int((idx / total_steps) * 100)
            self.root.after(0, self.update_progress, progress_val, f"⏳ {status_msg}")

            script_path = self.get_script_path(script_name)
            if not script_path:
                self.root.after(0, self.update_progress, 0, "❌ Pipeline stopped: Missing file")
                self.root.after(0, lambda name=script_name: messagebox.showerror(
                    "Error", f"Required script not found: {name}\nPipeline terminated."
                ))
                self.root.after(0, lambda: self.set_buttons_state(False))
                return

            retcode = self._execute_subprocess(script_path)

            if self.stop_event.is_set() or retcode == -1:
                break

            if retcode != 0:
                self.root.after(0, self.update_progress, 0, "❌ Pipeline stopped: Script error")
                self.root.after(0, lambda name=script_name: messagebox.showerror(
                    "Pipeline Error", f"Script [{name}] returned an error code. Aborting."
                ))
                self.root.after(0, lambda: self.set_buttons_state(False))
                return

        if self.stop_event.is_set():
            self.root.after(0, self.update_progress, 0, "⏹️ Pipeline interrupted by user.")
        else:
            self.root.after(0, self.update_progress, 100, "✅ Pipeline completed! Opening dashboard directory...")
            self.root.after(0, lambda: self.open_folder(BOARD_DIR))

        self.root.after(0, lambda: self.set_buttons_state(False))


if __name__ == "__main__":
    root = tk.Tk()
    app = MainAppController(root)
    root.mainloop()