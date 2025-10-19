# installerready.spec
# Build this using: pyinstaller installerready.spec

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

# ---- Collect any additional modules ----
hiddenimports = collect_submodules('tkinter')
hiddenimports += collect_submodules('win32com')
hiddenimports += collect_submodules('pythoncom')

a = Analysis(
    ['installerready.py'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('tkinter'),
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='installerready',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # GUI app, no console window
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='InstallerReady'
)
