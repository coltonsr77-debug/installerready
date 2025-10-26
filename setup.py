from setuptools import setup, find_packages

setup(
    name="InstallerReady",
    version="0.5",
    author="coltonsr77",
    author_email="coltonsr77@gmail.com",  # replace with your email
    description="A simple Tkinter GitHub project installer",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/coltonsr77/installerready",
    project_urls={
        "Bug Tracker": "https://github.com/coltonsr77/InstallerReady/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.10",
    entry_points={
        "gui_scripts": [
            "installerready=installerready.app:main",
        ],
    },
)
