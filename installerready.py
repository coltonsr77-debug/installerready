import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import sys
import subprocess

class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Project Installer")
        self.geometry("400x250")
        self.resizable(False, False)

        tk.Label(self, text="Choose where to install the project:", font=("Arial", 10)).pack(pady=10)

        self.path_var = tk.StringVar()
        tk.Entry(self, textvariable=self.path_var, width=40).pack(pady=5)
        tk.Button(self, text="Browse", command=self.choose_folder).pack(pady=5)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=15)

        self.status = tk.Label(self, text="", font=("Arial", 9))
        self.status.pack()

        tk.Button(self, text="Install", command=self.start_install).pack(pady=10)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def start_install(self):
        install_path = self.path_var.get().strip()
        if not install_path:
            messagebox.showerror("Error", "Please choose an install directory.")
            return

        # The folder where the EXE or script is running from
        source_path = os.path.dirname(os.path.abspath(
            sys.executable if getattr(sys, 'frozen', False) else __file__
        ))

        threading.Thread(target=self.run_install, args=(source_path, install_path), daemon=True).start()

    def run_install(self, source, destination):
        try:
            self.status.config(text="Installing files...")
            os.makedirs(destination, exist_ok=True)

            # Build a list of all files to copy (excluding installer-related ones and _internal folders)
            exclude_files = {
                "installerready.exe",
                "installerready.py",
                "installerready.spec",
                "__pycache__",
                ".spec",
            }

            files_to_copy = []
            for root, dirs, files in os.walk(source):
                # Skip any _internal folders
                dirs[:] = [d for d in dirs if d.lower() != "_internal"]

                for f in files:
                    if any(f.lower().endswith(ext) for ext in [".spec", ".pyc"]):
                        continue
                    if f.lower() in exclude_files:
                        continue
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, source)
                    files_to_copy.append((full_path, os.path.join(destination, rel_path)))

            total = len(files_to_copy)
            count = 0

            # Copy files recursively with progress
            for src, dest in files_to_copy:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)
                count += 1
                self.progress["value"] = (count / total) * 100
                self.update_idletasks()
                time.sleep(0.05)

            self.status.config(text="✅ Installation complete!")

            # Create optional desktop shortcut (Windows only)
            self.create_shortcut(destination)

            messagebox.showinfo("Success", "Installation finished successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Installation failed: {e}")

    def create_shortcut(self, target_folder):
        """Create a desktop shortcut to the main app (Windows only)."""
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop, "MyApp.lnk")

            # Detect main file to link (e.g., main.py or main.exe)
            target = None
            for candidate in ["main.py", "main.exe"]:
                cand_path = os.path.join(target_folder, candidate)
                if os.path.exists(cand_path):
                    target = cand_path
                    break

            if not target:
                return

            import pythoncom
            from win32com.client import Dispatch
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = target_folder
            shortcut.IconLocation = sys.executable
            shortcut.save()
        except Exception as e:
            print("Shortcut creation failed:", e)


if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()
