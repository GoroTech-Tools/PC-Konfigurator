"""
PC-Konfigurator - Haupt-GUI-Anwendung
=====================================

Moderne GUI-Anwendung zur PC-Konfiguration mit CustomTkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import sys
import os
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
from ui.execution_flow import (
    run_full_configuration_flow,
    run_office_configuration_flow,
)
from ui.configuration_tab import build_configuration_tab
from ui.overview_tab import build_overview_tab
from ui.registry_info_tab import build_registry_info_tab
from ui.layout import (
    build_main_layout,
    TAB_CONFIG,
    TAB_EXECUTION,
    TAB_LOGS,
    TAB_REGISTRY,
)
from ui.template_status import (
    render_safe_template_status,
    render_template_status,
    render_template_status_error,
)
from ui.registry_dialogs import show_gpo_theme_check_dialog
from ui.template_dialogs import (
    run_safe_restore_templates_dialog,
    run_update_office_templates_dialog,
)
from ui.tools_dialogs import run_bitness_and_com_check
from ui.logs_panel import (
    build_logs_tab,
    refresh_logs_view,
    clear_logs_view,
    save_logs_view,
)
from ui.sizing import apply_uniform_button_sizes
from ui.system_status import (
    start_system_requirements_check,
    apply_system_status,
)
from ui.explorer_actions import (
    append_registry_restart_notice,
    restart_windows_explorer_with_prompt,
)
from ui.status_output import append_status_text
from ui.file_actions import (
    open_runtime_folder_path,
    open_documentation_file,
)
from startmenu_guard import set_startmenu_mode
from runtime.runtime_bundle import (
    get_bundle_root,
    prepare_runtime_bundle,
)

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


class PCKonfiguratorGUI:
    def _get_startmenu_mode_text(self) -> str:
        """Liefert den anzuzeigenden Startmenü-Modus als Klartext."""
        return "🟧 Klassisch (Fallback)" if self.startmenu_mode.get() == "classic" else "🟦 Windows 11 (empfohlen)"

    def _update_startmenu_mode_label(self):
        """Aktualisiert die Start-Tab-Anzeige für den aktiven Startmenü-Modus."""
        label = getattr(self, "startmenu_mode_status_label", None)
        if label is None:
            return
        try:
            is_classic = self.startmenu_mode.get() == "classic"
            color = ("#8A4B00", "#FFC37A") if is_classic else ("#114D8C", "#8EC5FF")
            label.configure(
                text=f"Aktueller Startmenü-Modus: {self._get_startmenu_mode_text()}",
                text_color=color,
            )
        except Exception:
            pass

    def _run_startmenu_guard(self):
        """Setzt beim Start den gewünschten Startmenü-Modus."""
        try:
            prefer_classic_mode = self.startmenu_mode.get() == "classic"
            result = set_startmenu_mode(
                prefer_classic_mode=prefer_classic_mode,
                auto_restart_explorer=True,
            )
            mode_label = "klassisch" if prefer_classic_mode else "Windows 11"
            if result.get("changed"):
                self.logger.info(
                    "Startmenü-Guard: Modus '%s' wurde gesetzt (%d Schlüssel angepasst, Explorer neu gestartet=%s)",
                    mode_label,
                    len(result.get("changed_keys", [])),
                    result.get("explorer_restarted", False),
                )
            else:
                self.logger.info("Startmenü-Guard: Keine Anpassung erforderlich (Modus '%s').", mode_label)
        except Exception as exc:
            self.logger.warning("Startmenü-Guard fehlgeschlagen: %s", exc)

    def _get_runtime_base_dir(self) -> Path:
        """Liefert das Basisverzeichnis der Laufzeitdaten."""
        return prepare_runtime_bundle(
            app_name=APP_NAME,
            version=BUILD_INFO.get("version", "dev"),
            runtime_folders=RUNTIME_FOLDERS,
            runtime_files=RUNTIME_FILES,
        )

    def _get_icon_path(self) -> Path:
        """Ermittelt den Pfad zur ICO-Datei für GUI und EXE-Modus."""
        bundle_icon = get_bundle_root() / "app_icon.ico"
        if bundle_icon.exists():
            return bundle_icon
        return self.app_dir / "app_icon.ico"

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
                "startmenu_mode": self.startmenu_mode.get(),
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

        startmenu_mode = str(settings.get("startmenu_mode", "win11")).strip().lower()
        if startmenu_mode in ("win11", "classic"):
            self.startmenu_mode.set(startmenu_mode)

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

    def _on_startmenu_mode_changed(self, *_args):
        """Persistiert den Modus und setzt ihn direkt im Benutzerkontext."""
        self._save_gui_state()
        self._run_startmenu_guard()
        self._update_startmenu_mode_label()

    def _update_last_result_view(self):
        started_label = getattr(self, "last_result_started_label", None)
        mode_label = getattr(self, "last_result_mode_label", None)
        status_label = getattr(self, "last_result_status_label", None)
        log_label = getattr(self, "last_result_log_label", None)

        if (
            started_label is None
            or mode_label is None
            or status_label is None
            or log_label is None
        ):
            return

        started_label.configure(text=f"Start: {self._last_run_started}")
        mode_label.configure(text=f"Modus: {self._last_run_mode}")
        status_label.configure(text=f"Status: {self._last_run_status}")
        log_name = Path(self._last_run_log_path).name if self._last_run_log_path else "-"
        log_label.configure(text=f"Log: {log_name}")

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
        show_gpo_theme_check_dialog(self.root)

    def run_bitness_check(self):
        run_bitness_and_com_check(self.logger)
    
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
        self.startmenu_mode = tk.StringVar(value="win11")
        self.font_name = tk.StringVar(value=default_font_family)
        self.font_size_word = tk.IntVar(value=11)
        self.font_size_excel = tk.IntVar(value=10)
        self.run_controller: ExecutionRunController | None = None
        self._last_run_started = "-"
        self._last_run_mode = "-"
        self._last_run_status = "-"
        self._last_run_log_path = ""
        self.start_status_label = None
        self.startmenu_mode_status_label = None
        self.template_status_frame = None
        self._logs_auto_refresh_job = None
        self._logs_auto_refresh_ms = 2000

        self._load_gui_state()
        self._run_startmenu_guard()
        
        self.create_widgets()

        # Persistenz bei Änderungen
        self.target_drive.trace_add("write", self._on_setting_changed)
        self.use_documents.trace_add("write", self._on_setting_changed)
        self.startmenu_mode.trace_add("write", self._on_startmenu_mode_changed)
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
        self.root.geometry("1180x900")
        self.root.minsize(1040, 780)
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
        layout_refs = build_main_layout(self.root, title="PC-Konfigurator")
        self.tabview = layout_refs["tabview"]
        
        self.create_overview_tab()
        self.create_start_tab()
        self.create_configuration_tab()
        self.create_registry_info_tab()
        self.create_execution_tab()
        self.create_logs_tab()

        apply_uniform_button_sizes(self.root)

    def _switch_to_tab(self, tab_name: str):
        """Wechselt robust auf den gewünschten Tab."""
        try:
            self.tabview.set(tab_name)
        except Exception:
            pass

    def open_runtime_folder(self, folder_name: str):
        """Öffnet einen Laufzeitordner (wird bei Bedarf erstellt)."""
        open_runtime_folder_path(self.app_dir, folder_name)

    def open_documentation(self, doc_name: str):
        """Öffnet eine Dokumentationsdatei im docs-Ordner."""
        open_documentation_file(self.app_dir, doc_name)

    def create_start_tab(self):
        """AP1-ähnlicher Startbereich mit klaren Schnellaktionen."""
        refs = build_start_tab(
            self.tabview,
            version=self.version,
            current_startmenu_mode_text=self._get_startmenu_mode_text(),
            on_open_config=lambda: self._switch_to_tab(TAB_CONFIG),
            on_open_registry_info=lambda: self._switch_to_tab(TAB_REGISTRY),
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
            on_show_execution=lambda: self._switch_to_tab(TAB_EXECUTION),
        )
        self.startmenu_mode_status_label = refs.get("startmenu_mode_label") if isinstance(refs, dict) else None
        self._update_startmenu_mode_label()
        
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
            startmenu_mode_var=self.startmenu_mode,
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
            self._switch_to_tab(TAB_EXECUTION)
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
            self._switch_to_tab(TAB_EXECUTION)
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
        run_full_configuration_flow(
            root_update=self.root.update,
            system_checker=self.system_checker,
            install_all_fonts=self._install_all_fonts,
            get_office_settings_from_gui=self._get_office_settings_from_gui,
            office_configurator=self.office_configurator,
            template_manager=self.template_manager,
            safe_office_config=self.safe_office_config,
            get_office_font_name=self._get_office_font_name,
            get_font_size_word=self.font_size_word.get,
            get_font_size_excel=self.font_size_excel.get,
            advance_step=self._advance_execution_step,
            append_status=self._append_execution_status,
            add_registry_restart_notice=self._add_registry_restart_notice,
            finish_progress=self._finish_execution_progress,
        )
    
    def _run_office_configuration(self):
        """Nur Office-Konfiguration in separatem Thread"""
        run_office_configuration_flow(
            root_update=self.root.update,
            install_all_fonts=self._install_all_fonts,
            get_office_settings_from_gui=self._get_office_settings_from_gui,
            office_configurator=self.office_configurator,
            advance_step=self._advance_execution_step,
            append_status=self._append_execution_status,
            add_registry_restart_notice=self._add_registry_restart_notice,
            finish_progress=self._finish_execution_progress,
        )

    def _add_registry_restart_notice(self):
        """Hinweis für Anwender nach Registry-Anpassungen anzeigen."""
        append_registry_restart_notice(self.execution_status)

    def restart_windows_explorer(self):
        """Startet den Windows-Explorer mit Rückfrage neu."""
        restart_windows_explorer_with_prompt(self.office_configurator, self.execution_status)
    
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
        refs = build_logs_tab(
            self.tabview,
            tab_name=TAB_LOGS,
            on_refresh=self.refresh_logs,
            on_clear=self.clear_logs,
            on_save=self.save_logs,
        )
        self.log_text = refs["log_text"]

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
            if hasattr(self, "tabview") and self.tabview.get() == TAB_LOGS:
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
        start_system_requirements_check(
            self.root,
            self.system_checker,
            self.logger,
            self.update_system_status,
        )
        
    def update_system_status(self, result):
        """System-Status in der GUI aktualisieren"""
        apply_system_status(result, self.status_label, self.start_status_label)
    
    def add_status_text(self, text):
        """Text zur Status-Anzeige hinzufügen"""
        target_widget = getattr(self, "status_text", None) or getattr(self, "execution_status", None)
        append_status_text(
            text=text,
            target_widget=target_widget,
            logger=getattr(self, "logger", None),
        )
        
    def refresh_logs(self, show_errors: bool = True):
        """Log-Dateien neu laden und anzeigen"""
        refresh_logs_view(self.log_text, self.app_dir, show_errors=show_errors)
            
    def clear_logs(self):
        """Log-Anzeige leeren"""
        clear_logs_view(self.log_text)
        
    def save_logs(self):
        """Logs in Datei speichern"""
        save_logs_view(self.log_text)
    
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
            render_safe_template_status(self.template_status_frame, status)
            
        except Exception as e:
            render_template_status_error(
                self.template_status_frame,
                f"Fehler beim Überprüfen der Templates: {str(e)}",
            )
    
    def safe_restore_templates(self):
        """Sichere Template-Wiederherstellung und Schriftart-Konfiguration"""
        run_safe_restore_templates_dialog(
            self.root,
            font_name_display=self.font_name.get(),
            font_size_word=self.font_size_word.get(),
            font_size_excel=self.font_size_excel.get(),
            office_font_name=self._get_office_font_name(),
            install_all_fonts=self._install_all_fonts,
            safe_office_config=self.safe_office_config,
            on_refresh_status=self.check_safe_template_status,
        )
    
    def show_template_status(self):
        """Überprüft den Status der Office-Templates"""
        try:
            # Template-Status ermitteln
            status = self.template_manager.check_templates_exist()
            current_fonts = self.template_manager.get_current_fonts_in_templates()
            render_template_status(self.template_status_frame, status, current_fonts)
            
        except Exception as e:
            render_template_status_error(
                self.template_status_frame,
                f"Fehler beim Überprüfen der Templates: {str(e)}",
            )
    
    def update_office_templates(self):
        """Kopiert und aktualisiert Office-Templates"""
        run_update_office_templates_dialog(
            self.root,
            font_name_display=self.font_name.get(),
            font_size_word=self.font_size_word.get(),
            font_size_excel=self.font_size_excel.get(),
            template_manager=self.template_manager,
            on_refresh_status=self.check_safe_template_status,
        )
    
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