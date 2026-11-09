import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from src.config import TEAM_ALIASES_PATH


class TeamNormalizer:
    """Normalizes historical LoL team names (S1-S16) to canonical team IDs."""

    def __init__(self, aliases_path: Path = TEAM_ALIASES_PATH):
        self.aliases_path = aliases_path
        self.teams_by_id: Dict[str, Dict[str, Any]] = {}
        self.alias_to_id: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if not self.aliases_path.exists():
            return
        data = json.loads(self.aliases_path.read_text(encoding="utf-8"))
        for entry in data.get("teams", []):
            tid = entry["team_id"].upper()
            self.teams_by_id[tid] = entry
            self.alias_to_id[self._clean(tid)] = tid
            self.alias_to_id[self._clean(entry["name"])] = tid
            self.alias_to_id[self._clean(entry["short_name"])] = tid
            for alias in entry.get("aliases", []):
                self.alias_to_id[self._clean(alias)] = tid

    @staticmethod
    def _clean(name: str) -> str:
        return re.sub(r"[^a-z0-9]", "", name.lower().strip())

    def resolve(self, raw_name: str, default_region: str = "OTHER") -> Tuple[str, Dict[str, Any]]:
        """Returns (canonical_team_id, team_metadata_dict)."""
        cleaned = self._clean(raw_name)
        if cleaned in self.alias_to_id:
            tid = self.alias_to_id[cleaned]
            return tid, self.teams_by_id[tid]

        # Dynamic fallback for unmapped teams
        short = re.sub(r"[^A-Za-z0-9]", "", raw_name.upper())[:6] or "UNK"
        meta = {
            "team_id": short,
            "name": raw_name.strip(),
            "short_name": short[:4],
            "region": default_region,
            "founded_season": "S1",
            "worlds_titles": 0,
            "msi_titles": 0,
            "aliases": [raw_name.strip()],
        }
        self.teams_by_id[short] = meta
        self.alias_to_id[cleaned] = short
        return short, meta

    def all_canonical_teams(self) -> List[Dict[str, Any]]:
        return list(self.teams_by_id.values())
