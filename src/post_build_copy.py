# Nach-Build-Skript: Kopiert alle benötigten Ordner/Dateien aus _internal auf die Root-Ebene
import shutil
import os
from pathlib import Path

# Zielverzeichnis (Build-Ordner)
build_dir = Path(__file__).parent.parent / 'dist' / 'PC-Konfigurator-v2.0.26'
internal_dir = build_dir / '_internal'

# Liste der zu kopierenden Ordner/Dateien
TO_COPY = [
    'data',
    'docs',
    'README.md',
    'BUILD-INFO.txt',
    'com_bitness_checker.py',
]

def copytree(src, dst):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

def main():
    for name in TO_COPY:
        src = internal_dir / name
        dst = build_dir / name
        if src.is_dir():
            copytree(src, dst)
            print(f'Ordner kopiert: {name}')
        elif src.is_file():
            shutil.copy2(src, dst)
            print(f'Datei kopiert: {name}')
        else:
            print(f'Nicht gefunden: {name}')

if __name__ == '__main__':
    main()
