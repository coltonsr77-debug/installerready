import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import requests
import os
import zipfile
import io
import re
import subprocess

VERSION = "0.4"
OWNER = "coltonsr77"
API_BASE = f"https://api.github.com/users/{OWNER}/repos"


class InstallerReadyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"InstallerReady v{VERSION}")
        self.geometry("700x500")
        self.resizable(False, False)
        self.install_path = os.getcwd()
        self.projects = []
        self.create_tabs()
        self.load_projects()

    def create_tabs(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self.tab_github = self.tabview.add("Install from GitHub")
        self.tab_myprojects = self.tabview.add("My Projects")
        self.tab_about = self.tabview.add("About")

        self.create_github_tab()
        self.create_myprojects_tab()
        self.create_about_tab()

    def create_github_tab(self):
        ctk.CTkLabel(self.tab_github, text="Install from GitHub URL", font=("Arial", 18, "bold")).pack(pady=10)
        self.repo_entry = ctk.CTkEntry(self.tab_github, placeholder_text="Enter GitHub repository URL...")
        self.repo_entry.pack(padx=20, pady=10, fill="x")

        ctk.CTkButton(self.tab_github, text="Select Install Folder", command=self.select_folder).pack(pady=5)
        self.folder_label = ctk.CTkLabel(self.tab_github, text=f"Install Path: {self.install_path}")
        self.folder_label.pack()

        self.progress = ctk.CTkProgressBar(self.tab_github, width=400)
        self.progress.set(0)
        self.progress.pack(pady=20)
        self.progress_label = ctk.CTkLabel(self.tab_github, text="Ready")
        self.progress_label.pack()

        ctk.CTkButton(self.tab_github, text="Install", command=self.start_install_from_url).pack(pady=10)

    def create_myprojects_tab(self):
        ctk.CTkLabel(self.tab_myprojects, text="My GitHub Projects", font=("Arial", 18, "bold")).pack(pady=10)
        self.projects_frame = ctk.CTkScrollableFrame(self.tab_myprojects, width=650, height=350)
        self.projects_frame.pack(padx=10, pady=5, fill="both", expand=True)
        ctk.CTkButton(self.tab_myprojects, text="Refresh List", command=self.load_projects).pack(pady=5)

    def create_about_tab(self):
        text = (
            f"InstallerReady v{VERSION}\n\n"
            "Created by Colton Robertson\n\n"
            "Use this tool to install GitHub projects easily.\n"
            "You can install any repository via URL or from your own projects list."
        )
        ctk.CTkLabel(self.tab_about, text=text, justify="left").pack(padx=20, pady=20)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.install_path = path
            self.folder_label.configure(text=f"Install Path: {self.install_path}")

    def update_progress(self, value, text):
        self.progress.set(value)
        self.progress_label.configure(text=text)
        self.update_idletasks()

    def start_install_from_url(self):
        url = self.repo_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a GitHub repository URL.")
            return
        threading.Thread(target=self.download_and_extract, args=(url,), daemon=True).start()

    def start_install_project(self, repo_name):
        url = f"https://github.com/{OWNER}/{repo_name}"
        threading.Thread(target=self.download_and_extract, args=(url,), daemon=True).start()

    def download_and_extract(self, repo_url):
        try:
            self.update_progress(0.05, "Downloading repository...")
            repo_name = self.get_repo_name(repo_url)
            zip_url = f"{repo_url}/archive/refs/heads/main.zip"
            r = requests.get(zip_url, stream=True)
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            buffer = io.BytesIO()

            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    buffer.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        self.update_progress(min(0.8, downloaded / total * 0.8), f"Downloading {repo_name}...")

            buffer.seek(0)
            with zipfile.ZipFile(buffer) as zip_ref:
                zip_ref.extractall(self.install_path)
            self.update_progress(1.0, "Done!")
            messagebox.showinfo("Installed", f"{repo_name} installed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install project:\n{e}")
            self.update_progress(0, "Error")

    def load_projects(self):
        for widget in self.projects_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.projects_frame, text="Loading projects...", font=("Arial", 14)).pack(pady=20)
        threading.Thread(target=self.fetch_projects, daemon=True).start()

    def fetch_projects(self):
        try:
            r = requests.get(API_BASE)
            r.raise_for_status()
            self.projects = r.json()
            self.display_projects()
        except Exception as e:
            for widget in self.projects_frame.winfo_children():
                widget.destroy()
            ctk.CTkLabel(self.projects_frame, text=f"Error loading projects: {e}", text_color="red").pack(pady=20)

    def display_projects(self):
        for widget in self.projects_frame.winfo_children():
            widget.destroy()

        for project in self.projects:
            frame = ctk.CTkFrame(self.projects_frame)
            frame.pack(fill="x", padx=10, pady=5)

            name = project.get("name", "Unnamed")
            desc = project.get("description", "No description provided.")
            ctk.CTkLabel(frame, text=name, font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(frame, text=desc, wraplength=600, justify="left").pack(anchor="w", padx=10)
            ctk.CTkButton(frame, text="Install", command=lambda n=name: self.start_install_project(n)).pack(pady=5)

    def get_repo_name(self, repo_url):
        match = re.search(r"github\.com/[^/]+/([^/]+)", repo_url)
        if match:
            return match.group(1).replace(".git", "")
        return "repository"


if __name__ == "__main__":
    app = InstallerReadyApp()
    app.mainloop()

