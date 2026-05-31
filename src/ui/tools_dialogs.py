from __future__ import annotations

import logging
import platform
import sys
import winreg
from tkinter import messagebox

import com_bitness_checker as checker


def run_bitness_and_com_check(logger: logging.Logger | None = None) -> None:
    """Führt den Bitness-/COM-Check aus und zeigt das Ergebnis als Dialog."""
    log = logger or logging.getLogger("bitness_check")
    log.info("Starte Bitness- und COM-Check...")

    def _get_com_registration(prog_id: str):
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\CLSID") as key:
                clsid, _ = winreg.QueryValueEx(key, "")
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"CLSID\\{clsid}\\LocalServer32") as key:
                    server, _ = winreg.QueryValueEx(key, "")
                return clsid, server
            except OSError:
                return clsid, None
        except OSError:
            return None, None

    try:
        lines = ["=== Office/Python Bitness-Checker ==="]

        python_arch_raw = platform.architecture()[0]
        python_bitness = "64-bit" if "64" in python_arch_raw else "32-bit"
        lines.append(f"Python (aktuelle Laufzeit): {sys.executable} ({python_bitness})")

        office_bits = {}
        office_progids = {"Word": "Word.Application", "Excel": "Excel.Application"}
        for app in ["Word", "Excel"]:
            bit, path = checker.get_office_bitness(app)
            if bit:
                lines.append(f"{app}: {bit} ({path})")
                office_bits[app] = bit
            else:
                lines.append(f"{app}: Bitness/Pfad nicht gefunden!")

        lines.append("")
        lines.append("COM-Registrierung (schnell):")
        for app, prog_id in office_progids.items():
            clsid, server = _get_com_registration(prog_id)
            if clsid:
                if server:
                    lines.append(f"- {app}: ProgID/CLSID OK ({clsid})")
                else:
                    lines.append(f"- {app}: CLSID vorhanden ({clsid}), aber LocalServer32 fehlt")
            else:
                lines.append(f"- {app}: ProgID nicht registriert ({prog_id})")

        lines.append("")
        lines.append("Bewertung:")
        if office_bits:
            for app, office_bit in office_bits.items():
                if office_bit != python_bitness:
                    lines.append(
                        f"- {app}: Python {python_bitness} vs. Office {office_bit} -> normalerweise trotzdem COM-fähig (Out-of-Process)."
                    )
                else:
                    lines.append(f"- {app}: Python und Office haben gleiche Bitness ({office_bit}).")
        else:
            lines.append("- Office-Bitness konnte nicht ermittelt werden.")

        if getattr(sys, "frozen", False):
            lines.append("Hinweis: Check wurde im EXE-Modus ohne externe Python-Prozesse ausgeführt.")

        output = "\n".join(lines)
        log.info(output)
        messagebox.showinfo("Bitness- und COM-Check", output[-3000:])
    except Exception as exc:
        log.error(f"Fehler beim Bitness-Check: {exc}")
        messagebox.showerror("Fehler", str(exc))
