# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path


# Hilfsfunktion: Alle Dateien rekursiv für datas auflisten
def collect_datas(src_folder, dest_folder=None):
    datas = []
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, src_folder)
            rel_dir = os.path.dirname(rel_path)
            # Zielpfad für PyInstaller-Datas ist immer ein Verzeichnis
            if dest_folder:
                target = os.path.join(dest_folder, rel_dir) if rel_dir else dest_folder
            else:
                target = rel_dir if rel_dir else '.'
            datas.append((full_path, target))
    return datas


# Pfade robust auflösen (PyInstaller stellt in .spec kein __file__ bereit)
ROOT_DIR = Path(os.getcwd()).resolve()
BASE_DIR = ROOT_DIR / 'src'

# Build-Informationen laden
sys.path.insert(0, str(BASE_DIR))
from build_info import BUILD_INFO

# Versionsnummer für Ordnername extrahieren
version = BUILD_INFO['version']

# Analysis-Block

# Alle .py-Dateien aus src direkt nach src kopieren (ohne Unterordner)
src_py_files = [
    (str(BASE_DIR / f), 'src')
    for f in os.listdir(str(BASE_DIR)) if f.endswith('.py')
]

a = Analysis(
    [str(BASE_DIR / 'main.py')],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=(
        collect_datas(str(BASE_DIR / 'pcconfig'), 'pcconfig') +
        collect_datas(str(ROOT_DIR / 'data' / 'Datei-Vorlagen'), 'data/Datei-Vorlagen') +
        collect_datas(str(ROOT_DIR / 'data' / 'Fonts'), 'data/Fonts') +
        collect_datas(str(ROOT_DIR / 'docs'), 'docs') +
        src_py_files +
        [
            (str(BASE_DIR / 'app_icon.ico'), '.'),
            (str(BASE_DIR / 'BUILD-INFO.txt'), '.'),
            (str(ROOT_DIR / 'README.md'), '.'),
        ]
    ),
    hiddenimports=['pcconfig.safe_template_processor', 'pcconfig.office_template_manager', 'psutil'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    exclude_binaries=False,
    name='PC-Konfigurator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(BASE_DIR / 'app_icon.ico'),
)