import json
from typing import Any, Dict, List, Optional
from pathlib import Path
from src.config import DB_PATH
from src.db.schema import get_connection
from src.etl.rosters_catalog import get_champion_icon_url, TEAM_BRANDING


class EsportsRepository:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def get_all_teams(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM teams"
        params: List[Any] = []
        if region and region.upper() != "ALL":
            query += " WHERE UPPER(region) = ?"
            params.append(region.upper())
        query += " ORDER BY current_elo DESC"
        with get_connection(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                d["aliases"] = json.loads(d.get("aliases_json") or "[]")
                d["logo_url"] = f"/api/avatar/team/{d['team_id']}.svg"
                d["branding"] = TEAM_BRANDING.get(d["team_id"], {})
                result.append(d)
            return result

    def get_team(self, team_id: str) -> Optional[Dict[str, Any]]:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM teams WHERE UPPER(team_id) = UPPER(?) OR UPPER(short_name) = UPPER(?) OR UPPER(name) = UPPER(?)",
                (team_id, team_id, team_id),
            ).fetchone()
            if not row:
                return None
            d = dict(row)
            d["aliases"] = json.loads(d.get("aliases_json") or "[]")
            d["logo_url"] = f"/api/avatar/team/{d['team_id']}.svg"
            d["branding"] = TEAM_BRANDING.get(d["team_id"], {})
            return d

    def get_tournaments(
        self,
        season: Optional[str] = None,
        tier: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT t.*,
                   c.name AS champion_name,
                   c.region AS champion_region,
                   ru.name AS runner_up_name,
                   ru.region AS runner_up_region,
                   (SELECT COUNT(*) FROM series_matches sm WHERE sm.tournament_id = t.tournament_id) AS match_count
            FROM tournaments t
            LEFT JOIN teams c ON t.champion_team_id = c.team_id
            LEFT JOIN teams ru ON t.runner_up_team_id = ru.team_id
            WHERE 1=1
        """
        params: List[Any] = []
        if season and season.upper() != "ALL":
            query += " AND UPPER(t.season) = ?"
            params.append(season.upper())
        if tier and tier.upper() != "ALL":
            query += " AND UPPER(t.tier) = ?"
            params.append(tier.upper())
        if region and region.upper() != "ALL":
            query += " AND UPPER(t.region) = ?"
            params.append(region.upper())
        query += " ORDER BY t.year DESC, CASE t.tier WHEN 'Worlds' THEN 1 WHEN 'MSI' THEN 2 ELSE 3 END"
        with get_connection(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_matches(
        self,
        season: Optional[str] = None,
        tournament_id: Optional[str] = None,
        team_id: Optional[str] = None,
        tier: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT sm.*,
                   t.name AS tournament_name,
                   t.tier AS tournament_tier,
                   t.region AS tournament_region,
                   t1.name AS team1_name,
                   t1.region AS team1_region,
                   t2.name AS team2_name,
                   t2.region AS team2_region
            FROM series_matches sm
            JOIN tournaments t ON sm.tournament_id = t.tournament_id
            LEFT JOIN teams t1 ON sm.team1_id = t1.team_id
            LEFT JOIN teams t2 ON sm.team2_id = t2.team_id
            WHERE 1=1
        """
        params: List[Any] = []
        if season and season.upper() != "ALL":
            query += " AND UPPER(sm.season) = ?"
            params.append(season.upper())
        if tournament_id:
            query += " AND sm.tournament_id = ?"
            params.append(tournament_id)
        if team_id:
            query += " AND (UPPER(sm.team1_id) = UPPER(?) OR UPPER(sm.team2_id) = UPPER(?))"
            params.extend([team_id, team_id])
        if tier and tier.upper() != "ALL":
            query += " AND UPPER(t.tier) = ?"
            params.append(tier.upper())
        query += " ORDER BY sm.date_played DESC, sm.match_id DESC LIMIT ?"
        params.append(limit)
        with get_connection(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_head_to_head(self, team_a: str, team_b: str, as_of_date: Optional[str] = None) -> Dict[str, Any]:
        """Head-to-head record. Only completed series count; when `as_of_date` is
        given (e.g. a walk-forward backtest), only series played strictly before
        that date are included so future results cannot leak into predictions."""
        series_where = "sm.status = 'completed'"
        series_params: List[Any] = []
        if as_of_date:
            series_where += " AND sm.date_played < ?"
            series_params.append(as_of_date)

        game_where = "1=1"
        game_params: List[Any] = []
        if as_of_date:
            game_where = "g.date_played < ?"
            game_params.append(as_of_date)

        with get_connection(self.db_path) as conn:
            series_rows = conn.execute(
                f"""
                SELECT sm.*, t.name AS tournament_name, t.tier AS tournament_tier
                FROM series_matches sm
                JOIN tournaments t ON sm.tournament_id = t.tournament_id
                WHERE ({series_where})
                  AND ((sm.team1_id = ? AND sm.team2_id = ?)
                   OR (sm.team1_id = ? AND sm.team2_id = ?))
                ORDER BY sm.date_played DESC
                """,
                series_params + [team_a, team_b, team_b, team_a],
            ).fetchall()

            game_rows = conn.execute(
                f"""
                SELECT g.*
                FROM games g
                WHERE ({game_where})
                  AND ((g.blue_team_id = ? AND g.red_team_id = ?)
                   OR (g.blue_team_id = ? AND g.red_team_id = ?))
                ORDER BY g.date_played DESC
                """,
                game_params + [team_a, team_b, team_b, team_a],
            ).fetchall()

        a_series_wins = 0
        b_series_wins = 0
        intl_a_wins = 0
        intl_b_wins = 0
        bo5_a_wins = 0
        bo5_b_wins = 0
        history_list = []

        for r in series_rows:
            d = dict(r)
            if d["winner_id"] == team_a:
                a_series_wins += 1
                if d["is_international"]:
                    intl_a_wins += 1
                if d["best_of"] == 5:
                    bo5_a_wins += 1
            else:
                b_series_wins += 1
                if d["is_international"]:
                    intl_b_wins += 1
                if d["best_of"] == 5:
                    bo5_b_wins += 1
            history_list.append(d)

        a_game_wins = sum(1 for g in game_rows if g["winner_team_id"] == team_a)
        b_game_wins = sum(1 for g in game_rows if g["winner_team_id"] == team_b)

        return {
            "team_a": team_a,
            "team_b": team_b,
            "total_series": len(series_rows),
            "team_a_series_wins": a_series_wins,
            "team_b_series_wins": b_series_wins,
            "team_a_game_wins": a_game_wins,
            "team_b_game_wins": b_game_wins,
            "international_series": intl_a_wins + intl_b_wins,
            "intl_a_wins": intl_a_wins,
            "intl_b_wins": intl_b_wins,
            "bo5_a_wins": bo5_a_wins,
            "bo5_b_wins": bo5_b_wins,
            "recent_Encounters": history_list[:10],
        }

    def get_titles_as_of(
        self, team_id: str, as_of_date: Optional[str] = None
    ) -> Dict[str, int]:
        """Worlds/MSI titles won strictly before `as_of_date` (None = all concluded
        tournaments). A title only counts once its deciding final has been played,
        so an ongoing tournament never contributes pedigree weight."""
        cutoff = ""
        params: List[Any] = [team_id]
        if as_of_date:
            cutoff = """
                AND (SELECT MAX(sm.date_played) FROM series_matches sm
                     WHERE sm.tournament_id = t.tournament_id) < ?
            """
            params.append(as_of_date)

        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                f"""
                SELECT t.tier, COUNT(*) AS cnt
                FROM tournaments t
                WHERE t.champion_team_id = ?
                  AND t.tier IN ('Worlds', 'MSI')
                  {cutoff}
                GROUP BY t.tier
                """,
                params,
            ).fetchall()
        titles = {r["tier"]: int(r["cnt"]) for r in rows}
        return {
            "worlds_titles": titles.get("Worlds", 0),
            "msi_titles": titles.get("MSI", 0),
        }

    def get_team_roster(self, team_id: str, season: Optional[str] = None) -> List[Dict[str, Any]]:
        with get_connection(self.db_path) as conn:
            if season and season.upper() != "ALL":
                rows = conn.execute(
                    """
                    SELECT * FROM player_rosters
                    WHERE team_id = ? AND UPPER(season) = UPPER(?)
                    ORDER BY CASE role
                        WHEN 'top' THEN 1
                        WHEN 'jng' THEN 2
                        WHEN 'mid' THEN 3
                        WHEN 'bot' THEN 4
                        WHEN 'sup' THEN 5
                        ELSE 6 END
                    """,
                    (team_id, season),
                ).fetchall()
                if rows:
                    return [self._parse_roster_row(r) for r in rows]

                # Closest era <= requested season
                try:
                    target_num = int(season.upper().lstrip("S"))
                    closest = conn.execute(
                        """
                        SELECT season FROM player_rosters
                        WHERE team_id = ?
                        ORDER BY ABS(CAST(SUBSTR(season, 2) AS INTEGER) - ?) ASC,
                                 CAST(SUBSTR(season, 2) AS INTEGER) DESC
                        LIMIT 1
                        """,
                        (team_id, target_num),
                    ).fetchone()
                    if closest:
                        rows = conn.execute(
                            """
                            SELECT * FROM player_rosters
                            WHERE team_id = ? AND season = ?
                            ORDER BY CASE role
                                WHEN 'top' THEN 1
                                WHEN 'jng' THEN 2
                                WHEN 'mid' THEN 3
                                WHEN 'bot' THEN 4
                                WHEN 'sup' THEN 5
                                ELSE 6 END
                            """,
                            (team_id, closest["season"]),
                        ).fetchall()
                        if rows:
                            return [self._parse_roster_row(r) for r in rows]
                except ValueError:
                    pass

            # Fallback to latest available season for this team
            latest = conn.execute(
                """
                SELECT season FROM player_rosters
                WHERE team_id = ?
                ORDER BY CAST(SUBSTR(season, 2) AS INTEGER) DESC
                LIMIT 1
                """,
                (team_id,),
            ).fetchone()
            if not latest:
                return []
            rows = conn.execute(
                """
                SELECT * FROM player_rosters
                WHERE team_id = ? AND season = ?
                ORDER BY CASE role
                    WHEN 'top' THEN 1
                    WHEN 'jng' THEN 2
                    WHEN 'mid' THEN 3
                    WHEN 'bot' THEN 4
                    WHEN 'sup' THEN 5
                    ELSE 6 END
                """,
                (team_id, latest["season"]),
            ).fetchall()
            return [self._parse_roster_row(r) for r in rows]

    def get_team_all_era_rosters(self, team_id: str) -> Dict[str, List[Dict[str, Any]]]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM player_rosters
                WHERE team_id = ?
                ORDER BY CAST(SUBSTR(season, 2) AS INTEGER) DESC,
                         CASE role
                             WHEN 'top' THEN 1
                             WHEN 'jng' THEN 2
                             WHEN 'mid' THEN 3
                             WHEN 'bot' THEN 4
                             WHEN 'sup' THEN 5
                             ELSE 6 END
                """,
                (team_id,),
            ).fetchall()
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for r in rows:
            parsed = self._parse_roster_row(r)
            s = parsed["season"]
            grouped.setdefault(s, []).append(parsed)
        return grouped

    @staticmethod
    def _parse_roster_row(row: Any) -> Dict[str, Any]:
        d = dict(row)
        champs = json.loads(d.get("signature_champions_json") or "[]")
        d["signature_champions"] = champs
        d["champion_icons"] = [{"name": c, "icon": get_champion_icon_url(c)} for c in champs]
        d["avatar_url"] = f"/api/avatar/player/{d['player_name']}.svg?team={d['team_id']}&role={d['role']}"
        return d

    def get_team_elo_trajectory(self, team_id: str) -> List[Dict[str, Any]]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT eh.*, sm.stage, sm.tournament_id
                FROM elo_history eh
                LEFT JOIN series_matches sm ON eh.match_id = sm.match_id
                WHERE eh.team_id = ?
                ORDER BY eh.date_played ASC, eh.id ASC
                """,
                (team_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_database_summary(self) -> Dict[str, Any]:
        with get_connection(self.db_path) as conn:
            teams_cnt = conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
            tourn_cnt = conn.execute("SELECT COUNT(*) FROM tournaments").fetchone()[0]
            series_cnt = conn.execute("SELECT COUNT(*) FROM series_matches").fetchone()[0]
            games_cnt = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
            players_cnt = conn.execute("SELECT COUNT(*) FROM player_rosters").fetchone()[0]
            seasons = conn.execute(
                "SELECT DISTINCT season FROM tournaments ORDER BY CAST(SUBSTR(season, 2) AS INTEGER) ASC"
            ).fetchall()
            return {
                "teams_count": teams_cnt,
                "tournaments_count": tourn_cnt,
                "series_count": series_cnt,
                "games_count": games_cnt,
                "rosters_count": players_cnt,
                "seasons_covered": [r[0] for r in seasons],
            }
