from __future__ import annotations

from typing import Tuple


def get_work_area() -> Tuple[int, int, int, int]:
    """Liefert den nutzbaren Desktop-Arbeitsbereich (ohne Taskleiste)."""
    try:
        import ctypes

        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long),
            ]

        rect = RECT()
        SPI_GETWORKAREA = 0x0030
        ok = ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
        if ok:
            return rect.left, rect.top, rect.right, rect.bottom
    except Exception:
        pass

    # Fallback: Vollbildbereich (inkl. Taskleiste), falls API nicht verfügbar ist
    return 0, 0, 1920, 1080


def center_window_on_work_area(window, width: int, height: int) -> tuple[int, int]:
    """Zentriert ein Fenster innerhalb des Arbeitsbereichs und setzt die Geometrie."""
    left, top, right, bottom = get_work_area()
    work_width = max(1, right - left)
    work_height = max(1, bottom - top)

    final_width = max(1, min(int(width), work_width))
    final_height = max(1, min(int(height), work_height))

    x = left + max(0, (work_width - final_width) // 2)
    y = top + max(0, (work_height - final_height) // 2)

    window.geometry(f"{final_width}x{final_height}+{x}+{y}")
    return final_width, final_height
