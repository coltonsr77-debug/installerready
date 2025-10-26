import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
import zipfile
import io
import threading

class InstallerReadyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("InstallerReady v0.3")
        self.geometry("500x400")

        self.repo_label = ttk.Label(self, text="GitHub Repository URL:")
        self.repo_label.pack(pady=10)

        self.repo_entry = ttk.Entry(self, width=50)
        self.repo_entry.pack()

        self.install_button = ttk.Button(self, text="Install Project", command=self.download_repo)
        self.install_button.pack(pady=20)

        self.status_label = ttk.Label(self, text="")
        self.status_label.pack()

    def download_repo(self):
        repo_url = self.repo_entry.get().strip()
        if not repo_url:
            messagebox.showerror("Error", "Please enter a GitHub repo URL.")
            return

        threading.Thread(target=self._download_repo_thread, args=(repo_url,), daemon=True).start()

    def _download_repo_thread(self, repo_url):
        try:
            self.status_label.config(text="Downloading repository...")
            self.install_button.config(state="disabled")

            # Handle GitHub repo name
            if repo_url.endswith("/"):
                repo_url = repo_url[:-1]
            repo_name = repo_url.split("/")[-1]

            zip_url = repo_url + "/archive/refs/heads/main.zip"
            response = requests.get(zip_url)
            response.raise_for_status()

            zip_data = zipfile.ZipFile(io.BytesIO(response.content))
            extract_path = os.path.join(os.getcwd(), repo_name)
            zip_data.extractall(extract_path)

            self.status_label.config(text=f"✅ Installed to {extract_path}")
        except Exception as e:
            self.status_label.config(text=f"❌ Error: {e}")
        finally:
            self.install_button.config(state="normal")

def main():
    app = InstallerReadyApp()
    app.mainloop()

if __name__ == "__main__":
    main()
