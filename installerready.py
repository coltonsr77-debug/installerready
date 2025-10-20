import customtkinter as ctk
from tkinter import messagebox
import os
import subprocess
import zipfile
import requests
import io

# Version
VERSION = "0.4"

class InstallerReadyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"InstallerReady v{VERSION}")
        self.geometry("500x300")
        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="InstallerReady", font=("Arial", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(self, text=f"Version {VERSION}").pack(pady=5)

        ctk.CTkLabel(self, text="Select a folder to install a GitHub project:").pack(pady=10)
        ctk.CTkButton(self, text="Select Folder", command=self.select_folder).pack(pady=5)
        self.folder_label = ctk.CTkLabel(self, text="")
        self.folder_label.pack()

        self.repo_entry = ctk.CTkEntry(self, placeholder_text="GitHub repo URL...")
        self.repo_entry.pack(pady=10, padx=20, fill="x")

        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(0)
        self.progress.pack(pady=10)
        self.progress_label = ctk.CTkLabel(self, text="Ready")
        self.progress_label.pack()

        ctk.CTkButton(self, text="Install Project", command=self.start_install).pack(pady=10)
        ctk.CTkButton(self, text="About", command=self.show_about).pack(pady=5)

    def select_folder(self):
        from tkinter import filedialog
        path = filedialog.askdirectory()
        if path:
            self.install_path = path
            self.folder_label.configure(text=f"Install Path: {path}")
        else:
            self.install_path = os.getcwd()
            self.folder_label.configure(text=f"Install Path: {self.install_path}")

    def start_install(self):
        repo_url = self.repo_entry.get().strip()
        if not repo_url:
            messagebox.showwarning("Missing URL", "Please enter a GitHub repository URL.")
            return
        import threading
        threading.Thread(target=self.download_repo, args=(repo_url,), daemon=True).start()

    def update_progress(self, percent, message):
        self.progress.set(percent)
        self.progress_label.configure(text=message)
        self.update_idletasks()

    def download_repo(self, repo_url):
        self.update_progress(0.05, "Downloading repository...")
        try:
            zip_url = f"{repo_url}/archive/refs/heads/main.zip"
            r = requests.get(zip_url, stream=True)
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            downloaded = 0
            buffer = io.BytesIO()
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    buffer.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        self.update_progress(min(0.8, downloaded / total * 0.8), "Downloading repository...")
            buffer.seek(0)
            with zipfile.ZipFile(buffer) as zip_ref:
                zip_ref.extractall(self.install_path)
            self.update_progress(1.0, "Download complete!")
            messagebox.showinfo("Success", f"Project downloaded to {self.install_path}")
        except Exception as e:
            self.update_progress(1.0, f"Failed: {e}")
            messagebox.showerror("Error", str(e))

    def show_about(self):
        messagebox.showinfo(
            "About InstallerReady",
            f"InstallerReady v{VERSION}\nCreated by Coltonsr77"
        )

if __name__ == "__main__":
    app = InstallerReadyApp()
    app.mainloop()
