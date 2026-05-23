from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class GuiStateStore:
    """Persistiert GUI-Zustand als JSON-Datei."""

    def __init__(self, state_file: Path) -> None:
        self.state_file = state_file

    def load(self) -> dict[str, Any]:
        if not self.state_file.exists():
            return {}
        try:
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save(self, data: dict[str, Any]) -> bool:
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return True
        except Exception:
            return False
