"""Sicherung und Wiederherstellung von Microsoft-Edge-Profilen.

Die portable Sicherung liegt im vom Anwender gewählten Datei-Vorlagen-Ordner:

    Datei-Vorlagen/Edge-Profile/
        User Data/       Edge-Profilordner inklusive Local State
    Datei-Vorlagen/E-Mail-Signaturen/
        Outlook-Signaturen (falls vorhanden)

Cache- und Prozessdateien werden bewusst ausgelassen. Verschlüsselte Edge-
Anmeldedaten sind grundsätzlich an das Windows-Benutzerprofil gebunden und
können auf einem anderen Rechner ggf. nicht entschlüsselt werden.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path

from user_paths import get_documents_directory


class EdgeProfileManager:
    """Sichert und restauriert Edge-Profile und Outlook-Signaturen."""

    BACKUP_FOLDER_NAME = "Edge-Profile"
    SIGNATURE_BACKUP_FOLDER_NAME = "E-Mail-Signaturen"
    USER_DATA_FOLDER_NAME = "User Data"
    PROFILE_NAMES = {"Default"}

    # Temporäre, automatisch regenerierte oder häufig gesperrte Daten.
    IGNORED_NAMES = {
        "Cache",
        "Code Cache",
        "GPUCache",
        "DawnCache",
        "Crashpad",
        "BrowserMetrics",
        "GrShaderCache",
        "Service Worker",
        "SingletonCookie",
        "SingletonLock",
        "SingletonSocket",
    }

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger(__name__)

    @property
    def edge_user_data_dir(self) -> Path:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        return Path(local_app_data) / "Microsoft" / "Edge" / "User Data"

    @property
    def signatures_dir(self) -> Path:
        app_data = os.environ.get("APPDATA", "")
        return Path(app_data) / "Microsoft" / "Signatures"

    @classmethod
    def target_backup_dir(cls, office_settings: dict) -> Path:
        """Ermittelt den portablen Backup-Ordner aus den GUI-Einstellungen."""
        if office_settings.get("use_documents_folder"):
            base = get_documents_directory()
        else:
            drive = str(office_settings.get("target_drive", "")).strip()
            base = Path(drive + "\\") if drive else get_documents_directory()
        return base / "Datei-Vorlagen" / cls.BACKUP_FOLDER_NAME

    @classmethod
    def target_signatures_dir(cls, office_settings: dict) -> Path:
        """Ermittelt den separaten portablen Ablageort für E-Mail-Signaturen."""
        return cls.target_backup_dir(office_settings).parent / cls.SIGNATURE_BACKUP_FOLDER_NAME

    @classmethod
    def _is_profile_dir(cls, path: Path) -> bool:
        return path.is_dir() and (path.name in cls.PROFILE_NAMES or path.name.startswith("Profile "))

    @classmethod
    def _profile_dirs(cls, user_data_dir: Path) -> list[Path]:
        if not user_data_dir.is_dir():
            return []
        return sorted(
            (path for path in user_data_dir.iterdir() if cls._is_profile_dir(path)),
            key=lambda path: path.name.lower(),
        )

    @classmethod
    def _copy_ignore(cls, directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in cls.IGNORED_NAMES or name.startswith("Singleton")}

    @classmethod
    def _has_backup(cls, backup_dir: Path) -> bool:
        user_data = backup_dir / cls.USER_DATA_FOLDER_NAME
        return bool(cls._profile_dirs(user_data)) or (user_data / "Local State").is_file()

    @staticmethod
    def _has_files(directory: Path) -> bool:
        return directory.is_dir() and any(path.is_file() for path in directory.rglob("*"))

    def _close_edge(self) -> None:
        """Beendet Edge vor dem Zugriff auf gesperrte Profildateien."""
        try:
            subprocess.run(
                ["taskkill", "/IM", "msedge.exe", "/F"],
                check=False,
                capture_output=True,
                creationflags=0x08000000 if os.name == "nt" else 0,
            )
            self.logger.info("Microsoft Edge wurde vor der Profil-Synchronisierung beendet.")
        except Exception as exc:
            self.logger.warning("Microsoft Edge konnte nicht beendet werden: %s", exc)

    @staticmethod
    def _copy_tree(source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            source,
            target,
            dirs_exist_ok=True,
            ignore=EdgeProfileManager._copy_ignore,
        )

    def restore(self, office_settings: dict) -> dict:
        """Stellt ein vorhandenes Backup im aktuellen Windows-Benutzerprofil wieder her."""
        backup_dir = self.target_backup_dir(office_settings)
        backup_signatures = self.target_signatures_dir(office_settings)
        has_edge_backup = self._has_backup(backup_dir)
        has_signature_backup = self._has_files(backup_signatures)
        if not has_edge_backup and not has_signature_backup:
            return {
                "success": True,
                "restored": False,
                "profiles": 0,
                "signatures": False,
                "signature_backup_available": False,
                "message": "Kein Edge- oder Signatur-Backup vorhanden.",
            }

        if has_edge_backup:
            self._close_edge()
        restored_profiles = 0
        restored_signatures = False
        try:
            if has_edge_backup:
                backup_user_data = backup_dir / self.USER_DATA_FOLDER_NAME
                self.edge_user_data_dir.mkdir(parents=True, exist_ok=True)
                for source in self._profile_dirs(backup_user_data):
                    self._copy_tree(source, self.edge_user_data_dir / source.name)
                    restored_profiles += 1

                local_state = backup_user_data / "Local State"
                if local_state.is_file():
                    shutil.copy2(local_state, self.edge_user_data_dir / local_state.name)

            if not self._has_files(self.signatures_dir) and self._has_files(backup_signatures):
                self._copy_tree(backup_signatures, self.signatures_dir)
                restored_signatures = True
                self.logger.info("E-Mail-Signaturen wurden in das leere Benutzerverzeichnis wiederhergestellt.")

            parts = []
            if has_edge_backup:
                parts.append(f"{restored_profiles} Edge-Profil(e)")
            if restored_signatures:
                parts.append("E-Mail-Signaturen")
            message = " und ".join(parts) + " wiederhergestellt." if parts else (
                "Vorhandene E-Mail-Signaturen wurden beibehalten."
            )
            self.logger.info(message)
            return {
                "success": True,
                "restored": bool(restored_profiles or restored_signatures),
                "profiles": restored_profiles,
                "signatures": restored_signatures,
                "signature_backup_available": has_signature_backup,
                "message": message,
            }
        except Exception as exc:
            self.logger.error("Edge-Backup konnte nicht wiederhergestellt werden: %s", exc)
            return {"success": False, "restored": False, "error": str(exc)}

    def backup(self, office_settings: dict) -> dict:
        """Sichert vorhandene Edge-Profile und Signaturen in den Zielordner."""
        profiles = self._profile_dirs(self.edge_user_data_dir)
        signatures_exist = self._has_files(self.signatures_dir)
        if not profiles and not signatures_exist:
            return {
                "success": True,
                "backed_up": False,
                "profiles": 0,
                "signatures": False,
                "message": "Keine Edge-Profile oder E-Mail-Signaturen gefunden.",
            }

        if profiles:
            self._close_edge()
        backup_dir = self.target_backup_dir(office_settings)
        temporary_dir = backup_dir.with_name(backup_dir.name + ".pckconfig-tmp")
        try:
            if temporary_dir.exists():
                shutil.rmtree(temporary_dir, ignore_errors=True)
            temporary_dir.mkdir(parents=True, exist_ok=True)

            user_data_target = temporary_dir / self.USER_DATA_FOLDER_NAME
            user_data_target.mkdir(parents=True, exist_ok=True)
            for source in profiles:
                self._copy_tree(source, user_data_target / source.name)

            local_state = self.edge_user_data_dir / "Local State"
            if local_state.is_file():
                shutil.copy2(local_state, user_data_target / local_state.name)

            backup_dir.parent.mkdir(parents=True, exist_ok=True)
            if profiles:
                if backup_dir.exists():
                    shutil.rmtree(backup_dir, ignore_errors=True)
                os.replace(temporary_dir, backup_dir)
            else:
                shutil.rmtree(temporary_dir, ignore_errors=True)

            if signatures_exist:
                signature_target = self.target_signatures_dir(office_settings)
                signature_temp = signature_target.with_name(signature_target.name + ".pckconfig-tmp")
                if signature_temp.exists():
                    shutil.rmtree(signature_temp, ignore_errors=True)
                self._copy_tree(self.signatures_dir, signature_temp)
                signature_target.parent.mkdir(parents=True, exist_ok=True)
                if signature_target.exists():
                    shutil.rmtree(signature_target, ignore_errors=True)
                os.replace(signature_temp, signature_target)

            parts = []
            if profiles:
                parts.append(f"{len(profiles)} Edge-Profil(e)")
            if signatures_exist:
                parts.append("E-Mail-Signaturen")
            message = " und ".join(parts) + " gesichert."
            self.logger.info("%s Ziel: %s", message, backup_dir)
            return {
                "success": True,
                "backed_up": True,
                "profiles": len(profiles),
                "signatures": signatures_exist,
                "message": message,
            }
        except Exception as exc:
            self.logger.error("Edge-Profile konnten nicht gesichert werden: %s", exc)
            shutil.rmtree(temporary_dir, ignore_errors=True)
            return {"success": False, "backed_up": False, "error": str(exc)}
