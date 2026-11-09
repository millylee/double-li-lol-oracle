import math
from typing import Any, Dict, List
from pathlib import Path
from src.config import DB_PATH, REGION_BASE_ELO
from src.db.schema import get_connection


class CrossRegionEloEngine:
    """
    Chronological S1-S16 Elo & Regional Strength Calibration Engine.
    Accounts for tournament tier (Worlds, MSI, Regional), stage weight, margin of victory (3-0 vs 3-2),
    and inter-season soft mean reversion toward dynamically calibrated regional baselines.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    @staticmethod
    def expected_score(elo_a: float, elo_b: float) -> float:
        return 1.0 / (1.0 + math.pow(10.0, (elo_b - elo_a) / 400.0))

    @staticmethod
    def k_factor(is_international: int, stage: str, best_of: int) -> float:
        stage_lower = stage.lower()
        if is_international:
            if "final" in stage_lower and "semi" not in stage_lower and "quarter" not in stage_lower:
                base_k = 46.0
            elif "semi" in stage_lower or "winner" in stage_lower or "loser" in stage_lower:
                base_k = 40.0
            else:
                base_k = 34.0
        else:
            if "final" in stage_lower:
                base_k = 30.0
            elif "playoff" in stage_lower:
                base_k = 26.0
            else:
                base_k = 20.0

        if best_of >= 5:
            return base_k * 1.15
        if best_of == 3:
            return base_k * 1.0
        return base_k * 0.75

    def get_elo_as_of(self, team_ids: List[str], as_of_date: str) -> Dict[str, float]:
        """Returns each team's Elo strictly before `as_of_date` (walk-forward safe),
        reconstructed from the chronological elo_history. Teams without any prior
        match fall back to their region base rating."""
        result: Dict[str, float] = {}
        with get_connection(self.db_path) as conn:
            region_rows = conn.execute("SELECT team_id, region FROM teams").fetchall()
            team_region = {r["team_id"]: r["region"] for r in region_rows}
            base = dict(REGION_BASE_ELO)

            for tid in team_ids:
                row = conn.execute(
                    """
                    SELECT elo_after FROM elo_history
                    WHERE team_id = ? AND date_played < ?
                    ORDER BY date_played DESC, id DESC LIMIT 1
                    """,
                    (tid, as_of_date),
                ).fetchone()
                if row:
                    result[tid] = float(row["elo_after"])
                else:
                    # No match before the cutoff: fall back to regional base Elo
                    first = conn.execute(
                        """
                        SELECT elo_before FROM elo_history WHERE team_id = ?
                        ORDER BY date_played ASC, id ASC LIMIT 1
                        """,
                        (tid,),
                    ).fetchone()
                    result[tid] = float(first["elo_before"]) if first else base.get(
                        team_region.get(tid, "OTHER"), 1450.0
                    )
        return result

    def recompute_all_ratings(self) -> Dict[str, Any]:
        with get_connection(self.db_path) as conn:
            teams_rows = conn.execute("SELECT team_id, region FROM teams").fetchall()
            team_region: Dict[str, str] = {r["team_id"]: r["region"] for r in teams_rows}

            region_ratings: Dict[str, float] = dict(REGION_BASE_ELO)
            team_elos: Dict[str, float] = {
                tid: region_ratings.get(reg, 1450.0) for tid, reg in team_region.items()
            }
            peak_elos: Dict[str, float] = dict(team_elos)
            peak_seasons: Dict[str, str] = {tid: "S1" for tid in team_region}

            matches = conn.execute(
                """
                SELECT match_id, season, year, date_played, stage, best_of,
                       team1_id, team2_id, team1_score, team2_score, winner_id, is_international
                FROM series_matches
                WHERE status = 'completed'
                ORDER BY date_played ASC, match_id ASC
                """
            ).fetchall()

            conn.execute("DELETE FROM elo_history")
            current_season = None
            active_in_season = set()
            history_records = []

            for m in matches:
                # Defensive guard: skip any row without a valid winner (scheduled fixtures)
                if m["winner_id"] not in (m["team1_id"], m["team2_id"]):
                    continue
                season = m["season"]
                # Apply soft inter-season mean reversion when transitioning to a new season
                if current_season is not None and season != current_season:
                    for tid in list(team_elos.keys()):
                        reg = team_region.get(tid, "OTHER")
                        reg_anchor = region_ratings.get(reg, 1450.0)
                        if tid in active_in_season:
                            team_elos[tid] = round(0.76 * team_elos[tid] + 0.24 * reg_anchor, 2)
                        else:
                            team_elos[tid] = round(0.70 * team_elos[tid] + 0.30 * 1450.0, 2)
                    active_in_season.clear()
                current_season = season

                t1 = m["team1_id"]
                t2 = m["team2_id"]
                active_in_season.add(t1)
                active_in_season.add(t2)
                if t1 not in team_elos:
                    team_elos[t1] = 1450.0
                    peak_elos[t1] = 1450.0
                    peak_seasons[t1] = season
                if t2 not in team_elos:
                    team_elos[t2] = 1450.0
                    peak_elos[t2] = 1450.0
                    peak_seasons[t2] = season

                elo1_before = team_elos[t1]
                elo2_before = team_elos[t2]

                exp1 = self.expected_score(elo1_before, elo2_before)
                exp2 = 1.0 - exp1

                s1, s2 = int(m["team1_score"]), int(m["team2_score"])
                total_g = max(1, s1 + s2)
                # Blend binary series win (75%) with game win share (25%) for smooth MOV scaling
                actual1 = 0.75 * (1.0 if m["winner_id"] == t1 else 0.0) + 0.25 * (s1 / total_g)
                actual2 = 1.0 - actual1

                k = self.k_factor(int(m["is_international"]), m["stage"], int(m["best_of"]))
                delta1 = round(k * (actual1 - exp1), 2)
                delta2 = round(k * (actual2 - exp2), 2)

                elo1_after = round(elo1_before + delta1, 2)
                elo2_after = round(elo2_before + delta2, 2)

                team_elos[t1] = elo1_after
                team_elos[t2] = elo2_after

                if elo1_after >= peak_elos.get(t1, 0.0):
                    peak_elos[t1] = elo1_after
                    peak_seasons[t1] = season
                if elo2_after >= peak_elos.get(t2, 0.0):
                    peak_elos[t2] = elo2_after
                    peak_seasons[t2] = season

                # Cross-region international calibration
                reg1 = team_region.get(t1, "OTHER")
                reg2 = team_region.get(t2, "OTHER")
                if m["is_international"] and reg1 != reg2:
                    reg_shift = 0.12 * delta1
                    region_ratings[reg1] = round(region_ratings.get(reg1, 1450.0) + reg_shift, 2)
                    region_ratings[reg2] = round(region_ratings.get(reg2, 1450.0) - reg_shift, 2)

                history_records.append(
                    (
                        m["match_id"],
                        m["date_played"],
                        season,
                        t1,
                        elo1_before,
                        elo1_after,
                        t2,
                        m["is_international"],
                        m["stage"],
                    )
                )
                history_records.append(
                    (
                        m["match_id"],
                        m["date_played"],
                        season,
                        t2,
                        elo2_before,
                        elo2_after,
                        t1,
                        m["is_international"],
                        m["stage"],
                    )
                )

            conn.executemany(
                """
                INSERT INTO elo_history
                (match_id, date_played, season, team_id, elo_before, elo_after, opponent_id, is_international, stage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                history_records,
            )

            for tid, cur_elo in team_elos.items():
                conn.execute(
                    """
                    UPDATE teams
                    SET current_elo = ?, peak_elo = ?, peak_season = ?
                    WHERE team_id = ?
                    """,
                    (cur_elo, peak_elos.get(tid, cur_elo), peak_seasons.get(tid, "S16"), tid),
                )

            conn.commit()

        top_teams = sorted(team_elos.items(), key=lambda x: x[1], reverse=True)[:10]
        return {
            "matches_processed": len(matches),
            "history_entries": len(history_records),
            "calibrated_region_ratings": region_ratings,
            "top_10_elo": [{"team_id": k, "elo": v, "peak_elo": peak_elos[k]} for k, v in top_teams],
        }
