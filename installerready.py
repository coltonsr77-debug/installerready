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

        # Assume the installer EXE is in the repo folder
        source_path = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
        threading.Thread(target=self.run_install, args=(source_path, install_path), daemon=True).start()

    def run_install(self, source, destination):
        try:
            self.status.config(text="Installing files...")
            os.makedirs(destination, exist_ok=True)

            files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
            total = len(files)
            count = 0

            for file in files:
                if file.lower() == "installerready.exe":
                    continue  # Skip itself

                src_file = os.path.join(source, file)
                dest_file = os.path.join(destination, file)
                shutil.copy2(src_file, dest_file)

                count += 1
                self.progress["value"] = (count / total) * 100
                self.update_idletasks()
                time.sleep(0.2)

            self.status.config(text="✅ Installation complete!")

            # Optionally create desktop shortcut (Windows only)
            self.create_shortcut(destination)

            messagebox.showinfo("Success", "Installation finished successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Installation failed: {e}")

    def create_shortcut(self, target_folder):
        """Create a desktop shortcut to the main app (Windows only)."""
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop, "MyApp.lnk")

            target = os.path.join(target_folder, "main.py")
            if not os.path.exists(target):
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
