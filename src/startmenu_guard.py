"""Hilfsmodul für den Startmenü-Modus (Windows 11 oder klassisch) im Benutzerkontext."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import ctypes
import os
from pathlib import Path
import subprocess
import time

try:
    import winreg
except Exception:  # pragma: no cover
    winreg = None  # type: ignore[assignment]


WIN11_CLASSIC_CONTEXTMENU_CLSID = "{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
WIN11_CLASSIC_CONTEXTMENU_KEY = rf"Software\Classes\CLSID\{WIN11_CLASSIC_CONTEXTMENU_CLSID}\InprocServer32"
WIN11_CLASSIC_CONTEXTMENU_PARENT_KEY = rf"Software\Classes\CLSID\{WIN11_CLASSIC_CONTEXTMENU_CLSID}"


@dataclass
class StartmenuGuardResult:
    changed: bool
    changed_keys: list[str]
    explorer_restarted: bool
    errors: list[str]


@dataclass
class StartmenuAutostartProvisionResult:
    changed: bool
    guard_script_path: str
    guard_cmd_path: str
    startup_cmd_path: str
    errors: list[str]


def _set_dword_if_needed(root, path: str, name: str, value: int) -> bool:
    reg = winreg
    if reg is None:
        raise RuntimeError("winreg nicht verfügbar")

    key = reg.CreateKeyEx(root, path, 0, reg.KEY_READ | reg.KEY_WRITE)
    with key:
        try:
            current, reg_type = reg.QueryValueEx(key, name)
            if reg_type == reg.REG_DWORD and int(current) == int(value):
                return False
        except FileNotFoundError:
            pass

        reg.SetValueEx(key, name, 0, reg.REG_DWORD, int(value))
        return True


def _set_sz_if_needed(root, path: str, name: str, value: str) -> bool:
    reg = winreg
    if reg is None:
        raise RuntimeError("winreg nicht verfügbar")

    key = reg.CreateKeyEx(root, path, 0, reg.KEY_READ | reg.KEY_WRITE)
    with key:
        try:
            current, reg_type = reg.QueryValueEx(key, name)
            if reg_type == reg.REG_SZ and str(current) == str(value):
                return False
        except FileNotFoundError:
            pass

        reg.SetValueEx(key, name, 0, reg.REG_SZ, str(value))
        return True


def _restart_explorer() -> bool:
    """Startet den Explorer neu, damit Startmenü-Änderungen sofort wirksam werden."""
    try:
        def _taskbar_visible() -> bool:
            try:
                user32 = ctypes.windll.user32  # type: ignore[attr-defined]
                hwnd = user32.FindWindowW("Shell_TrayWnd", None)
                if not hwnd:
                    return False
                return bool(user32.IsWindowVisible(hwnd))
            except Exception:
                return False

        def _show_taskbar_if_present() -> bool:
            try:
                user32 = ctypes.windll.user32  # type: ignore[attr-defined]
                hwnd = user32.FindWindowW("Shell_TrayWnd", None)
                if not hwnd:
                    return False
                user32.ShowWindow(hwnd, 5)  # SW_SHOW
                user32.SetForegroundWindow(hwnd)
                return bool(user32.IsWindowVisible(hwnd))
            except Exception:
                return False

        subprocess.run(
            ["taskkill", "/F", "/IM", "explorer.exe"],
            check=False,
            capture_output=True,
            text=True,
        )

        subprocess.Popen(["cmd", "/c", "start", "", "explorer.exe"])

        deadline = time.monotonic() + 20.0
        while time.monotonic() < deadline:
            if _taskbar_visible():
                return True
            time.sleep(0.25)

        if _show_taskbar_if_present() and _taskbar_visible():
            return True

        subprocess.Popen(["cmd", "/c", "start", "", "explorer.exe"])
        deadline2 = time.monotonic() + 8.0
        while time.monotonic() < deadline2:
            if _taskbar_visible():
                return True
            time.sleep(0.25)

        if _show_taskbar_if_present() and _taskbar_visible():
            return True

        for proc in ("ShellExperienceHost", "StartMenuExperienceHost", "SearchHost"):
            subprocess.run(
                ["taskkill", "/F", "/IM", f"{proc}.exe"],
                check=False,
                capture_output=True,
                text=True,
            )

        subprocess.Popen(["cmd", "/c", "start", "", "explorer.exe"])
        subprocess.Popen(["cmd", "/c", "start", "", r"C:\Windows\System32\userinit.exe"])

        deadline3 = time.monotonic() + 12.0
        while time.monotonic() < deadline3:
            if _taskbar_visible() or _show_taskbar_if_present():
                return True
            time.sleep(0.25)

        return False
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

    reg = winreg
    if reg is None:
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
            reg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "Start_ShowClassicMode",
            mode_value,
        ),
        (
            reg.HKEY_CURRENT_USER,
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

    # Windows-11-Kontextmenü: klassisch (Key vorhanden) vs. modern (Key entfernt)
    try:
        if prefer_classic_mode:
            if _set_sz_if_needed(
                reg.HKEY_CURRENT_USER,
                WIN11_CLASSIC_CONTEXTMENU_KEY,
                "",
                "",
            ):
                changed_keys.append(f"HKCU\\{WIN11_CLASSIC_CONTEXTMENU_KEY}::(Default)")
        else:
            removed = False
            try:
                reg.DeleteKey(reg.HKEY_CURRENT_USER, WIN11_CLASSIC_CONTEXTMENU_KEY)
                removed = True
            except FileNotFoundError:
                pass

            try:
                reg.DeleteKey(reg.HKEY_CURRENT_USER, WIN11_CLASSIC_CONTEXTMENU_PARENT_KEY)
                removed = True
            except FileNotFoundError:
                pass
            except OSError:
                # Nicht leer / anderweitig belegt -> unkritisch
                pass

            if removed:
                changed_keys.append(f"HKCU\\{WIN11_CLASSIC_CONTEXTMENU_KEY}::(removed)")
    except Exception as exc:
        errors.append(f"{WIN11_CLASSIC_CONTEXTMENU_KEY}: {exc}")

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


def _write_text_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            existing = path.read_text(encoding="utf-8")
        except Exception:
            existing = ""
        if existing == content:
            return False
    path.write_text(content, encoding="utf-8")
    return True


def _build_guard_ps1(mode_value: int) -> str:
    return f"""# Auto-generiert durch PC-Konfigurator
$ErrorActionPreference = 'Stop'

$logDir = Join-Path $env:LOCALAPPDATA 'PC-Konfigurator\\logs'
$logFile = Join-Path $logDir 'startmenu-guard.log'

function Write-GuardLog {{
    param([Parameter(Mandatory)] [string]$Message)
    try {{
        if (-not (Test-Path $logDir)) {{
            New-Item -Path $logDir -ItemType Directory -Force | Out-Null
        }}
        $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        Add-Content -Path $logFile -Value "[$timestamp] $Message"
    }} catch {{
        # Logging darf den Guard nicht blockieren
    }}
}}

function Set-DwordValue {{
    param(
        [Parameter(Mandatory)] [string]$Path,
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [int]$Value
    )

    if (-not (Test-Path $Path)) {{
        New-Item -Path $Path -Force | Out-Null
    }}

    $currentValue = $null
    try {{
        $currentValue = (Get-ItemProperty -Path $Path -Name $Name -ErrorAction Stop).$Name
    }} catch {{
        $currentValue = $null
    }}

    if ($currentValue -ne $Value) {{
        New-ItemProperty -Path $Path -Name $Name -PropertyType DWord -Value $Value -Force | Out-Null
        return $true
    }}

    return $false
}}

try {{
    Write-GuardLog 'Startmenu-Guard gestartet.'

    $changed = $false
    $changed = (Set-DwordValue -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'Start_ShowClassicMode' -Value {mode_value}) -or $changed
    $changed = (Set-DwordValue -Path 'HKCU:\\Software\\ExplorerPatcher' -Name 'Start_ShowClassicMode' -Value {mode_value}) -or $changed

    $contextClassicPath = 'HKCU:\\Software\\Classes\\CLSID\\{WIN11_CLASSIC_CONTEXTMENU_CLSID}\\InprocServer32'
    $contextParentPath = 'HKCU:\\Software\\Classes\\CLSID\\{WIN11_CLASSIC_CONTEXTMENU_CLSID}'

    if ({mode_value} -eq 1) {{
        if (-not (Test-Path $contextClassicPath)) {{
            New-Item -Path $contextClassicPath -Force | Out-Null
            $changed = $true
        }}
        try {{
            $contextKey = Get-Item -Path $contextClassicPath -ErrorAction Stop
            $defaultValue = $contextKey.GetValue('', $null)
            if ($defaultValue -ne '') {{
                $contextKey.SetValue('', '', [Microsoft.Win32.RegistryValueKind]::String)
                $changed = $true
            }}
        }} catch {{
            # unkritisch
        }}
    }} else {{
        if (Test-Path $contextClassicPath) {{
            Remove-Item -Path $contextClassicPath -Force -ErrorAction SilentlyContinue
            $changed = $true
        }}
        if (Test-Path $contextParentPath) {{
            try {{
                Remove-Item -Path $contextParentPath -Force -ErrorAction Stop
                $changed = $true
            }} catch {{
                # Parent-Key kann noch Untereinträge haben; dann ignorieren
            }}
        }}
    }}

    if ($changed) {{
        Write-GuardLog 'Änderungen erkannt, Explorer wird neu gestartet.'
        Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
        Start-Process explorer.exe
    }} else {{
        Write-GuardLog 'Keine Änderung erforderlich.'
    }}

    Write-GuardLog 'Startmenu-Guard erfolgreich beendet.'
    exit 0
}} catch {{
    Write-GuardLog ("Fehler: " + $_.Exception.Message)
    exit 1
}}
"""


def _build_guard_cmd() -> str:
    return (
        "@echo off\r\n"
        "\"%SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe\" -NoProfile -ExecutionPolicy Bypass -File \"%~dp0Ensure-StartmenuMode.ps1\"\r\n"
        "exit /b %ERRORLEVEL%\r\n"
    )


def _build_startup_cmd(guard_cmd_path: Path) -> str:
    guard_cmd = str(guard_cmd_path)
    return f"@echo off\r\ncall \"{guard_cmd}\"\r\n"


def provision_startmenu_autostart(prefer_classic_mode: bool) -> dict:
    """
    Hinterlegt eine externe Startmenü-Guard-Variante im Benutzerprofil und
    registriert sie für den Benutzer-Autostart.
    """
    errors: list[str] = []
    changed = False

    appdata = os.environ.get("APPDATA", "").strip()
    if not appdata:
        return asdict(
            StartmenuAutostartProvisionResult(
                changed=False,
                guard_script_path="",
                guard_cmd_path="",
                startup_cmd_path="",
                errors=["APPDATA nicht verfügbar"],
            )
        )

    mode_value = 1 if prefer_classic_mode else 0
    guard_dir = Path(appdata) / "PC-Konfigurator" / "startmenu-guard"
    startup_dir = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

    guard_script_path = guard_dir / "Ensure-StartmenuMode.ps1"
    guard_cmd_path = guard_dir / "Ensure-StartmenuMode.cmd"
    startup_cmd_path = startup_dir / "PC-Konfigurator-StartmenuGuard.cmd"

    try:
        changed = _write_text_if_changed(guard_script_path, _build_guard_ps1(mode_value)) or changed
    except Exception as exc:
        errors.append(f"PS1 konnte nicht geschrieben werden: {exc}")

    try:
        changed = _write_text_if_changed(guard_cmd_path, _build_guard_cmd()) or changed
    except Exception as exc:
        errors.append(f"CMD konnte nicht geschrieben werden: {exc}")

    try:
        changed = _write_text_if_changed(startup_cmd_path, _build_startup_cmd(guard_cmd_path)) or changed
    except Exception as exc:
        errors.append(f"Autostart-CMD konnte nicht geschrieben werden: {exc}")

    return asdict(
        StartmenuAutostartProvisionResult(
            changed=changed,
            guard_script_path=str(guard_script_path),
            guard_cmd_path=str(guard_cmd_path),
            startup_cmd_path=str(startup_cmd_path),
            errors=errors,
        )
    )
