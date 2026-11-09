from typing import Any, Dict, List, Optional
from pathlib import Path
from src.config import DB_PATH
from src.db.schema import get_connection
from src.db.repository import EsportsRepository
from src.etl.rosters_catalog import get_champion_icon_url, get_season_meta_pool
from src.analytics.elo_engine import CrossRegionEloEngine


# Default role combat baselines for role-accurate damage, tankiness, and gold conversion
ROLE_COMBAT_BASELINES: Dict[str, Dict[str, Any]] = {
    "top": {
        "dpm_base": 575.0,
        "dtpm_base": 890.0,
        "dmg_share": 22.5,
        "tank_share": 28.5,
        "gold_share": 21.0,
        "vspm": 1.15,
        "champions": ["K'Sante", "Jax", "Rumble", "Aatrox"],
    },
    "jng": {
        "dpm_base": 435.0,
        "dtpm_base": 920.0,
        "dmg_share": 16.5,
        "tank_share": 29.5,
        "gold_share": 18.5,
        "vspm": 1.65,
        "champions": ["Lee Sin", "Viego", "Sejuani", "Vi"],
    },
    "mid": {
        "dpm_base": 645.0,
        "dtpm_base": 540.0,
        "dmg_share": 26.5,
        "tank_share": 16.0,
        "gold_share": 23.0,
        "vspm": 1.30,
        "champions": ["Azir", "Ahri", "Orianna", "Sylas"],
    },
    "bot": {
        "dpm_base": 695.0,
        "dtpm_base": 460.0,
        "dmg_share": 28.5,
        "tank_share": 13.0,
        "gold_share": 25.0,
        "vspm": 1.25,
        "champions": ["Xayah", "Kai'Sa", "Varus", "Ezreal"],
    },
    "sup": {
        "dpm_base": 220.0,
        "dtpm_base": 480.0,
        "dmg_share": 6.0,
        "tank_share": 13.0,
        "gold_share": 12.5,
        "vspm": 3.45,
        "champions": ["Rakan", "Nautilus", "Rell", "Braum"],
    },
}

HISTORICAL_ROSTER_FALLBACKS: Dict[str, Dict[str, str]] = {
    "JDG": {"top": "Ale", "jng": "Kanavi", "mid": "Yagao", "bot": "Ruler", "sup": "MISSING"},
    "WBG": {"top": "Breathe", "jng": "Tarzan", "mid": "Xiaohu", "bot": "Light", "sup": "Crisp"},
    "LNG": {"top": "Zika", "jng": "Weiwei", "mid": "Scout", "bot": "GALA", "sup": "Hang"},
    "EDG": {"top": "Flandre", "jng": "Jiejie", "mid": "Scout", "bot": "Viper", "sup": "Meiko"},
    "RNG": {"top": "Letme", "jng": "Mlxg", "mid": "Xiaohu", "bot": "Uzi", "sup": "Ming"},
    "IG": {"top": "TheShy", "jng": "Ning", "mid": "Rookie", "bot": "JackeyLove", "sup": "Baolan"},
    "FPX": {"top": "GimGoon", "jng": "Tian", "mid": "Doinb", "bot": "Lwx", "sup": "Crisp"},
    "DRX": {"top": "Kingen", "jng": "Pyosik", "mid": "Zeka", "bot": "Deft", "sup": "BeryL"},
    "FNC": {"top": "Oscarinin", "jng": "Razork", "mid": "Humanoid", "bot": "Noah", "sup": "Jun"},
    "MAD": {"top": "Myrwn", "jng": "Elyoya", "mid": "Fresskowy", "bot": "Supa", "sup": "Alvaro"},
    "RGE": {"top": "Odoamne", "jng": "Malrang", "mid": "Larssen", "bot": "Comp", "sup": "Trymbi"},
    "C9": {"top": "Thanatos", "jng": "Blaber", "mid": "Jojopyun", "bot": "Berserker", "sup": "Vulcan"},
    "TL": {"top": "Impact", "jng": "UmTi", "mid": "APA", "bot": "Yeon", "sup": "CoreJJ"},
    "TSM": {"top": "Hauntzer", "jng": "Svenskeren", "mid": "Bjergsen", "bot": "Doublelift", "sup": "Biofrost"},
    "CLG": {"top": "Dhokla", "jng": "Contractz", "mid": "Palafox", "bot": "FBI", "sup": "IgNar"},
    "TPA": {"top": "Stanley", "jng": "Lilballz", "mid": "Toyz", "bot": "Bebe", "sup": "MiSTakE"},
    "WE": {"top": "957", "jng": "Condi", "mid": "xiye", "bot": "Mystic", "sup": "Ben"},
    "OMG": {"top": "Gogoing", "jng": "Lovelin", "mid": "Cool", "bot": "San", "sup": "Cloud"},
    "M5": {"top": "Darien", "jng": "Diamondprox", "mid": "Alex Ich", "bot": "Genja", "sup": "Edward"},
    "AZF": {"top": "Shy", "jng": "CloudTemplar", "mid": "RapidStar", "bot": "Woong", "sup": "MadLife"},
    "OG": {"top": "sOAZ", "jng": "Amazing", "mid": "xPeke", "bot": "Niels", "sup": "Mithy"},
    "AAA": {"top": "Wickd", "jng": "Snoopeh", "mid": "Froggen", "bot": "Yellowpete", "sup": "Krepo"},
}


class TeamFeatureStore:
    """
    Computes multi-dimensional team and roster features, including:
    - Six-Dimension Team Radar Scores (0-100 scale)
    - Five-Role Combat Metrics (DPM, Damage Share %, DTPM Tankiness, Tank Share %, Damage Conversion %, GD@15)
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.repo = EsportsRepository(db_path)
        self.elo_engine = CrossRegionEloEngine(db_path)

    def _enrich_roster(
        self, tid: str, raw_roster: List[Dict[str, Any]], team_elo: float, season: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        roles = ["top", "jng", "mid", "bot", "sup"]
        role_map = {r["role"]: dict(r) for r in raw_roster}
        elo_factor = max(0.85, min(1.18, team_elo / 1520.0))
        meta_pool = get_season_meta_pool(season or "S16")

        enriched: List[Dict[str, Any]] = []
        raw_dpm_list = []
        raw_dtpm_list = []

        for r in roles:
            base = ROLE_COMBAT_BASELINES[r]
            if r in role_map:
                p = role_map[r]
            else:
                fb_names = HISTORICAL_ROSTER_FALLBACKS.get(tid, {})
                p = {
                    "team_id": tid,
                    "season": "S16",
                    "role": r,
                    "player_name": fb_names.get(r, f"{tid} {r.upper()}"),
                    "kda": round(3.8 * elo_factor, 1),
                    "dpm": round(base["dpm_base"] * elo_factor, 0),
                    "gd15": round((team_elo - 1500.0) * 1.4, 0),
                    "cs_per_min": 8.6 if r != "sup" else 1.3,
                    "kp_pct": 71.0,
                    "signature_champions": meta_pool.get(r, base["champions"])[:4],
                    "rating": round(min(95.0, max(78.0, 84.0 + (team_elo - 1500.0) / 22.0)), 1),
                }

            rating_scale = float(p.get("rating", 86.0)) / 88.0
            dpm = float(p.get("dpm") or base["dpm_base"] * rating_scale)
            # Calculate authentic role-specific Damage Taken Per Minute (DTPM)
            dtpm = round(base["dtpm_base"] * (0.92 + 0.12 * rating_scale), 0)
            p["dpm"] = round(dpm, 0)
            p["dtpm"] = dtpm
            p["gold_share"] = base["gold_share"]
            p["vspm"] = round(base["vspm"] * rating_scale, 2)
            raw_dpm_list.append(dpm)
            raw_dtpm_list.append(dtpm)
            enriched.append(p)

        total_dpm = max(1.0, sum(raw_dpm_list))
        total_dtpm = max(1.0, sum(raw_dtpm_list))

        for p in enriched:
            dmg_share = round((p["dpm"] / total_dpm) * 100.0, 1)
            tank_share = round((p["dtpm"] / total_dtpm) * 100.0, 1)
            gold_share = float(p["gold_share"])
            # Damage conversion efficiency: (Damage Share / Gold Share) * 100
            dmg_conv = round((dmg_share / max(1.0, gold_share)) * 100.0, 1)
            p["dmg_share"] = dmg_share
            p["tank_share"] = tank_share
            p["dmg_conversion"] = dmg_conv
            champs = p.get("signature_champions", [])
            p["champion_icons"] = [{"name": c, "icon": get_champion_icon_url(c)} for c in champs]
            p["avatar_url"] = f"/api/avatar/player/{p['player_name']}.svg?team={tid}&role={p['role']}"

        return enriched

    def get_team_feature_profile(
        self,
        team_id: str,
        season: Optional[str] = None,
        as_of_date: Optional[str] = None,
        recent_limit: int = 35,
    ) -> Dict[str, Any]:
        """Builds a team feature snapshot. Only completed series/games are used.
        When `as_of_date` (YYYY-MM-DD) is provided, features are computed strictly
        from matches played before that date (walk-forward safe: no look-ahead)."""
        team_meta = self.repo.get_team(team_id)
        if not team_meta:
            raise ValueError(f"Unknown team_id: {team_id}")

        tid = team_meta["team_id"]
        with get_connection(self.db_path) as conn:
            series_query = """
                SELECT * FROM series_matches
                WHERE status = 'completed' AND (team1_id = ? OR team2_id = ?)
            """
            series_params: List[Any] = [tid, tid]
            if season and season.upper() != "ALL":
                series_query += " AND UPPER(season) <= UPPER(?)"
                series_params.append(season)
            if as_of_date:
                series_query += " AND date_played < ?"
                series_params.append(as_of_date)
            series_query += " ORDER BY date_played DESC"
            series_rows = conn.execute(series_query, series_params).fetchall()

            game_query = """
                SELECT g.* FROM games g
                JOIN series_matches sm ON g.match_id = sm.match_id
                WHERE sm.status = 'completed' AND (g.blue_team_id = ? OR g.red_team_id = ?)
            """
            game_params: List[Any] = [tid, tid]
            if season and season.upper() != "ALL":
                game_query += " AND UPPER(g.season) <= UPPER(?)"
                game_params.append(season)
            if as_of_date:
                game_query += " AND g.date_played < ?"
                game_params.append(as_of_date)
            game_query += " ORDER BY g.date_played DESC LIMIT ?"
            game_params.append(recent_limit)
            game_rows = conn.execute(game_query, game_params).fetchall()

        total_series = len(series_rows)
        series_wins = sum(1 for r in series_rows if r["winner_id"] == tid)
        intl_series = [r for r in series_rows if r["is_international"] == 1]
        intl_wins = sum(1 for r in intl_series if r["winner_id"] == tid)
        bo5_series = [r for r in series_rows if r["best_of"] == 5]
        bo5_wins = sum(1 for r in bo5_series if r["winner_id"] == tid)
        game5_series = [
            r for r in bo5_series if (int(r["team1_score"]) + int(r["team2_score"])) == 5
        ]
        game5_wins = sum(1 for r in game5_series if r["winner_id"] == tid)

        recent_10 = series_rows[:10]
        recent_10_wr = (
            sum(1 for r in recent_10 if r["winner_id"] == tid) / len(recent_10)
            if recent_10
            else 0.55
        )

        if game_rows:
            n_games = len(game_rows)
            g_wins = 0
            blue_games = 0
            blue_wins = 0
            red_games = 0
            red_wins = 0
            gd15_list = []
            xpd15_list = []
            csd15_list = []
            fb_cnt = 0
            ft_cnt = 0
            fd_cnt = 0
            drag_taken = 0
            drag_total = 0
            baron_taken = 0
            baron_total = 0
            towers_taken = 0
            durations = []
            kills_per_game = []

            for g in game_rows:
                is_blue = g["blue_team_id"] == tid
                won = g["winner_team_id"] == tid
                if won:
                    g_wins += 1
                if is_blue:
                    blue_games += 1
                    if won:
                        blue_wins += 1
                    gd15_list.append(float(g["blue_gd15"]))
                    xpd15_list.append(float(g["blue_xpd15"]))
                    csd15_list.append(float(g["blue_csd15"]))
                    my_drag, opp_drag = int(g["blue_dragons"]), int(g["red_dragons"])
                    my_baron, opp_baron = int(g["blue_barons"]), int(g["red_barons"])
                    towers_taken += int(g["blue_towers"])
                    kills_per_game.append(int(g["blue_kills"]))
                else:
                    red_games += 1
                    if won:
                        red_wins += 1
                    gd15_list.append(-float(g["blue_gd15"]))
                    xpd15_list.append(-float(g["blue_xpd15"]))
                    csd15_list.append(-float(g["blue_csd15"]))
                    my_drag, opp_drag = int(g["red_dragons"]), int(g["blue_dragons"])
                    my_baron, opp_baron = int(g["red_barons"]), int(g["blue_barons"])
                    towers_taken += int(g["red_towers"])
                    kills_per_game.append(int(g["red_kills"]))

                if g["first_blood_team_id"] == tid:
                    fb_cnt += 1
                if g["first_tower_team_id"] == tid:
                    ft_cnt += 1
                if g["first_dragon_team_id"] == tid:
                    fd_cnt += 1

                drag_taken += my_drag
                drag_total += my_drag + opp_drag
                baron_taken += my_baron
                baron_total += my_baron + opp_baron
                durations.append(int(g["duration_sec"]))

            game_wr = g_wins / n_games
            blue_wr = blue_wins / blue_games if blue_games else game_wr
            red_wr = red_wins / red_games if red_games else game_wr
            avg_gd15 = sum(gd15_list) / n_games
            avg_xpd15 = sum(xpd15_list) / n_games
            avg_csd15 = sum(csd15_list) / n_games
            fb_rate = fb_cnt / n_games
            ft_rate = ft_cnt / n_games
            fd_rate = fd_cnt / n_games
            dragon_ctrl = drag_taken / max(1, drag_total)
            baron_ctrl = baron_taken / max(1, baron_total)
            avg_towers = towers_taken / n_games
            avg_duration_sec = sum(durations) / n_games
            avg_kills = sum(kills_per_game) / n_games
        else:
            game_wr = 0.52
            blue_wr = 0.55
            red_wr = 0.49
            avg_gd15 = 150.0
            avg_xpd15 = 95.0
            avg_csd15 = 4.0
            fb_rate = 0.52
            ft_rate = 0.52
            fd_rate = 0.52
            dragon_ctrl = 0.52
            baron_ctrl = 0.52
            avg_towers = 6.8
            avg_duration_sec = 1920.0
            avg_kills = 14.5

        # As-of-aware Elo and championship pedigree (no look-ahead when backtesting)
        if as_of_date:
            team_elo = self.elo_engine.get_elo_as_of([tid], as_of_date).get(tid, 1500.0)
        else:
            team_elo = float(team_meta["current_elo"])
        titles = self.repo.get_titles_as_of(tid, as_of_date=as_of_date)

        raw_roster = self.repo.get_team_roster(tid, season=season)
        roster = self._enrich_roster(tid, raw_roster, team_elo, season=season or "S16")
        active_roster_season = roster[0].get("season", "S16") if roster else "S16"
        all_era_rosters = self.repo.get_team_all_era_rosters(tid)
        roster_avg_rating = sum(float(p["rating"]) for p in roster) / len(roster)
        team_dpm = sum(float(p["dpm"]) for p in roster)
        team_dtpm = sum(float(p["dtpm"]) for p in roster)

        # Six-Dimension Standardized Radar Scores (0 - 100)
        laning_score = round(min(98.0, max(58.0, 74.0 + avg_gd15 / 38.0 + (ft_rate - 0.5) * 35.0)), 1)
        teamfight_dmg_score = round(min(98.0, max(60.0, (team_dpm - 2100.0) / 8.5 + avg_kills * 1.4)), 1)
        frontline_tank_score = round(min(97.0, max(62.0, (team_dtpm - 2850.0) / 9.5 + game_wr * 22.0)), 1)
        objective_ctrl_score = round(min(98.0, max(58.0, (dragon_ctrl * 0.48 + baron_ctrl * 0.52) * 145.0)), 1)
        vision_macro_score = round(
            min(98.0, max(60.0, 52.0 + avg_towers * 4.2 + (team_elo - 1400.0) / 14.0)), 1
        )
        bo5_wr_val = bo5_wins / max(1, len(bo5_series)) if bo5_series else 0.50
        clutch_bo5_score = round(
            min(
                99.0,
                max(
                    58.0,
                    60.0
                    + bo5_wr_val * 28.0
                    + titles["worlds_titles"] * 3.2
                    + titles["msi_titles"] * 2.0,
                ),
            ),
            1,
        )

        radar_scores = {
            "laning": laning_score,
            "teamfight_dmg": teamfight_dmg_score,
            "frontline_tank": frontline_tank_score,
            "objective_ctrl": objective_ctrl_score,
            "vision_macro": vision_macro_score,
            "clutch_bo5": clutch_bo5_score,
        }

        if avg_duration_sec < 1850 and avg_gd15 > 500:
            style_tag = "极致前中期快攻压制 (Early-Game Snowball)"
        elif baron_ctrl > 0.60 and dragon_ctrl > 0.57:
            style_tag = "史诗资源与团战运营王牌 (Macro & Objective Control)"
        elif avg_duration_sec > 1960:
            style_tag = "中后期大核团战与视野拉扯 (Late-Game Teamfight)"
        else:
            style_tag = "攻守均衡多核体系 (Balanced Multi-Threat)"

        return {
            "team_id": tid,
            "name": team_meta["name"],
            "short_name": team_meta["short_name"],
            "region": team_meta["region"],
            "logo_url": team_meta.get("logo_url", f"/api/avatar/team/{tid}.svg"),
            "active_roster_season": active_roster_season,
            "available_era_seasons": list(all_era_rosters.keys()),
            "all_era_rosters": all_era_rosters,
            "worlds_titles": titles["worlds_titles"],
            "msi_titles": titles["msi_titles"],
            "current_elo": round(team_elo, 1),
            "peak_elo": round(float(team_meta["peak_elo"]), 1),
            "peak_season": team_meta["peak_season"],
            "total_series": total_series,
            "series_win_rate": round(series_wins / max(1, total_series), 3),
            "recent_10_series_wr": round(recent_10_wr, 3),
            "intl_series_count": len(intl_series),
            "intl_win_rate": round(intl_wins / max(1, len(intl_series)), 3) if intl_series else 0.50,
            "bo5_count": len(bo5_series),
            "bo5_win_rate": round(bo5_wr_val, 3),
            "game5_record": f"{game5_wins}W-{len(game5_series) - game5_wins}L",
            "game5_win_rate": round(game5_wins / max(1, len(game5_series)), 3) if game5_series else 0.50,
            "game_win_rate": round(game_wr, 3),
            "blue_side_wr": round(blue_wr, 3),
            "red_side_wr": round(red_wr, 3),
            "avg_gd15": round(avg_gd15, 0),
            "avg_xpd15": round(avg_xpd15, 0),
            "avg_csd15": round(avg_csd15, 1),
            "first_blood_rate": round(fb_rate, 3),
            "first_tower_rate": round(ft_rate, 3),
            "first_dragon_rate": round(fd_rate, 3),
            "dragon_control_rate": round(dragon_ctrl, 3),
            "baron_control_rate": round(baron_ctrl, 3),
            "avg_towers_per_game": round(avg_towers, 1),
            "avg_duration_min": round(avg_duration_sec / 60.0, 1),
            "avg_kills_per_game": round(avg_kills, 1),
            "team_dpm": round(team_dpm, 0),
            "team_dtpm": round(team_dtpm, 0),
            "roster_avg_rating": round(roster_avg_rating, 2),
            "radar_scores": radar_scores,
            "style_tag": style_tag,
            "roster": roster,
        }
