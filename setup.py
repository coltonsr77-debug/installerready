from setuptools import setup, find_packages

setup(
    name="InstallerReady",
    version="0.7",
    author="coltonsr77",
    description="A Tkinter GitHub project installer",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/coltonsr77/ installerready",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.9",
    entry_points={
        "gui_scripts": [
            "installerready=installerready.app:main",
        ],
    },
)
