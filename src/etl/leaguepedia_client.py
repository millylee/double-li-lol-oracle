import json
import time
from typing import Any, Dict, List, Optional
import httpx
from src.config import LEAGUEPEDIA_API_URL, LEAGUEPEDIA_USER_AGENT, RAW_DATA_DIR, YEAR_SEASON_MAP
from src.db.schema import get_connection
from src.etl.team_normalizer import TeamNormalizer


class LeaguepediaClient:
    """
    Fetches historical and modern match schedules, series results, and game scoreboards
    from Leaguepedia's MediaWiki Cargo API (covering S1-S16 Worlds, MSI, LCK, LPL, LEC, LCS).
    """

    def __init__(self, normalizer: Optional[TeamNormalizer] = None):
        self.api_url = LEAGUEPEDIA_API_URL
        self.headers = {
            "User-Agent": LEAGUEPEDIA_USER_AGENT,
            "Accept": "application/json",
        }
        self.normalizer = normalizer or TeamNormalizer()
        self.cache_dir = RAW_DATA_DIR / "leaguepedia"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def cargo_query(
        self,
        tables: str,
        fields: str,
        where: str = "",
        join_on: str = "",
        order_by: str = "",
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "action": "cargoquery",
            "format": "json",
            "tables": tables,
            "fields": fields,
            "limit": limit,
        }
        if where:
            params["where"] = where
        if join_on:
            params["join_on"] = join_on
        if order_by:
            params["order_by"] = order_by

        with httpx.Client(headers=self.headers, timeout=25.0, follow_redirects=True) as client:
            resp = client.get(self.api_url, params=params)
            resp.raise_for_status()
            payload = resp.json()
            rows = payload.get("cargoquery", [])
            return [item.get("title", {}) for item in rows]

    def fetch_tournament_matches(self, overview_page: str, limit: int = 200) -> List[Dict[str, Any]]:
        """
        Queries MatchSchedule table from Leaguepedia for a given tournament overview page
        (e.g., '2024 Season World Championship/Main Event' or 'Season 3 World Championship').
        """
        cache_file = self.cache_dir / f"{overview_page.replace('/', '_').replace(' ', '_')}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text(encoding="utf-8"))

        where_clause = f'OverviewPage="{overview_page}" AND Team1 IS NOT NULL AND Team2 IS NOT NULL'
        fields = (
            "MatchId,OverviewPage,Team1,Team2,Team1Score,Team2Score,Winner,"
            "DateTime_UTC,BestOf,Tab,Patch"
        )
        results = self.cargo_query(
            tables="MatchSchedule",
            fields=fields,
            where=where_clause,
            order_by="DateTime_UTC ASC",
            limit=limit,
        )
        if results:
            cache_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        return results

    def sync_tournament_from_leaguepedia(
        self,
        overview_page: str,
        tournament_id: str,
        tournament_name: str,
        season: str,
        year: int,
        tier: str = "Worlds",
        region: str = "GLOBAL",
    ) -> Dict[str, Any]:
        """Fetches series matches from Leaguepedia Cargo API and upserts them into SQLite."""
        raw_matches = self.fetch_tournament_matches(overview_page)
        inserted_series = 0

        with get_connection() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO tournaments
                (tournament_id, name, season, year, tier, region, split)
                VALUES (?, ?, ?, ?, ?, ?, 'Main')
                """,
                (tournament_id, tournament_name, season, year, tier, region),
            )

            for idx, m in enumerate(raw_matches):
                t1_raw = (m.get("Team1") or "").strip()
                t2_raw = (m.get("Team2") or "").strip()
                if not t1_raw or not t2_raw or t1_raw.upper() == "TBD" or t2_raw.upper() == "TBD":
                    continue

                try:
                    s1 = int(m.get("Team1Score") or 0)
                    s2 = int(m.get("Team2Score") or 0)
                except ValueError:
                    continue
                if s1 == 0 and s2 == 0:
                    continue

                t1_id, t1_meta = self.normalizer.resolve(t1_raw, default_region=region if region != "GLOBAL" else "OTHER")
                t2_id, t2_meta = self.normalizer.resolve(t2_raw, default_region=region if region != "GLOBAL" else "OTHER")

                for tid, meta in [(t1_id, t1_meta), (t2_id, t2_meta)]:
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

                winner_id = t1_id if s1 >= s2 else t2_id
                date_str = (m.get("DateTime UTC") or m.get("DateTime_UTC") or f"{year}-10-15")[:10]
                best_of = int(m.get("BestOf") or (5 if max(s1, s2) == 3 else (3 if max(s1, s2) == 2 else 1)))
                stage = m.get("Tab") or "Main Stage"
                patch = m.get("Patch") or ""
                match_id = f"LP_{tournament_id}_{idx+1}"

                conn.execute(
                    """
                    INSERT OR REPLACE INTO series_matches
                    (match_id, tournament_id, season, year, date_played, stage, best_of,
                     team1_id, team2_id, team1_raw_name, team2_raw_name,
                     team1_score, team2_score, winner_id, patch, is_international, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'leaguepedia')
                    """,
                    (
                        match_id,
                        tournament_id,
                        season,
                        year,
                        date_str,
                        stage,
                        best_of,
                        t1_id,
                        t2_id,
                        t1_raw,
                        t2_raw,
                        s1,
                        s2,
                        winner_id,
                        patch,
                        1 if tier in ("Worlds", "MSI") else 0,
                    ),
                )
                inserted_series += 1

            conn.commit()

        return {
            "overview_page": overview_page,
            "tournament_id": tournament_id,
            "fetched_count": len(raw_matches),
            "inserted_series": inserted_series,
        }
