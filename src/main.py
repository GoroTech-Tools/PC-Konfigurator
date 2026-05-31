"""
PC-Konfigurator - Haupt-GUI-Anwendung
=====================================

Moderne GUI-Anwendung zur PC-Konfiguration mit CustomTkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import sys
import os
import shutil
import subprocess

# --- sys.path-Anpassung für PyInstaller-Build (src als Datenordner) ---
if getattr(sys, 'frozen', False):
    # Im EXE-Modus: src-Ordner aus dem Bundle für dynamische Module
    sys.path.insert(0, os.path.join(getattr(sys, '_MEIPASS', ''), 'src'))
from pathlib import Path
from datetime import datetime

# Lokale Module importieren
from system_checker import SystemChecker
from office_configurator import OfficeConfigurator
from pcconfig.office_template_manager import OfficeTemplateManager
from safe_office_configurator import SafeOfficeConfigurator
from file_sync import FileSync
from font_installer import FontInstaller
from logger_config import setup_logging
from registry_gui import RegistryExplanationWindow
from build_info import BUILD_INFO
from ui.state_store import GuiStateStore
from ui.run_controller import ExecutionRunController
from ui.start_tab import build_start_tab
from ui.execution_tab import build_execution_tab
from ui.configuration_tab import build_configuration_tab
from ui.overview_tab import build_overview_tab
from ui.registry_info_tab import build_registry_info_tab

# Feste Auswahlliste der unterstützten Schriftarten.
# Schlüssel  = Anzeigename im Dropdown
# Wert       = Schriftname, den Windows/Office intern kennt
FONT_OPTIONS: dict[str, str] = {
    "Aptos":              "Aptos",
    "Aptos Narrow":       "Aptos Narrow",
    "Futura Cyrillic":    "Futura Cyrillic",
    "Glacial Indifference": "Glacial Indifference",
    "Montserrat":         "Montserrat",
    "PT Sans":            "PT Sans",
    "PT Sans Narrow":     "PT Sans Narrow",
    "Raleway":            "Raleway",
}

APP_NAME = "PC-Konfigurator"
RUNTIME_FOLDERS = [
    "data",
    "docs",
    "pcconfig",
]
RUNTIME_FILES = [
    "README.md",
    "BUILD-INFO.txt",
    "app_icon.ico",
]
GUI_STATE_FILE = "gui_state.json"


def get_bundle_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def can_write_to(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except Exception:
        return False


def use_portable_runtime() -> bool:
    value = os.environ.get("PCONFIG_RUNTIME_MODE", "").strip().lower()
    return value in {"portable", "exe", "local"}


def get_runtime_root() -> Path:
    if getattr(sys, "frozen", False) and use_portable_runtime():
        exe_dir = Path(sys.executable).resolve().parent
        if can_write_to(exe_dir):
            return exe_dir

    appdata = os.environ.get("LOCALAPPDATA")
    base = Path(appdata) if appdata else Path.home() / "AppData" / "Local"
    version = BUILD_INFO.get("version", "dev")
    return base / APP_NAME / str(version)


def copy_path(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def prepare_runtime_bundle() -> Path:
    bundle_root = get_bundle_root()
    runtime_root = get_runtime_root()
    runtime_root.mkdir(parents=True, exist_ok=True)

    marker = runtime_root / ".bundle-ready"
    critical_template = runtime_root / "data" / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "Normal.dotm"
    if marker.exists() and critical_template.exists():
        return runtime_root

    for folder in RUNTIME_FOLDERS:
        copy_path(bundle_root / folder, runtime_root / folder)

    for file_name in RUNTIME_FILES:
        copy_path(bundle_root / file_name, runtime_root / file_name)

    (runtime_root / "logs").mkdir(parents=True, exist_ok=True)
    marker.write_text(BUILD_INFO.get("version", "dev"), encoding="utf-8")
    return runtime_root


class PCKonfiguratorGUI:
    def _get_runtime_base_dir(self) -> Path:
        """Liefert das Basisverzeichnis der Laufzeitdaten."""
        return prepare_runtime_bundle()

    def _get_icon_path(self) -> Path:
        """Ermittelt den Pfad zur ICO-Datei für GUI und EXE-Modus."""
        bundle_icon = get_bundle_root() / 'app_icon.ico'
        if bundle_icon.exists():
            return bundle_icon
        return self.app_dir / 'app_icon.ico'

    def _get_fonts_dir(self) -> Path:
        """Liefert das Fonts-Verzeichnis der Anwendung."""
        return self.app_dir / "data" / "Fonts"

    def _load_available_font_families(self):
        """Liefert die feste Auswahlliste der unterstützten Schriftarten."""
        return list(FONT_OPTIONS.keys())

    def _get_office_font_name(self) -> str:
        """Liefert den Windows-internen Schriftnamen für Office-Konfiguration."""
        return FONT_OPTIONS.get(self.font_name.get(), self.font_name.get())

    def _install_all_fonts(self):
        """Installiert alle Fonts aus dem Fonts-Ordner ins benutzerspezifische Fonts-Verzeichnis."""
        return self.font_installer.install_fonts_from_directory(self._get_fonts_dir())

    def _save_gui_state(self):
        data = {
            "settings": {
                "target_drive": self.target_drive.get(),
                "use_documents": bool(self.use_documents.get()),
                "font_name": self.font_name.get(),
                "font_size_word": int(self.font_size_word.get()),
                "font_size_excel": int(self.font_size_excel.get()),
            },
            "last_result": {
                "started": self._last_run_started,
                "mode": self._last_run_mode,
                "status": self._last_run_status,
                "log_path": self._last_run_log_path,
            },
        }
        self.state_store.save(data)

    def _load_gui_state(self):
        self._loaded_last_result = None
        data = self.state_store.load()
        if not data:
            return

        settings = data.get("settings", {})
        target_drive = str(settings.get("target_drive", "")).strip()
        if target_drive:
            self.target_drive.set(target_drive)

        self.use_documents.set(bool(settings.get("use_documents", False)))

        font_name = str(settings.get("font_name", "")).strip()
        if font_name in self.available_font_families:
            self.font_name.set(font_name)

        try:
            self.font_size_word.set(int(settings.get("font_size_word", 11)))
        except Exception:
            self.font_size_word.set(11)

        try:
            self.font_size_excel.set(int(settings.get("font_size_excel", 10)))
        except Exception:
            self.font_size_excel.set(10)

        self._loaded_last_result = data.get("last_result")

    def _on_setting_changed(self, *_args):
        self._save_gui_state()

    def _update_last_result_view(self):
        if not hasattr(self, "last_result_started_label"):
            return

        self.last_result_started_label.configure(text=f"Start: {self._last_run_started}")
        self.last_result_mode_label.configure(text=f"Modus: {self._last_run_mode}")
        self.last_result_status_label.configure(text=f"Status: {self._last_run_status}")
        log_name = Path(self._last_run_log_path).name if self._last_run_log_path else "-"
        self.last_result_log_label.configure(text=f"Log: {log_name}")

    def _open_last_run_log(self):
        if not self._last_run_log_path:
            messagebox.showinfo("Hinweis", "Es ist noch keine Log-Datei für einen Lauf gespeichert.")
            return

        path = Path(self._last_run_log_path)
        if not path.exists():
            messagebox.showwarning("Hinweis", f"Die letzte Log-Datei wurde nicht gefunden: {path}")
            return

        try:
            os.startfile(str(path))  # type: ignore[attr-defined]
        except Exception as exc:
            messagebox.showerror("Fehler", f"Log-Datei konnte nicht geöffnet werden: {exc}")

    def _save_execution_run_log(self, success: bool, content: str) -> str:
        logs_dir = self.app_dir / "logs"
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            mode = (self._last_run_mode or "run").lower().replace(" ", "-")
            result = "ok" if success else "error"
            file_path = logs_dir / f"gui_run_{ts}_{mode}_{result}.log"
            payload = content.strip()
            file_path.write_text((payload + "\n") if payload else "", encoding="utf-8")
            return str(file_path)
        except Exception:
            return ""

    def add_tools_menu(self):
        # Menüleiste für CustomTkinter: immer direkt mit tk.Menu arbeiten
        tk_root = self.root._get_tk() if hasattr(self.root, '_get_tk') else self.root  # type: ignore[attr-defined]
        menubar = tk.Menu(tk_root)
        tk_root.config(menu=menubar)
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Tools', menu=tools_menu)
        tools_menu.add_command(label='Bitness- und COM-Check', command=self.run_bitness_check)
        tools_menu.add_command(label='GPO-Design-Prüfung', command=self.run_gpo_check)

    def run_gpo_check(self):
        """GPO-Prüfung auf Office-Design-Richtlinien als eigenständiges Dialogfenster."""
        from registry_explainer import RegistryExplainer
        import tkinter as tk
        import customtkinter as ctk

        result = RegistryExplainer().check_gpo_office_theme()

        win = ctk.CTkToplevel(self.root)
        win.title("GPO-Design-Prüfung")
        win.geometry("820x540")
        win.lift()
        win.focus_force()
        win.grab_set()

        # Status-Zeile
        if result["gpo_active"]:
            if result["theme_related_count"] > 0:
                status = (
                    f"⚠ GPO aktiv – {result['theme_related_count']} Theme-bezogene(r) Eintrag/Einträge "
                    f"gefunden (gesamt: {result['all_entries_count']})"
                )
                color = "#e07800"
            else:
                status = (
                    f"ℹ GPO aktiv – {result['all_entries_count']} Office-Richtlinie(n), "
                    "kein direkter Theme-Eintrag"
                )
                color = "#1f6aa5"
        else:
            status = "✓ Keine Office-Gruppenrichtlinien für Themes/Designs gefunden."
            color = "#2e8b57"

        ctk.CTkLabel(
            win, text=status,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=color, wraplength=780, justify="left"
        ).pack(anchor="w", padx=16, pady=(14, 4))

        ctk.CTkLabel(
            win, text=result["recommendation"],
            wraplength=780, justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 8))

        # Detailbox
        lines = ["Geprüfte Registry-Pfade:"]
        for p in result["checked_paths"]:
            lines.append(f"  {p}")
        if result["entries"]:
            lines.append("")
            lines.append("Gefundene Richtlinien-Einträge:")
            for e in result["entries"]:
                marker = " [⚠ THEME]" if e["theme_related"] else ""
                lines.append(f"  {e['path']}")
                lines.append(f"    {e['name']} = {e['data']!r}{marker}")
        else:
            lines.append("")
            lines.append("Keine Richtlinien-Einträge gefunden.")

        box = ctk.CTkTextbox(win, font=ctk.CTkFont(family="Consolas", size=11))
        box.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        box.insert("0.0", "\n".join(lines))
        box.configure(state="disabled")

        ctk.CTkButton(win, text="Schließen", command=win.destroy).pack(pady=(0, 12))

    def run_bitness_check(self):
        import sys
        import platform
        import logging
        import winreg
        from tkinter import messagebox
        import com_bitness_checker as checker

        log = logging.getLogger("bitness_check")
        log.info("Starte Bitness- und COM-Check...")

        def _decode_hresult(err: Exception):
            hresult = getattr(err, "hresult", None)
            if hresult is None and getattr(err, "args", None):
                first = err.args[0]
                if isinstance(first, int):
                    hresult = first

            if hresult is None:
                return None, None

            unsigned = hresult & 0xFFFFFFFF
            hex_code = f"0x{unsigned:08X}"

            mapping = {
                0x80040154: "Klasse nicht registriert (ProgID/COM-Registrierung fehlt)",
                0x80070005: "Zugriff verweigert (Berechtigungen/UAC)",
                0x80080005: (
                    "COM-Serverausführung fehlgeschlagen.\n"
                    "Ursache: Sehr wahrscheinlich Click-to-Run (C2R) Office.\n"
                    "C2R-Office nutzt eine virtualisierte COM-Registrierung, die von\n"
                    "64-Bit-Prozessen per win32com.client.Dispatch() nicht gestartet werden kann.\n"
                    "→ Die Kernfunktionen dieses Programms (Registry-basiert) sind davon NICHT betroffen."
                ),
                0x800401F3: "Ungültige Klassenzeichenfolge (ProgID falsch)",
                0x80029C4A: "Typbibliothek/DLL konnte nicht geladen werden",
            }
            return hex_code, mapping.get(unsigned, "Unbekannter COM-Fehler")

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

            # Python-Runtime (nur aktuelle Laufzeit, keine externen Prozesse)
            python_arch_raw = platform.architecture()[0]
            python_bitness = "64-bit" if "64" in python_arch_raw else "32-bit"
            lines.append(f"Python (aktuelle Laufzeit): {sys.executable} ({python_bitness})")

            # Office-Bitness prüfen
            office_bits = {}
            office_progids = {"Word": "Word.Application", "Excel": "Excel.Application"}
            for app in ["Word", "Excel"]:
                bit, path = checker.get_office_bitness(app)
                if bit:
                    lines.append(f"{app}: {bit} ({path})")
                    office_bits[app] = bit
                else:
                    lines.append(f"{app}: Bitness/Pfad nicht gefunden!")

            # COM-Registrierung schnell prüfen (ohne App-Start)
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

            # Bitness-Bewertung
            lines.append("")
            lines.append("Bewertung:")
            if office_bits:
                for app, office_bit in office_bits.items():
                    if office_bit != python_bitness:
                        lines.append(f"- {app}: Python {python_bitness} vs. Office {office_bit} -> normalerweise trotzdem COM-fähig (Out-of-Process).")
                    else:
                        lines.append(f"- {app}: Python und Office haben gleiche Bitness ({office_bit}).")
            else:
                lines.append("- Office-Bitness konnte nicht ermittelt werden.")

            if getattr(sys, 'frozen', False):
                lines.append("Hinweis: Check wurde im EXE-Modus ohne externe Python-Prozesse ausgeführt.")

            output = "\n".join(lines)
            log.info(output)
            messagebox.showinfo("Bitness- und COM-Check", output[-3000:])
        except Exception as e:
            log.error(f"Fehler beim Bitness-Check: {e}")
            messagebox.showerror("Fehler", str(e))
    
    def __init__(self):
        """Initialisierung der GUI"""
        self.version = BUILD_INFO.get("version", "?")
        self.setup_appearance()
        self.root = ctk.CTk()
        self.app_dir = self._get_runtime_base_dir()
        self.state_store = GuiStateStore(self.app_dir / GUI_STATE_FILE)
        os.environ["PCONFIG_RUNTIME_ROOT"] = str(self.app_dir)
        self.setup_main_window()
        
        # Komponenten initialisieren
        self.system_checker = SystemChecker()
        self.office_configurator = OfficeConfigurator()
        self.file_sync = FileSync()
        self.font_installer = FontInstaller()
        self.registry_gui = RegistryExplanationWindow(self.root, config_callback=self._get_registry_config)
        
        # Office Template Manager initialisieren
        self.template_manager = OfficeTemplateManager(self.app_dir)
        
        # Sicherer Office-Konfigurator initialisieren
        self.safe_office_config = SafeOfficeConfigurator(self.app_dir)
        
        # Logging setup
        self.logger = setup_logging()

        self.available_font_families = self._load_available_font_families()
        default_font_family = "Aptos" if "Aptos" in self.available_font_families else self.available_font_families[0]
        
        # Variablen für Konfiguration
        self.target_drive = tk.StringVar(value="Z:")
        self.use_documents = tk.BooleanVar(value=False)
        self.font_name = tk.StringVar(value=default_font_family)
        self.font_size_word = tk.IntVar(value=11)
        self.font_size_excel = tk.IntVar(value=10)
        self.run_controller: ExecutionRunController | None = None
        self._last_run_started = "-"
        self._last_run_mode = "-"
        self._last_run_status = "-"
        self._last_run_log_path = ""
        self.start_status_label = None
        self.template_status_frame = None
        self._logs_auto_refresh_job = None
        self._logs_auto_refresh_ms = 2000

        self._load_gui_state()
        
        self.create_widgets()

        # Persistenz bei Änderungen
        self.target_drive.trace_add("write", self._on_setting_changed)
        self.use_documents.trace_add("write", self._on_setting_changed)
        self.font_name.trace_add("write", self._on_setting_changed)
        self.font_size_word.trace_add("write", self._on_setting_changed)
        self.font_size_excel.trace_add("write", self._on_setting_changed)

        if isinstance(self._loaded_last_result, dict):
            self._last_run_started = str(self._loaded_last_result.get("started", "-"))
            self._last_run_mode = str(self._loaded_last_result.get("mode", "-"))
            self._last_run_status = str(self._loaded_last_result.get("status", "-"))
            self._last_run_log_path = str(self._loaded_last_result.get("log_path", ""))
            self._update_last_result_view()

        self.add_tools_menu()
        # Systemstatus direkt beim Start im Hintergrund ermitteln
        self.root.after(500, self.check_system_requirements)
        
    def setup_appearance(self):
        """Erscheinungsbild der Anwendung festlegen"""
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
    def setup_main_window(self):
        """Hauptfenster konfigurieren"""
        self.root.title(f"PC-Konfigurator {self.version}")
        self.root.geometry("1180x820")
        self.root.minsize(1040, 720)
        self.root.resizable(True, True)
        
        # Icon setzen (falls vorhanden)
        icon_path = self._get_icon_path()
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except Exception:
                pass
            
        # Hidden-Attribute für Ordner setzen
        self.set_hidden_directories()
            
    def set_hidden_directories(self):
        """Setzt Hidden-Attribute für Laufzeitordner."""
        if getattr(sys, 'frozen', False):
            logs_dir = self.app_dir / "logs"
            if logs_dir.exists():
                try:
                    subprocess.run(["attrib", "+H", str(logs_dir)], check=False, capture_output=True)
                except Exception:
                    pass
            
    def create_widgets(self):
        """GUI-Widgets erstellen"""
        # Hauptframe
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titel
        title_label = ctk.CTkLabel(
            main_frame, 
            text="PC-Konfigurator", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Tabs erstellen
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabs hinzufügen
        self.tabview.add("Übersicht")
        self.tabview.add("Start")
        self.tabview.add("Vorlagen/Ablage")
        self.tabview.add("Registry")
        self.tabview.add("Ausführung")
        self.tabview.add("Logs")
        
        self.create_overview_tab()
        self.create_start_tab()
        self.create_configuration_tab()
        self.create_registry_info_tab()
        self.create_execution_tab()
        self.create_logs_tab()

    def _switch_to_tab(self, tab_name: str):
        """Wechselt robust auf den gewünschten Tab."""
        try:
            self.tabview.set(tab_name)
        except Exception:
            pass

    def open_runtime_folder(self, folder_name: str):
        """Öffnet einen Laufzeitordner (wird bei Bedarf erstellt)."""
        target = self.app_dir / folder_name
        try:
            target.mkdir(parents=True, exist_ok=True)
            os.startfile(str(target))  # type: ignore[attr-defined]
        except Exception as exc:
            messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden: {exc}")

    def open_documentation(self, doc_name: str):
        """Öffnet eine Dokumentationsdatei im docs-Ordner."""
        doc_path = self.app_dir / "docs" / doc_name
        if not doc_path.exists():
            messagebox.showwarning("Hinweis", f"Dokumentation nicht gefunden: {doc_path}")
            return
        try:
            os.startfile(str(doc_path))  # type: ignore[attr-defined]
        except Exception as exc:
            messagebox.showerror("Fehler", f"Dokumentation konnte nicht geöffnet werden: {exc}")

    def create_start_tab(self):
        """AP1-ähnlicher Startbereich mit klaren Schnellaktionen."""
        refs = build_start_tab(
            self.tabview,
            version=self.version,
            on_open_config=lambda: self._switch_to_tab("Vorlagen/Ablage"),
            on_open_registry_info=lambda: self._switch_to_tab("Registry"),
            on_run_full=self.execute_all_configurations,
            on_run_office=self.execute_office_only,
            on_check_system=self.check_system_requirements,
            on_restart_explorer=self.restart_windows_explorer,
            on_open_folder_templates=lambda: self.open_runtime_folder("data\\Datei-Vorlagen"),
            on_open_folder_fonts=lambda: self.open_runtime_folder("data\\Fonts"),
            on_open_folder_docs=lambda: self.open_runtime_folder("docs"),
            on_open_folder_logs=lambda: self.open_runtime_folder("logs"),
            on_open_doc_user=lambda: self.open_documentation("DOKUMENTATION_ANWENDER.md"),
            on_open_doc_tech=lambda: self.open_documentation("DOKUMENTATION_TECHNIK.md"),
            on_show_execution=lambda: self._switch_to_tab("Ausführung"),
        )
        
    def create_overview_tab(self):
        """Übersicht-Tab erstellen"""
        refs = build_overview_tab(
            self.tabview,
            on_check_system=self.check_system_requirements,
        )
        self.status_label = refs["status_label"]
        
    def create_configuration_tab(self):
        """Konfiguration-Tab erstellen"""
        refs = build_configuration_tab(
            self.tabview,
            use_documents_var=self.use_documents,
            target_drive_var=self.target_drive,
            font_name_var=self.font_name,
            font_size_word_var=self.font_size_word,
            font_size_excel_var=self.font_size_excel,
            available_font_families=self.available_font_families,
        )

        self.template_status_frame = refs.get("template_status_frame") if isinstance(refs, dict) else None
        
    def create_registry_info_tab(self):
        """Registry-Info Tab erstellen"""
        build_registry_info_tab(
            self.tabview,
            on_open_registry_details=self.open_registry_details,
        )

    def _run_on_ui(self, callback):
        """Führt UI-Updates thread-sicher aus."""
        try:
            self.root.after(0, callback)
        except Exception:
            pass

    def _append_execution_status(self, text: str):
        if not self.run_controller:
            return
        self.run_controller.append_status(text)

    def _reset_execution_progress(self, mode: str, title: str):
        self._last_run_started = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self._last_run_mode = "Voll" if mode == "full" else "Office"
        self._last_run_status = "Läuft ..."
        if self.run_controller:
            self.run_controller.reset(mode=mode, title=title)

        self._update_last_result_view()
        self._save_gui_state()

    def _advance_execution_step(self, detail: str | None = None):
        if not self.run_controller:
            return
        self.run_controller.advance(detail=detail)

    def _finish_execution_progress(self, success: bool):
        if self.run_controller:
            self.run_controller.finish(success=success)

        if success:
            self._last_run_status = "Erfolgreich"
        else:
            self._last_run_status = "Fehler"

        content = self.run_controller.get_log_text() if self.run_controller else ""
        self._last_run_log_path = self._save_execution_run_log(success=success, content=content)
        self._update_last_result_view()
        self._save_gui_state()
        
    def create_execution_tab(self):
        """Ausführung-Tab erstellen"""
        refs = build_execution_tab(
            self.tabview,
            on_run_full=self.execute_all_configurations,
            on_run_office=self.execute_office_only,
            on_restart_explorer=self.restart_windows_explorer,
        )

        self.execution_state_label = refs["execution_state_label"]
        self.execution_progress = refs["execution_progress"]
        self.execution_steps_label = refs["execution_steps_label"]
        self.execution_status = refs["execution_status"]

        # Legacy-Kompatibilität: ältere Methoden schreiben auf status_text
        self.status_text = self.execution_status

        self.run_controller = ExecutionRunController(
            run_on_ui=self._run_on_ui,
            state_label=self.execution_state_label,
            progress_bar=self.execution_progress,
            steps_label=self.execution_steps_label,
            status_textbox=self.execution_status,
        )
        self.run_controller.preview(mode="full")
        
    def execute_all_configurations(self):
        """Alle Konfigurationen ausführen"""
        try:
            self._switch_to_tab("Ausführung")
            self._reset_execution_progress(
                mode="full",
                title="🚀 VOLLSTÄNDIGE KONFIGURATION GESTARTET\n" + "=" * 40 + "\n\n",
            )
            
            # In separatem Thread ausführen
            thread = threading.Thread(target=self._run_full_configuration)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self._append_execution_status(f"FEHLER: {e}\n")
            self._finish_execution_progress(success=False)
    
    def execute_office_only(self):
        """Nur Office-Konfiguration ausführen"""
        try:
            self._switch_to_tab("Ausführung")
            self._reset_execution_progress(
                mode="office",
                title="📝 OFFICE-KONFIGURATION GESTARTET\n" + "=" * 35 + "\n\n",
            )
            
            # In separatem Thread ausführen
            thread = threading.Thread(target=self._run_office_configuration)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self._append_execution_status(f"FEHLER: {e}\n")
            self._finish_execution_progress(success=False)
    
    def _run_full_configuration(self):
        """Vollständige Konfiguration in separatem Thread"""
        try:
            overall_success = True

            # System-Check
            self._advance_execution_step("1. System-Check...\n")
            self.root.update()
            system_info = self.system_checker.get_system_info()
            self._append_execution_status(f"   Erfolg: {system_info.get('platform', 'System')} erkannt\n")

            # Gewählte Font-Familie installieren
            self._advance_execution_step("2. Alle Schriften aus dem Fonts-Ordner installieren...\n")
            self.root.update()
            font_result = self._install_all_fonts()
            if font_result.get('success'):
                installed_count = len(font_result.get('installed_fonts', []))
                self._append_execution_status(f"   Erfolg: {installed_count} Schrift-Dateien im Benutzerprofil installiert\n")
            else:
                self._append_execution_status(f"   Warnung: Font-Installation fehlgeschlagen ({font_result.get('error', 'Unbekannter Fehler')})\n")
            
            # Office-Konfiguration
            self._advance_execution_step("3. Office-Konfiguration...\n")
            self.root.update()
            
            office_settings = self._get_office_settings_from_gui()
            result = self.office_configurator.configure_all_settings(office_settings)
            
            if result['success']:
                applied_count = result.get('applied_count')
                if isinstance(applied_count, int):
                    self._append_execution_status(f"   Erfolg: {applied_count} Einstellungen angewendet\n")
                else:
                    self._append_execution_status("   Erfolg: Office-Einstellungen angewendet\n")
                if result.get('word_start_screen_disabled'):
                    self._append_execution_status("   ✅ Word-Startbildschirm deaktiviert (Start mit leerem Dokument)\n")
                if result.get('outlook_warning'):
                    self._append_execution_status(f"   ⚠️ Outlook-Vorlage: {result['outlook_warning']}\n")
                if result.get('windows_warning'):
                    self._append_execution_status(f"   ⚠️ Windows-Einstellungen: {result['windows_warning']}\n")
            else:
                self._append_execution_status(f"   Fehler: {result.get('error', 'Unbekannter Fehler')}\n")
                overall_success = False
            
            # Office-Templates wirklich anpassen + kopieren
            self._advance_execution_step("4. Office-Templates anpassen und kopieren...\n")
            self.root.update()
            
            try:
                mod_results = self.template_manager.update_font_in_templates(
                    font_name=self._get_office_font_name(),
                    font_size_word=self.font_size_word.get(),
                    font_size_excel=self.font_size_excel.get()
                )
                copy_results = self.template_manager.copy_templates_to_user()
                safe_results = self.safe_office_config.configure_fonts_via_registry(
                    font_name=self._get_office_font_name(),
                    font_size_word=self.font_size_word.get(),
                    font_size_excel=self.font_size_excel.get()
                )
                
                mod_ok = bool(mod_results) and all(bool(v) for v in mod_results.values())
                copy_ok = bool(copy_results) and all(bool(v) for v in copy_results.values())
                registry_ok = all(bool(v) for k, v in safe_results.items() if k != 'error')

                if mod_ok and copy_ok:
                    self._append_execution_status("   ✅ Templates angepasst und ins Benutzerprofil kopiert\n")
                else:
                    self._append_execution_status("   ⚠️ Template-Anpassung/Kopie teilweise fehlgeschlagen (Details im Log)\n")

                if registry_ok:
                    self._append_execution_status(f"   ✅ Schriftart konfiguriert: {self._get_office_font_name()}\n")
                    self._append_execution_status(f"   ✅ Word: {self.font_size_word.get()}pt, Excel: {self.font_size_excel.get()}pt\n")
                else:
                    self._append_execution_status("   ⚠️ Registry-Schriftart-Konfiguration teilweise fehlgeschlagen\n")
                    overall_success = False
                
            except Exception as template_error:
                self._append_execution_status(f"   ❌ Template-Fehler: {template_error}\n")
                overall_success = False
            
            # Datei-Synchronisation (optional)
            # (Feature nicht aktiviert)

            self._advance_execution_step("5. Abschluss...\n")
            self._append_execution_status("\nKonfiguration abgeschlossen!\n")
            self._add_registry_restart_notice()
            self._finish_execution_progress(success=overall_success)
            
        except Exception as e:
            self._append_execution_status(f"\nFEHLER: {e}\n")
            self._finish_execution_progress(success=False)
        
        self.root.update()
    
    def _run_office_configuration(self):
        """Nur Office-Konfiguration in separatem Thread"""
        try:
            self._advance_execution_step("1. Schriften installieren...\n")
            self._append_execution_status("Office-Konfiguration startet...\n")
            font_result = self._install_all_fonts()
            if font_result.get('success'):
                installed_count = len(font_result.get('installed_fonts', []))
                self._append_execution_status(f"Alle Schriften installiert: {installed_count} Dateien im Benutzerprofil\n")
            else:
                self._append_execution_status(f"Warnung: Font-Installation fehlgeschlagen ({font_result.get('error', 'Unbekannter Fehler')})\n")
            self.root.update()
            
            self._advance_execution_step("2. Office konfigurieren...\n")
            office_settings = self._get_office_settings_from_gui()
            result = self.office_configurator.configure_all_settings(office_settings, include_windows=False)
            
            if result['success']:
                applied_count = result.get('applied_count')
                if isinstance(applied_count, int):
                    self._append_execution_status(f"Erfolg: {applied_count} Einstellungen angewendet\n")
                else:
                    self._append_execution_status("Erfolg: Office-Einstellungen angewendet\n")
                if result.get('word_start_screen_disabled'):
                    self._append_execution_status("✅ Word-Startbildschirm deaktiviert (Start mit leerem Dokument)\n")
                if result.get('outlook_warning'):
                    self._append_execution_status(f"⚠️ Outlook-Vorlage: {result['outlook_warning']}\n")
                self._advance_execution_step("3. Abschluss...\n")
                self._append_execution_status("Office-Konfiguration abgeschlossen!\n")
                self._add_registry_restart_notice()
                self._finish_execution_progress(success=True)
            else:
                self._append_execution_status(f"Fehler: {result.get('error', 'Unbekannter Fehler')}\n")
                self._finish_execution_progress(success=False)
            
        except Exception as e:
            self._append_execution_status(f"FEHLER: {e}\n")
            self._finish_execution_progress(success=False)
        
        self.root.update()

    def _add_registry_restart_notice(self):
        """Hinweis für Anwender nach Registry-Anpassungen anzeigen."""
        notice = (
            "\nℹ️ Wichtiger Hinweis: Nach dem Anwenden der Registry-Einstellungen "
            "ist ein Neustart des Windows-Explorers oder eine Neuanmeldung am System empfohlen, "
            "damit alle Änderungen vollständig wirksam werden.\n"
        )
        self.execution_status.insert("end", notice)

    def restart_windows_explorer(self):
        """Startet den Windows-Explorer mit Rückfrage neu."""
        confirm = messagebox.askyesno(
            "Windows-Explorer neu starten",
            "Der Windows-Explorer wird jetzt neu gestartet.\n\n"
            "Dadurch werden Taskleiste und Desktop kurz neu geladen.\n"
            "Möchten Sie fortfahren?",
            icon="question"
        )

        if not confirm:
            return

        try:
            # Vor dem Neustart Windows-Defaults erneut anwenden (insb. TaskbarAl)
            windows_result = self.office_configurator.configure_windows_settings()
            if not windows_result.get("success", False):
                self.execution_status.insert(
                    "end",
                    f"⚠️ Windows-Einstellungen konnten nicht vollständig gesetzt werden: {windows_result.get('error', 'Unbekannter Fehler')}\n"
                )

            subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], check=False, capture_output=True)
            subprocess.Popen(["explorer.exe"])

            self.execution_status.insert(
                "end",
                "ℹ️ Windows-Explorer wurde neu gestartet. Änderungen sollten nun sichtbar sein.\n"
            )
            self.execution_status.see("end")
        except Exception as e:
            self.execution_status.insert("end", f"⚠️ Explorer-Neustart fehlgeschlagen: {e}\n")
            self.execution_status.see("end")
            messagebox.showerror(
                "Fehler beim Explorer-Neustart",
                f"Der Explorer konnte nicht neu gestartet werden:\n{e}\n\n"
                "Bitte melden Sie sich am System ab und wieder an."
            )
    
    def _get_office_settings_from_gui(self):
        """Office-Einstellungen aus GUI-Eingaben extrahieren"""
        return {
              'font_name': self._get_office_font_name(),
            'font_size_word': self.font_size_word.get(),
            'font_size_excel': self.font_size_excel.get(),
            'target_drive': self.target_drive.get(),
            'use_documents_folder': self.use_documents.get()
        }

    def _get_registry_config(self) -> dict:
        """Gibt die aktuelle Konfiguration für die Registry-Info-Anzeige zurück."""
        try:
            if self.use_documents.get():
                path = str(Path.home() / "Documents")
            else:
                drive = self.target_drive.get()
                path = (drive + "\\") if drive and Path(drive + "\\").exists() else str(Path.home() / "Documents")
            return {
                'path': path,
                'font': self._get_office_font_name(),
                'font_size_word': self.font_size_word.get(),
                'font_size_excel': self.font_size_excel.get(),
            }
        except Exception:
            return {'path': str(Path.home() / "Documents"), 'font': 'Aptos', 'font_size_word': 11, 'font_size_excel': 10}
        
    def create_logs_tab(self):
        """Logs-Tab erstellen"""
        logs_frame = self.tabview.tab("Logs")
        
        # Log-Textbereich
        self.log_text = ctk.CTkTextbox(logs_frame, height=400)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Button-Frame für Log-Aktionen
        log_button_frame = ctk.CTkFrame(logs_frame)
        log_button_frame.pack(fill="x", padx=10, pady=10)
        
        refresh_button = ctk.CTkButton(
            log_button_frame,
            text="Logs aktualisieren",
            command=self.refresh_logs
        )
        refresh_button.pack(side="left", padx=5)
        
        clear_button = ctk.CTkButton(
            log_button_frame,
            text="Logs löschen",
            command=self.clear_logs
        )
        clear_button.pack(side="left", padx=5)
        
        save_button = ctk.CTkButton(
            log_button_frame,
            text="Logs speichern",
            command=self.save_logs
        )
        save_button.pack(side="right", padx=5)

        # Initial laden + Live-Aktualisierung starten
        self.refresh_logs(show_errors=False)
        self._schedule_logs_auto_refresh()

    def _schedule_logs_auto_refresh(self):
        """Plant die periodische Live-Aktualisierung für den Logs-Tab."""
        if self._logs_auto_refresh_job:
            try:
                self.root.after_cancel(self._logs_auto_refresh_job)
            except Exception:
                pass
        self._logs_auto_refresh_job = self.root.after(self._logs_auto_refresh_ms, self._auto_refresh_logs_loop)

    def _auto_refresh_logs_loop(self):
        """Aktualisiert Logs live, solange die App läuft."""
        try:
            if hasattr(self, "tabview") and self.tabview.get() == "Logs":
                self.refresh_logs(show_errors=False)
        except Exception:
            pass
        finally:
            try:
                self._logs_auto_refresh_job = self.root.after(self._logs_auto_refresh_ms, self._auto_refresh_logs_loop)
            except Exception:
                self._logs_auto_refresh_job = None
        
    def check_system_requirements(self):
        """System-Anforderungen in separatem Thread prüfen"""
        def check():
            try:
                result = self.system_checker.check_all_requirements()
                self.root.after(0, lambda: self.update_system_status(result))
            except Exception as e:
                self.logger.error(f"Fehler bei Systemprüfung: {e}")
                self.root.after(0, lambda: self.update_system_status({"success": False, "error": str(e)}))
        
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
        
    def update_system_status(self, result):
        """System-Status in der GUI aktualisieren"""
        if result["success"]:
            office_bitness = result.get('office', {}).get('bitness', '?')
            status_text = (
                f"[OK] System OK\n"
                f"Windows: {result['windows_version']}\n"
                f"Office: {result['office_version']} ({office_bitness})"
            )
            self.status_label.configure(text=status_text, text_color="green", justify="left")
            if self.start_status_label is not None:
                self.start_status_label.configure(text=f"Status: System geprüft\n{status_text}", text_color="green", justify="left")
        else:
            error_text = f"[FEHLER] {result.get('error', 'Unbekannter Fehler')}"
            self.status_label.configure(text=error_text, text_color="red", justify="left")
            if self.start_status_label is not None:
                self.start_status_label.configure(text=f"Status: Systemprüfung fehlgeschlagen\n{error_text}", text_color="red", justify="left")
    
    def configure_office_settings(self, config):
        """Office-Einstellungen konfigurieren mit Hybrid Template-Manager"""
        try:
            # Schriftart und -größe aus Konfiguration extrahieren
            font_name = config.get('font_name', 'Aptos')
            font_size_word = config.get('font_size_word', 11)
            font_size_excel = config.get('font_size_excel', 10)
            self.add_status_text(f"🔧 Konfiguriere Office mit {font_name} (Word: {font_size_word}pt, Excel: {font_size_excel}pt)")

            # 1. Standards-Templates mit Schriftart anpassen
            self.add_status_text("📄 Standards-Templates werden angepasst...")
            mod_success = 0
            mod_total = 0
            copy_success = 0
            copy_total = 0
            modification_phase = {}
            copy_phase = {}
            overall_success = False

            # Schriftart in Templates anpassen
            try:
                mod_result = self.template_manager.update_font_in_templates(
                    font_name=font_name,
                    font_size_word=font_size_word,
                    font_size_excel=font_size_excel
                )
                modification_phase = {k: {'success': v} for k, v in mod_result.items()}
                mod_success = sum(1 for v in mod_result.values() if v)
                mod_total = len(mod_result)
            except Exception as e:
                self.logger.error(f"Fehler bei Template-Anpassung: {e}")
                self.add_status_text(f"❌ Fehler bei Template-Anpassung: {e}")

            # Templates ins Benutzerprofil kopieren
            self.add_status_text("📄 Standards-Templates werden kopiert...")
            try:
                copy_result = self.template_manager.copy_templates_to_user()
                copy_phase = {k: {'success': v} for k, v in copy_result.items()}
                copy_success = sum(1 for v in copy_result.values() if v)
                copy_total = len(copy_result)
            except Exception as e:
                self.logger.error(f"Fehler beim Kopieren der Templates: {e}")
                self.add_status_text(f"❌ Fehler beim Kopieren der Templates: {e}")

            # Status-Updates
            if mod_success == mod_total and mod_total > 0:
                self.add_status_text(f"✅ Alle {mod_total} Standards-Templates angepasst ({font_name})")
            elif mod_success > 0:
                self.add_status_text(f"⚠️ {mod_success}/{mod_total} Templates angepasst")
            else:
                self.add_status_text("❌ Template-Anpassung fehlgeschlagen")

            if copy_success == copy_total and copy_total > 0:
                self.add_status_text(f"✅ Alle {copy_total} Templates in Benutzerverzeichnisse kopiert")
            elif copy_success > 0:
                self.add_status_text(f"⚠️ {copy_success}/{copy_total} Templates kopiert")
            else:
                self.add_status_text("❌ Template-Kopierung fehlgeschlagen")

            overall_success = (mod_success == mod_total and copy_success == copy_total and mod_total > 0)
            template_results = {
                'modification_phase': modification_phase,
                'copy_phase': copy_phase,
                'overall_success': overall_success
            }

            # 2. Zusätzlich Registry-basierte Sicherheitskonfiguration
            registry_results = self.safe_office_config.configure_safe_office_defaults(
                font_name, font_size_word, font_size_excel
            )
            if registry_results['success']:
                self.add_status_text("✅ Registry-Konfiguration erfolgreich")
            else:
                self.add_status_text("⚠️ Registry-Konfiguration teilweise fehlgeschlagen")

            # 3. Alte Office-Konfiguration als Fallback
            fallback_results = self.office_configurator.configure_all_settings(config)

            # Gesamtergebnis bewerten
            overall_success = (
                template_results.get('overall_success', False) or 
                registry_results.get('success', False) or 
                fallback_results.get('success', False)
            )

            return {
                'success': overall_success,
                'template_results': template_results,
                'template_success': template_results.get('overall_success', False),
                'registry_results': registry_results,
                'fallback_results': fallback_results
            }

        except Exception as e:
            self.logger.error(f"Fehler bei Office-Konfiguration: {e}")
            self.add_status_text(f"❌ Fehler bei Office-Konfiguration: {e}")
            return {'success': False, 'error': str(e)}
        
    def add_status_text(self, text):
        """Text zur Status-Anzeige hinzufügen"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        target_widget = getattr(self, "status_text", None) or getattr(self, "execution_status", None)
        if target_widget is None:
            # Fallback für sehr frühe Initialisierungsphasen
            if hasattr(self, "logger"):
                self.logger.info(f"[{timestamp}] {text}")
            return
        target_widget.insert("end", f"[{timestamp}] {text}\n")
        target_widget.see("end")
        
    def refresh_logs(self, show_errors: bool = True):
        """Log-Dateien neu laden und anzeigen"""
        try:
            log_dir = self.app_dir / "logs"
            if not log_dir.exists():
                self.log_text.delete("0.0", "end")
                self.log_text.insert("0.0", "Keine Log-Dateien gefunden.")
                return
                
            # Neueste Log-Datei finden
            log_files = list(log_dir.glob("*.log"))
            if not log_files:
                self.log_text.delete("0.0", "end")
                self.log_text.insert("0.0", "Keine Log-Dateien gefunden.")
                return
                
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            
            # Log-Inhalt lesen und anzeigen
            with open(latest_log, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.log_text.delete("0.0", "end")
            self.log_text.insert("0.0", content)
            self.log_text.see("end")
            
        except Exception as e:
            if show_errors:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Logs: {e}")
            
    def clear_logs(self):
        """Log-Anzeige leeren"""
        self.log_text.delete("0.0", "end")
        
    def save_logs(self):
        """Logs in Datei speichern"""
        try:
            content = self.log_text.get("0.0", "end")
            if not content.strip():
                messagebox.showwarning("Warnung", "Keine Logs zum Speichern vorhanden.")
                return
                
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log-Dateien", "*.log"), ("Text-Dateien", "*.txt"), ("Alle Dateien", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_text.insert("end", f"\n[INFO] Logs gespeichert in: {filename}\n")
                self.log_text.see("end")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Logs: {e}")
    
    def open_registry_details(self):
        """Detaillierte Registry-Ansicht mit Tabs und dynamischen Einstellungen öffnen"""
        self.registry_gui.show_window()
    
    def check_safe_template_status(self):
        """Überprüft den Status der Office-Templates mit sicherer Methode"""
        if self.template_status_frame is None:
            return
        try:
            # Template-Status mit sicherer Methode ermitteln
            status = self.safe_office_config.check_template_status()
            
            # Bestehende Status-Widgets entfernen
            for widget in self.template_status_frame.winfo_children():
                widget.destroy()
            
            # Status-Anzeige erstellen
            status_info = "Template-Status (Sicherheitscheck):\\n\\n"
            
            template_names = {
                'normal_dotm': 'Word Standard-Template (Normal.dotm)',
                'mappe_xltx': 'Excel Standard-Template (Mappe.xltx)',
                'normal_email_dotm': 'Outlook E-Mail-Template (NormalEmail.dotm)'
            }
            
            for template_key, template_name in template_names.items():
                template_status = status[template_key]
                
                if template_status == "OK":
                    status_emoji = "✅"
                elif "Beschädigt" in template_status:
                    status_emoji = "⚠️"
                elif "Nicht vorhanden" in template_status:
                    status_emoji = "❌"
                else:
                    status_emoji = "⚠️"
                    
                status_info += f"{status_emoji} {template_name}\\n"
                status_info += f"   Status: {template_status}\\n\\n"
            
            status_label = ctk.CTkLabel(
                self.template_status_frame,
                text=status_info,
                justify="left",
                font=ctk.CTkFont(family="Courier New", size=11)
            )
            status_label.pack(anchor="w", padx=10, pady=5)
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.template_status_frame,
                text=f"Fehler beim Überprüfen der Templates: {str(e)}",
                text_color="red"
            )
            error_label.pack(anchor="w", padx=10, pady=5)
    
    def safe_restore_templates(self):
        """Sichere Template-Wiederherstellung und Schriftart-Konfiguration"""
        try:
            # Warnung und Bestätigung
            result = messagebox.askyesno(
                "Sichere Template-Wiederherstellung",
                "SICHERE TEMPLATE-WIEDERHERSTELLUNG\\n\\n"
                "Was passiert:\\n"
                "✅ Beschädigte Templates werden durch Original-Versionen ersetzt\\n"
                "✅ Schriftart-Einstellungen werden über Registry gesetzt (sicher!)\\n"
                "✅ Keine direkte Template-Manipulation\\n\\n"
                f"Gewählte Schriftart: {self.font_name.get()}\\n"
                f"Word-Größe: {self.font_size_word.get()}pt\\n"
                f"Excel-Größe: {self.font_size_excel.get()}pt\\n\\n"
                "Fortfahren?",
                icon="question"
            )
            
            if not result:
                return
            
            # Progress-Dialog
            progress_window = ctk.CTkToplevel(self.root)
            progress_window.title("Sichere Template-Wiederherstellung...")
            progress_window.geometry("450x150")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = ctk.CTkLabel(progress_window, text="Templates werden sicher wiederhergestellt...")
            progress_label.pack(pady=20)
            
            progress_details = ctk.CTkLabel(progress_window, text="", justify="left")
            progress_details.pack(pady=10)
            
            # Sichere Template-Konfiguration ausführen
            progress_details.configure(text="Sichere Schriftart-Konfiguration...")
            progress_window.update()

            font_install_result = self._install_all_fonts()
            
            results = self.safe_office_config.safe_font_setup(
                font_name=self._get_office_font_name(),
                font_size_word=self.font_size_word.get(),
                font_size_excel=self.font_size_excel.get()
            )
            
            progress_window.destroy()
            
            # Ergebnisse anzeigen
            if results['success']:
                recovered_templates = sum(results['template_recovery'].values())
                total_templates = len(results['template_recovery'])
                installed_font_count = len(font_install_result.get('installed_fonts', []))
                
                messagebox.showinfo(
                    "✅ Sichere Wiederherstellung erfolgreich!",
                    f"Templates und Schriftarten erfolgreich konfiguriert!\\n\\n"
                    f"📁 Templates wiederhergestellt: {recovered_templates}/{total_templates}\\n"
                    f"📝 Schriftart-Konfiguration: Erfolgreich\\n"
                    f"🔤 Installierte Font-Dateien: {installed_font_count}\\n\\n"
                    f"🎯 Neue Einstellungen:\\n"
                    f"• Schriftart: {self.font_name.get()}\\n"
                    f"• Word: {self.font_size_word.get()}pt\\n"
                    f"• Excel: {self.font_size_excel.get()}pt\\n\\n"
                    f"➤ Starten Sie Office-Programme neu für beste Ergebnisse!"
                )
            else:
                messagebox.showwarning(
                    "⚠️ Teilweise erfolgreich",
                    f"Wiederherstellung teilweise erfolgreich.\\n\\n"
                    f"Template-Wiederherstellung: {results['template_recovery']}\\n"
                    f"Font-Konfiguration: {results['font_configuration']}\\n\\n"
                    f"Überprüfen Sie die Log-Dateien für Details."
                )
            
            # Status neu laden
            self.check_safe_template_status()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei sicherer Template-Wiederherstellung: {str(e)}")
    
    def show_template_status(self):
        """Überprüft den Status der Office-Templates"""
        try:
            # Template-Status ermitteln
            status = self.template_manager.check_templates_exist()
            current_fonts = self.template_manager.get_current_fonts_in_templates()
            
            # Bestehende Status-Widgets entfernen
            for widget in self.template_status_frame.winfo_children():
                widget.destroy()
            
            # Status-Anzeige erstellen
            status_info = "Template-Status:\n\n"
            
            template_names = {
                'normal_dotm': 'Word Standard-Template (Normal.dotm)',
                'mappe_xltx': 'Excel Standard-Template (Mappe.xltx)',
                'normal_email_dotm': 'Outlook E-Mail-Template (NormalEmail.dotm)'
            }
            
            for template_key, template_name in template_names.items():
                exists = status[template_key]
                current_font = current_fonts[template_key]
                
                status_emoji = "✅" if exists else "❌"
                status_info += f"{status_emoji} {template_name}\n"
                status_info += f"   Aktuell: {current_font}\n\n"
            
            status_label = ctk.CTkLabel(
                self.template_status_frame,
                text=status_info,
                justify="left",
                font=ctk.CTkFont(family="Courier New", size=11)
            )
            status_label.pack(anchor="w", padx=10, pady=5)
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.template_status_frame,
                text=f"Fehler beim Überprüfen der Templates: {str(e)}",
                text_color="red"
            )
            error_label.pack(anchor="w", padx=10, pady=5)
    
    def update_office_templates(self):
        """Kopiert und aktualisiert Office-Templates"""
        try:
            # Office-Prozess-Warnung anzeigen
            office_warning = messagebox.askyesno(
                "Office-Programme schließen",
                "WICHTIG: Für beste Ergebnisse sollten alle Office-Programme geschlossen sein.\n\n"
                "Sind Word, Excel und Outlook geschlossen?\n\n"
                "➤ JA: Fortfahren mit Template-Update\n"
                "➤ NEIN: Zuerst Office-Programme schließen",
                icon="question"
            )
            
            if not office_warning:
                messagebox.showinfo(
                    "Template-Update abgebrochen",
                    "Bitte schließen Sie alle Office-Programme und versuchen Sie es erneut.\n\n"
                    "Office-Programme:\n• Microsoft Word\n• Microsoft Excel\n• Microsoft Outlook\n• Microsoft PowerPoint"
                )
                return
            
            # Bestätigung vom Benutzer
            result = messagebox.askyesno(
                "Templates aktualisieren",
                "Möchten Sie die Office-Templates kopieren und mit der gewählten Schriftart aktualisieren?\n\n"
                f"Gewählte Schriftart: {self.font_name.get()}\n\n"
                "Was passiert:\n"
                "• Normal.dotm → Word Standard-Template\n"
                "• Mappe.xltx → Excel Standard-Template\n"
                "• NormalEmail.dotm → Outlook E-Mail-Template\n\n"
                "Bestehende Templates werden überschrieben!"
            )
            
            if not result:
                return
            
            # Progress-Dialog anzeigen (vereinfacht)
            progress_window = ctk.CTkToplevel(self.root)
            progress_window.title("Templates werden aktualisiert...")
            progress_window.geometry("400x200")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = ctk.CTkLabel(progress_window, text="Templates werden kopiert und aktualisiert...")
            progress_label.pack(pady=20)
            
            progress_details = ctk.CTkLabel(progress_window, text="", justify="left")
            progress_details.pack(pady=10)
            
            # Template-Operationen ausführen
            progress_details.configure(text="Schritt 1/2: Templates kopieren...")
            progress_window.update()
            
            progress_details.configure(text="Schritt 1/2: Schriftarten aktualisieren...")
            progress_window.update()

            # Schriftarten in Templates aktualisieren (zuerst!)
            font_results = self.template_manager.update_font_in_templates(
                font_name=self.font_name.get(),
                font_size_word=self.font_size_word.get(),
                font_size_excel=self.font_size_excel.get()
            )

            progress_details.configure(text="Schritt 2/2: Templates kopieren...")
            progress_window.update()

            # Templates erst nach Anpassung ins Benutzerprofil kopieren
            copy_results = self.template_manager.copy_templates_to_user()
            
            progress_window.destroy()
            
            # Ergebnisse anzeigen
            success_count = sum(copy_results.values()) + sum(font_results.values())
            total_operations = len(copy_results) + len(font_results)
            
            copy_success = sum(copy_results.values())
            font_success = sum(font_results.values())
            
            # Detaillierte Ergebnis-Analyse
            failed_templates = []
            successful_templates = []
            
            for template_key in copy_results.keys():
                copy_ok = copy_results[template_key]
                font_ok = font_results[template_key]
                
                template_names = {
                    'normal_dotm': 'Word Standard-Template',
                    'mappe_xltx': 'Excel Standard-Template', 
                    'normal_email_dotm': 'Outlook E-Mail-Template'
                }
                
                template_name = template_names.get(template_key, template_key)
                
                if copy_ok and font_ok:
                    successful_templates.append(f"✅ {template_name}")
                elif copy_ok and not font_ok:
                    failed_templates.append(f"⚠️ {template_name} (kopiert, aber Schriftart-Update fehlgeschlagen)")
                elif not copy_ok and font_ok:
                    failed_templates.append(f"⚠️ {template_name} (Schriftart aktualisiert, aber Kopieren fehlgeschlagen)")
                else:
                    failed_templates.append(f"❌ {template_name} (komplett fehlgeschlagen)")
            
            if success_count == total_operations:
                messagebox.showinfo(
                    "✅ Vollständig erfolgreich!",
                    f"Alle Templates erfolgreich aktualisiert!\n\n"
                    f"Erfolgreiche Templates:\n" +
                    "\n".join(successful_templates) +
                    f"\n\nNeue Standard-Schriftart: {self.font_name.get()}\n"
                    f"Word-Größe: {self.font_size_word.get()}pt, Excel-Größe: {self.font_size_excel.get()}pt\n\n"
                    f"➤ Neue Word-Dokumente verwenden jetzt {self.font_name.get()}!\n"
                    f"➤ Neue Excel-Dokumente verwenden jetzt {self.font_name.get()}!\n"
                    f"➤ Neue E-Mails verwenden jetzt {self.font_name.get()}!"
                )
            elif len(successful_templates) > 0:
                message = f"Templates teilweise aktualisiert:\n\n"
                
                if successful_templates:
                    message += "Erfolgreich:\n" + "\n".join(successful_templates) + "\n\n"
                
                if failed_templates:
                    message += "Probleme:\n" + "\n".join(failed_templates) + "\n\n"
                
                message += f"Mögliche Ursachen für Probleme:\n"
                message += f"• Office-Programme (Word/Excel/Outlook) sind noch geöffnet\n"
                message += f"• Template-Dateien werden von anderen Programmen verwendet\n\n"
                message += f"Empfehlung: Alle Office-Programme schließen und erneut versuchen."
                
                messagebox.showwarning("⚠️ Teilweise erfolgreich", message)
            else:
                messagebox.showerror(
                    "❌ Fehler bei Template-Update",
                    f"Leider konnten keine Templates aktualisiert werden.\n\n"
                    f"Mögliche Ursachen:\n"
                    f"• Office-Programme sind geöffnet (Word, Excel, Outlook)\n"
                    f"• Template-Dateien sind gesperrt\n"
                    f"• Keine Berechtigung für Template-Verzeichnisse\n\n"
                    f"Lösungsvorschläge:\n"
                    f"1. Alle Office-Programme schließen\n"
                    f"2. Als Administrator ausführen\n"
                    f"3. Überprüfen Sie die Log-Dateien für Details"
                )
            
            # Status neu laden
            self.check_safe_template_status()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Aktualisieren der Templates: {str(e)}")
    
    def run(self):
        """Anwendung starten"""
        self.root.mainloop()


def main():
    """Hauptfunktion"""
    try:
        app = PCKonfiguratorGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Kritischer Fehler", f"Anwendung konnte nicht gestartet werden: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()