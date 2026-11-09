import json
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
from src.config import YEAR_SEASON_MAP
from src.db.schema import get_connection
from src.etl.team_normalizer import TeamNormalizer


SUPPORTED_LEAGUES = {
    "WLDS": ("Worlds", "GLOBAL"),
    "WCS": ("Worlds", "GLOBAL"),
    "MSI": ("MSI", "GLOBAL"),
    "LCK": ("Regional", "LCK"),
    "OGN": ("Regional", "LCK"),
    "LPL": ("Regional", "LPL"),
    "LEC": ("Regional", "LEC"),
    "EULCS": ("Regional", "LEC"),
    "EU LCS": ("Regional", "LEC"),
    "LCS": ("Regional", "LCS"),
    "NALCS": ("Regional", "LCS"),
    "NA LCS": ("Regional", "LCS"),
    "LTA": ("Regional", "LCS"),
}


class OraclesElixirImporter:
    """
    Imports Oracle's Elixir match/player CSV files (2014/S4 - 2026/S16) into the SQLite database.
    Extracts both game-level advanced metrics (GD@15, XPD@15, CSD@15, dragons, barons, towers, picks/bans)
    and aggregated series matches across Worlds, MSI, LCK, LPL, LEC, and LCS.
    """

    def __init__(self, normalizer: Optional[TeamNormalizer] = None):
        self.normalizer = normalizer or TeamNormalizer()

    def import_csv(self, csv_path: Path, filter_major_leagues: bool = True) -> Dict[str, Any]:
        if not csv_path.exists():
            raise FileNotFoundError(f"Oracle's Elixir CSV not found: {csv_path}")

        df = pd.read_csv(csv_path, low_memory=False)
        if filter_major_leagues and "league" in df.columns:
            df["league_upper"] = df["league"].astype(str).str.upper().str.strip()
            df = df[df["league_upper"].isin(SUPPORTED_LEAGUES.keys())].copy()

        # Team rows in Oracle's Elixir have participantid 100 (Blue) and 200 (Red) or position == 'team'
        if "position" in df.columns:
            team_df = df[df["position"].astype(str).str.lower() == "team"].copy()
        else:
            team_df = df[df["participantid"].isin([100, 200])].copy()

        games_imported = 0
        series_grouped: Dict[str, Any] = {}

        with get_connection() as conn:
            for game_id, group in team_df.groupby("gameid"):
                if len(group) < 2:
                    continue

                blue_rows = group[group["side"].astype(str).str.lower() == "blue"]
                red_rows = group[group["side"].astype(str).str.lower() == "red"]
                if blue_rows.empty or red_rows.empty:
                    blue_row = group.iloc[0]
                    red_row = group.iloc[1]
                else:
                    blue_row = blue_rows.iloc[0]
                    red_row = red_rows.iloc[0]

                year = int(blue_row.get("year") or 2024)
                season = YEAR_SEASON_MAP.get(year, f"S{max(1, year - 2010)}")
                league_code = str(blue_row.get("league") or "LCK").upper().strip()
                tier, region = SUPPORTED_LEAGUES.get(league_code, ("Regional", league_code))
                split = str(blue_row.get("split") or "Main")
                tournament_id = f"OE_{season}_{league_code}_{split}".upper().replace(" ", "_")

                blue_raw = str(blue_row.get("teamname") or "Blue Team")
                red_raw = str(red_row.get("teamname") or "Red Team")
                blue_id, blue_meta = self.normalizer.resolve(
                    blue_raw, default_region=region if region != "GLOBAL" else "OTHER"
                )
                red_id, red_meta = self.normalizer.resolve(
                    red_raw, default_region=region if region != "GLOBAL" else "OTHER"
                )

                for tid, meta in [(blue_id, blue_meta), (red_id, red_meta)]:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO teams (team_id, name, short_name, region, founded_season, aliases_json)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            tid,
                            meta["name"],
                            meta["short_name"],
                            meta["region"],
                            meta.get("founded_season", season),
                            json.dumps(meta.get("aliases", []), ensure_ascii=False),
                        ),
                    )

                conn.execute(
                    """
                    INSERT OR IGNORE INTO tournaments (tournament_id, name, season, year, tier, region, split)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tournament_id,
                        f"{year} {league_code} {split}",
                        season,
                        year,
                        tier,
                        region,
                        split,
                    ),
                )

                date_str = str(blue_row.get("date") or f"{year}-06-01")[:10]
                game_num = int(blue_row.get("game") or 1)
                blue_win = int(blue_row.get("result") or 0) == 1
                winner_id = blue_id if blue_win else red_id
                duration_sec = int(float(blue_row.get("gamelength") or 1900))
                patch = str(blue_row.get("patch") or "")

                pair_key = "_".join(sorted([blue_id, red_id]))
                match_id = f"OE_SER_{tournament_id}_{date_str}_{pair_key}"

                blue_bans = [
                    str(blue_row.get(f"ban{i}"))
                    for i in range(1, 6)
                    if pd.notna(blue_row.get(f"ban{i}"))
                ]
                red_bans = [
                    str(red_row.get(f"ban{i}"))
                    for i in range(1, 6)
                    if pd.notna(red_row.get(f"ban{i}"))
                ]
                blue_picks = [
                    str(blue_row.get(f"pick{i}"))
                    for i in range(1, 6)
                    if pd.notna(blue_row.get(f"pick{i}"))
                ]
                red_picks = [
                    str(red_row.get(f"pick{i}"))
                    for i in range(1, 6)
                    if pd.notna(red_row.get(f"pick{i}"))
                ]

                conn.execute(
                    """
                    INSERT OR REPLACE INTO games (
                        game_id, match_id, tournament_id, season, year, date_played, game_number,
                        blue_team_id, red_team_id, winner_team_id, duration_sec, patch,
                        blue_kills, red_kills, blue_gold, red_gold,
                        blue_gd15, blue_xpd15, blue_csd15,
                        first_blood_team_id, first_tower_team_id, first_dragon_team_id,
                        blue_dragons, red_dragons, blue_barons, red_barons, blue_towers, red_towers,
                        blue_bans_json, red_bans_json, blue_picks_json, red_picks_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(game_id),
                        match_id,
                        tournament_id,
                        season,
                        year,
                        date_str,
                        game_num,
                        blue_id,
                        red_id,
                        winner_id,
                        duration_sec,
                        patch,
                        int(float(blue_row.get("kills") or 0)),
                        int(float(red_row.get("kills") or 0)),
                        int(float(blue_row.get("totalgold") or 0)),
                        int(float(red_row.get("totalgold") or 0)),
                        float(blue_row.get("golddiffat15") or 0.0),
                        float(blue_row.get("xpdiffat15") or 0.0),
                        float(blue_row.get("csdiffat15") or 0.0),
                        blue_id if float(blue_row.get("firstblood") or 0) == 1 else red_id,
                        blue_id if float(blue_row.get("firsttower") or 0) == 1 else red_id,
                        blue_id if float(blue_row.get("firstdragon") or 0) == 1 else red_id,
                        int(float(blue_row.get("dragons") or 0)),
                        int(float(red_row.get("dragons") or 0)),
                        int(float(blue_row.get("barons") or 0)),
                        int(float(red_row.get("barons") or 0)),
                        int(float(blue_row.get("towers") or 0)),
                        int(float(red_row.get("towers") or 0)),
                        json.dumps(blue_bans, ensure_ascii=False),
                        json.dumps(red_bans, ensure_ascii=False),
                        json.dumps(blue_picks, ensure_ascii=False),
                        json.dumps(red_picks, ensure_ascii=False),
                    ),
                )
                games_imported += 1

                if match_id not in series_grouped:
                    series_grouped[match_id] = {
                        "match_id": match_id,
                        "tournament_id": tournament_id,
                        "season": season,
                        "year": year,
                        "date_played": date_str,
                        "stage": "Playoffs" if int(float(blue_row.get("playoffs") or 0)) == 1 else "Regular Season",
                        "team1_id": blue_id,
                        "team2_id": red_id,
                        "team1_raw_name": blue_raw,
                        "team2_raw_name": red_raw,
                        "team1_score": 0,
                        "team2_score": 0,
                        "patch": patch,
                        "is_international": 1 if tier in ("Worlds", "MSI") else 0,
                    }
                if winner_id == series_grouped[match_id]["team1_id"]:
                    series_grouped[match_id]["team1_score"] += 1
                else:
                    series_grouped[match_id]["team2_score"] += 1

            for m_id, sdata in series_grouped.items():
                s1 = sdata["team1_score"]
                s2 = sdata["team2_score"]
                max_s = max(s1, s2)
                best_of = 5 if max_s >= 3 else (3 if max_s == 2 else 1)
                winner_id = sdata["team1_id"] if s1 >= s2 else sdata["team2_id"]
                conn.execute(
                    """
                    INSERT OR REPLACE INTO series_matches (
                        match_id, tournament_id, season, year, date_played, stage, best_of,
                        team1_id, team2_id, team1_raw_name, team2_raw_name,
                        team1_score, team2_score, winner_id, patch, is_international, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'oracles_elixir')
                    """,
                    (
                        m_id,
                        sdata["tournament_id"],
                        sdata["season"],
                        sdata["year"],
                        sdata["date_played"],
                        sdata["stage"],
                        best_of,
                        sdata["team1_id"],
                        sdata["team2_id"],
                        sdata["team1_raw_name"],
                        sdata["team2_raw_name"],
                        s1,
                        s2,
                        winner_id,
                        sdata["patch"],
                        sdata["is_international"],
                    ),
                )

            conn.commit()

        return {
            "csv_path": str(csv_path),
            "games_imported": games_imported,
            "series_imported": len(series_grouped),
        }
