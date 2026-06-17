"""Hilfsmodul für den Startmenü-Modus (Windows 11 oder klassisch) im Benutzerkontext."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import subprocess

try:
    import winreg
except Exception:  # pragma: no cover
    winreg = None  # type: ignore[assignment]


@dataclass
class StartmenuGuardResult:
    changed: bool
    changed_keys: list[str]
    explorer_restarted: bool
    errors: list[str]


def _set_dword_if_needed(root, path: str, name: str, value: int) -> bool:
    key = winreg.CreateKeyEx(root, path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
    with key:
        try:
            current, reg_type = winreg.QueryValueEx(key, name)
            if reg_type == winreg.REG_DWORD and int(current) == int(value):
                return False
        except FileNotFoundError:
            pass

        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, int(value))
        return True


def _restart_explorer() -> bool:
    """Startet den Explorer neu, damit Startmenü-Änderungen sofort wirksam werden."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "explorer.exe"],
            check=False,
            capture_output=True,
            text=True,
        )
        subprocess.Popen(["explorer.exe"])
        return True
    except Exception:
        return False


def set_startmenu_mode(prefer_classic_mode: bool, auto_restart_explorer: bool = True) -> dict:
    """
    Setzt den gewünschten Startmenü-Modus im HKCU-Kontext.

    Setzt bekannte Schalter auf klassisch (1) oder Windows 11 (0) und startet
    den Explorer nur dann neu, wenn tatsächlich eine Änderung vorgenommen wurde.
    """
    changed_keys: list[str] = []
    errors: list[str] = []
    mode_value = 1 if prefer_classic_mode else 0

    if winreg is None:
        return asdict(
            StartmenuGuardResult(
                changed=False,
                changed_keys=[],
                explorer_restarted=False,
                errors=["winreg nicht verfügbar"],
            )
        )

    targets = [
        (
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "Start_ShowClassicMode",
            mode_value,
        ),
        (
            winreg.HKEY_CURRENT_USER,
            r"Software\ExplorerPatcher",
            "Start_ShowClassicMode",
            mode_value,
        ),
    ]

    for root, path, name, value in targets:
        try:
            if _set_dword_if_needed(root, path, name, value):
                changed_keys.append(f"HKCU\\{path}::{name}")
        except Exception as exc:
            errors.append(f"{path}::{name}: {exc}")

    changed = len(changed_keys) > 0
    explorer_restarted = False
    if changed and auto_restart_explorer:
        explorer_restarted = _restart_explorer()

    return asdict(
        StartmenuGuardResult(
            changed=changed,
            changed_keys=changed_keys,
            explorer_restarted=explorer_restarted,
            errors=errors,
        )
    )


def ensure_win11_startmenu(auto_restart_explorer: bool = True) -> dict:
    """Kompatibilitäts-Wrapper: Erzwingt das Windows-11-Startmenü."""
    return set_startmenu_mode(prefer_classic_mode=False, auto_restart_explorer=auto_restart_explorer)
