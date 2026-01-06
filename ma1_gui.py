# ma1_gui.py
# Dark-mode, single-window GUI for MA1 Auto-Grader pipeline (ZIP → grade → charts → master summary)
# Uses workspace paths (Documents/MA1_Autograder/...) when utilities/paths.py is present.

import json
import os
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import sys

from utilities.bootstrap_assets import bootstrap_assets

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
bootstrap_assets(PROJECT_ROOT)


from run_pipeline import run_pipeline
from writers.import_zip_to_student_groups import import_zip_to_student_groups

# Workspace helpers (Documents/MA1_Autograder/...)
try:
    from utilities.paths import workspace_root
except Exception:
    workspace_root = None

CONFIG_FILE = "gui_config.json"

# -----------------------------
# Dark Mode Theme (Tesla-ish)
# -----------------------------
DARK_BG = "#0b0f14"       # deep blue-black
DARK_PANEL = "#111824"    # card/panel bg
DARK_FIELD = "#0f1520"    # entry/log bg
DARK_TEXT = "#e6e8eb"     # main text
DARK_MUTED = "#aab2bd"    # secondary text
ACCENT = "#d71921"        # red accent
GOOD = "#22c55e"
WARN = "#f59e0b"
BAD = "#ef4444"


def apply_dark_theme(root: tk.Tk):
    root.configure(bg=DARK_BG)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(".", background=DARK_BG, foreground=DARK_TEXT, font=("Segoe UI", 10))
    style.configure("TFrame", background=DARK_BG)
    style.configure("Card.TFrame", background=DARK_PANEL)

    style.configure("TLabel", background=DARK_BG, foreground=DARK_TEXT)
    style.configure("Muted.TLabel", background=DARK_BG, foreground=DARK_MUTED)
    style.configure("Header.TLabel", background=DARK_BG, foreground=DARK_TEXT, font=("Segoe UI", 18, "bold"))
    style.configure("SubHeader.TLabel", background=DARK_BG, foreground=DARK_MUTED, font=("Segoe UI", 10))

    # Badge styles (status pill)
    style.configure("BadgeIdle.TLabel", background=DARK_PANEL, foreground=DARK_MUTED, padding=(10, 4))
    style.configure("BadgeRun.TLabel",  background=DARK_PANEL, foreground=WARN,       padding=(10, 4))
    style.configure("BadgeDone.TLabel", background=DARK_PANEL, foreground=GOOD,       padding=(10, 4))
    style.configure("BadgeErr.TLabel",  background=DARK_PANEL, foreground=BAD,        padding=(10, 4))

    # Entry
    style.configure(
        "TEntry",
        fieldbackground=DARK_FIELD,
        foreground=DARK_TEXT,
        insertcolor=DARK_TEXT,
        bordercolor=DARK_PANEL,
        lightcolor=DARK_PANEL,
        darkcolor=DARK_PANEL
    )

    # Buttons
    style.configure(
        "TButton",
        padding=(12, 8),
        background=DARK_PANEL,
        foreground=DARK_TEXT,
        borderwidth=0,
        focusthickness=0
    )
    style.map(
        "TButton",
        background=[("active", "#192235"), ("disabled", "#141a23")],
        foreground=[("disabled", "#6b7280")]
    )

    style.configure(
        "Accent.TButton",
        padding=(12, 8),
        background=ACCENT,
        foreground="#ffffff",
        borderwidth=0,
        focusthickness=0
    )
    style.map(
        "Accent.TButton",
        background=[("active", "#b6141a"), ("disabled", "#5a0b0e")],
        foreground=[("disabled", "#d1d5db")]
    )

    style.configure("Slim.TButton", padding=(10, 6))

    # Progressbar
    style.configure("TProgressbar", troughcolor=DARK_PANEL, background=ACCENT, bordercolor=DARK_PANEL)


# -----------------------------
# Config helpers
# -----------------------------
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


# -----------------------------
# Logging redirect
# -----------------------------
class TextRedirector:
    def __init__(self, q: queue.Queue):
        self.q = q

    def write(self, msg: str):
        if msg:
            self.q.put(msg)

    def flush(self):
        pass


def open_folder(path: str):
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        messagebox.showwarning("Not found", f"Folder not found:\n{path}")
        return

    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore
    elif sys.platform == "darwin":
        subprocess.run(["open", path], check=False)
    else:
        subprocess.run(["xdg-open", path], check=False)


def copy_to_clipboard(root: tk.Tk, text: str):
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
    except Exception:
        pass


def get_workspace_root_fallback() -> str:
    """
    If utilities.paths.workspace_root() exists, use it.
    Otherwise, fallback to current working directory (dev mode).
    """
    if workspace_root is not None:
        try:
            return workspace_root()
        except Exception:
            pass
    return os.getcwd()


def ws_join(*parts) -> str:
    return os.path.join(get_workspace_root_fallback(), *parts)


# -----------------------------
# App
# -----------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("MA1 Auto-Grader (Internal)")
        self.geometry("1020x720")
        self.minsize(920, 640)

        apply_dark_theme(self)

        self.cfg = load_config()
        self.log_queue: queue.Queue = queue.Queue()
        self.worker_thread = None

        self.last_graded_path = None
        self.last_course_label = None

        self._build_ui()
        self.after(100, self._poll_logs)

    # ---------- UI helpers ----------
    def _set_badge(self, mode: str, text: str):
        style = {
            "idle": "BadgeIdle.TLabel",
            "run": "BadgeRun.TLabel",
            "done": "BadgeDone.TLabel",
            "err": "BadgeErr.TLabel",
        }.get(mode, "BadgeIdle.TLabel")
        self.badge_lbl.configure(text=text, style=style)

    def _ui_safe(self, fn, *args, **kwargs):
        self.after(0, lambda: fn(*args, **kwargs))

    # ---------- Build UI ----------
    def _build_ui(self):
        pad = 14

        header = ttk.Label(self, text="MA1 Auto-Grader", style="Header.TLabel")
        header.pack(anchor="w", padx=pad, pady=(pad, 2))

        sub = ttk.Label(
            self,
            text="ZIP → workspace → grade → charts → instructor master (summary)",
            style="SubHeader.TLabel"
        )
        sub.pack(anchor="w", padx=pad, pady=(0, pad))

        # Status strip
        status_strip = ttk.Frame(self, style="Card.TFrame", padding=12)
        status_strip.pack(fill="x", padx=pad, pady=(0, pad))

        ttk.Label(status_strip, text="Status:", style="Muted.TLabel").pack(side="left")
        self.badge_lbl = ttk.Label(status_strip, text="Idle", style="BadgeIdle.TLabel")
        self.badge_lbl.pack(side="left", padx=(10, 0))

        self.step_var = tk.StringVar(value="Waiting for input…")
        ttk.Label(status_strip, textvariable=self.step_var, style="Muted.TLabel").pack(side="left", padx=(14, 0))

        self.progress = ttk.Progressbar(status_strip, mode="indeterminate", length=240)
        self.progress.pack(side="right")

        # Input card
        frame = ttk.Frame(self, style="Card.TFrame", padding=12)
        frame.pack(fill="x", padx=pad, pady=(0, pad))

        self.course_var = tk.StringVar(value=self.cfg.get("course_label", "MAT-144-501"))
        self.zip_var = tk.StringVar(value=self.cfg.get("zip_path", ""))

        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Course Label", style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.course_var, width=25).grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Student Zip File", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(frame, textvariable=self.zip_var).grid(row=1, column=1, sticky="ew", pady=(10, 0))

        ttk.Button(frame, text="Browse…", style="Slim.TButton", command=self.on_browse_zip)\
            .grid(row=1, column=2, sticky="e", padx=(10, 0), pady=(10, 0))

        ttk.Button(frame, text="Import Zip", style="Slim.TButton", command=self.on_import_zip)\
            .grid(row=1, column=3, sticky="e", padx=(10, 0), pady=(10, 0))

        # Action buttons
        btn_frame = ttk.Frame(self, style="Card.TFrame", padding=12)
        btn_frame.pack(fill="x", padx=pad, pady=(0, pad))

        self.run_btn = ttk.Button(btn_frame, text="Run Full Pipeline", style="Accent.TButton", command=self.on_run)
        self.run_btn.pack(side="left")

        self.open_out_btn = ttk.Button(btn_frame, text="Open Output Folder", command=self.on_open_output, state="disabled")
        self.open_out_btn.pack(side="left", padx=(10, 0))

        self.open_groups_btn = ttk.Button(btn_frame, text="Open Student Groups", command=self.on_open_groups, state="disabled")
        self.open_groups_btn.pack(side="left", padx=(10, 0))

        self.open_ws_btn = ttk.Button(btn_frame, text="Open Workspace", command=self.on_open_workspace)
        self.open_ws_btn.pack(side="left", padx=(10, 0))

        self.copy_path_btn = ttk.Button(btn_frame, text="Copy Output Path", command=self.on_copy_output, state="disabled")
        self.copy_path_btn.pack(side="left", padx=(10, 0))

        self.clear_btn = ttk.Button(btn_frame, text="Clear Log", command=self.on_clear)
        self.clear_btn.pack(side="right")

        ttk.Label(self, text="Log Output", style="Muted.TLabel").pack(anchor="w", padx=pad, pady=(0, 6))

        self.log_text = tk.Text(
            self,
            wrap="word",
            bg=DARK_FIELD,
            fg=DARK_TEXT,
            insertbackground=DARK_TEXT,
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=DARK_PANEL,
            highlightcolor=DARK_PANEL
        )
        self.log_text.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        self._append_log("Ready.\n")
        self._set_badge("idle", "Idle")
        self.progress.stop()

    # ---------- Log plumbing ----------
    def _append_log(self, msg: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _poll_logs(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self._append_log(msg)
        except queue.Empty:
            pass
        self.after(100, self._poll_logs)

    # ---------- Button handlers ----------
    def on_clear(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def on_open_output(self):
        if self.last_graded_path:
            open_folder(self.last_graded_path)

    def on_open_groups(self):
        # ✅ FIX: open from WORKSPACE, not project root
        if not self.last_course_label:
            messagebox.showinfo("Student Groups", "Run Import or Pipeline first.")
            return

        groups_path = ws_join("student_groups", self.last_course_label)
        open_folder(groups_path)

    def on_open_workspace(self):
        open_folder(get_workspace_root_fallback())

    def on_copy_output(self):
        if self.last_graded_path:
            copy_to_clipboard(self, self.last_graded_path)
            messagebox.showinfo("Copied", "Output path copied to clipboard.")

    def on_browse_zip(self):
        path = filedialog.askopenfilename(
            title="Select Student Zip File",
            filetypes=[("Zip files", "*.zip"), ("All files", "*.*")]
        )
        if path:
            self.zip_var.set(path)
            self.cfg["zip_path"] = path
            save_config(self.cfg)

    def on_import_zip(self):
        course_label = self.course_var.get().strip()
        zip_path = self.zip_var.get().strip()

        if not course_label:
            messagebox.showerror("Missing", "Please enter a course label first.")
            return
        if not zip_path or not os.path.exists(zip_path):
            messagebox.showerror("Missing", "Please select a valid zip file.")
            return

        try:
            self._set_badge("run", "Importing…")
            self.step_var.set("Extracting zip into workspace student_groups/…")
            self.progress.start(10)

            dest = import_zip_to_student_groups(zip_path, course_label)

            self.last_course_label = course_label
            self.open_groups_btn.configure(state="normal")

            self._append_log(f"\n✅ Imported zip into:\n{dest}\n")
            self.step_var.set("Import complete.")
            self._set_badge("done", "Imported ✅")

        except Exception as e:
            self._set_badge("err", "Import failed ❌")
            self.step_var.set("Import failed.")
            messagebox.showerror("Import failed", str(e))
        finally:
            self.progress.stop()

    def on_run(self):
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo("Running", "A run is already in progress.")
            return

        course_label = self.course_var.get().strip()
        zip_path = self.zip_var.get().strip()

        if not course_label:
            messagebox.showerror("Missing", "Please enter a course label.")
            return
        if not zip_path or not os.path.exists(zip_path):
            messagebox.showerror("Missing", "Please select a valid zip file.")
            return

        # Save config
        self.cfg["course_label"] = course_label
        self.cfg["zip_path"] = zip_path
        save_config(self.cfg)

        self.last_course_label = course_label
        self.open_groups_btn.configure(state="normal")

        # UI lock
        self._set_badge("run", "Running…")
        self.step_var.set("Running full pipeline…")
        self.run_btn.configure(state="disabled")
        self.open_out_btn.configure(state="disabled")
        self.copy_path_btn.configure(state="disabled")
        self.progress.start(10)

        # Redirect stdout/stderr to log
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        sys.stdout = TextRedirector(self.log_queue)
        sys.stderr = TextRedirector(self.log_queue)

        def worker():
            try:
                print("\n=== Starting MA1 Pipeline ===\n")
                graded_path = run_pipeline(zip_path, course_label)

                # run_pipeline should return a string path; guard just in case
                if isinstance(graded_path, (tuple, list)):
                    graded_path = graded_path[0] if graded_path else ""

                self.last_graded_path = graded_path

                print(f"\n✅ Done! Output folder: {graded_path}\n")

                # Update UI safely
                self._ui_safe(self._set_badge, "done", "Done ✅")
                self._ui_safe(self.step_var.set, "Pipeline complete.")
                self._ui_safe(self.open_out_btn.configure, state="normal")
                self._ui_safe(self.copy_path_btn.configure, state="normal")

            except Exception as e:
                print(f"\n❌ ERROR: {e}\n")
                self._ui_safe(self._set_badge, "err", "Error ❌")
                self._ui_safe(self.step_var.set, "Pipeline error. See log.")

            finally:
                sys.stdout = orig_stdout
                sys.stderr = orig_stderr
                self._ui_safe(self.progress.stop)
                self._ui_safe(self.run_btn.configure, state="normal")

        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()


if __name__ == "__main__":
    App().mainloop()
