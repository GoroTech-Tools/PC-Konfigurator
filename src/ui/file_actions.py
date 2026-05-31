from __future__ import annotations

import os
from pathlib import Path
from tkinter import messagebox


def open_last_run_log_file(last_run_log_path: str) -> None:
    """Öffnet die zuletzt gespeicherte Log-Datei mit robusten Hinweisen."""
    if not last_run_log_path:
        messagebox.showinfo("Hinweis", "Es ist noch keine Log-Datei für einen Lauf gespeichert.")
        return

    path = Path(last_run_log_path)
    if not path.exists():
        messagebox.showwarning("Hinweis", f"Die letzte Log-Datei wurde nicht gefunden: {path}")
        return

    try:
        os.startfile(str(path))  # type: ignore[attr-defined]
    except Exception as exc:
        messagebox.showerror("Fehler", f"Log-Datei konnte nicht geöffnet werden: {exc}")


def open_runtime_folder_path(app_dir: Path, folder_name: str) -> None:
    """Öffnet einen Laufzeitordner (wird bei Bedarf erstellt)."""
    target = app_dir / folder_name
    try:
        target.mkdir(parents=True, exist_ok=True)
        os.startfile(str(target))  # type: ignore[attr-defined]
    except Exception as exc:
        messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden: {exc}")


def open_documentation_file(app_dir: Path, doc_name: str) -> None:
    """Öffnet eine Dokumentationsdatei im docs-Ordner."""
    doc_path = app_dir / "docs" / doc_name
    if not doc_path.exists():
        messagebox.showwarning("Hinweis", f"Dokumentation nicht gefunden: {doc_path}")
        return

    try:
        os.startfile(str(doc_path))  # type: ignore[attr-defined]
    except Exception as exc:
        messagebox.showerror("Fehler", f"Dokumentation konnte nicht geöffnet werden: {exc}")
