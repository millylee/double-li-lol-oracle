from typing import Any, Dict, List, Optional
from pathlib import Path
from src.config import DB_PATH
from src.db.repository import EsportsRepository
from src.analytics.ml_predictor import QuantitativeMatchPredictor
from src.analytics.feature_store import TeamFeatureStore


class AgentToolbox:
    """
    Provides structured analytical tools invoked by the Multi-Agent Predictor
    during match analysis.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.repo = EsportsRepository(db_path)
        self.quant = QuantitativeMatchPredictor(db_path)
        self.feature_store = TeamFeatureStore(db_path)

    def tool_quant_baseline_and_pace(
        self,
        team_a: str,
        team_b: str,
        best_of: int = 5,
        stage: str = "Worlds Knockout BO5",
        season: Optional[str] = None,
        season_a: Optional[str] = None,
        season_b: Optional[str] = None,
        blue_side_team: Optional[str] = None,
        as_of_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Tool 1: Runs the quantitative Elo + ML + Markov series simulator and extracts pace/macro metrics."""
        return self.quant.predict_matchup(
            team_a_id=team_a,
            team_b_id=team_b,
            best_of=best_of,
            stage=stage,
            season=season,
            season_a=season_a,
            season_b=season_b,
            blue_side_team=blue_side_team,
            as_of_date=as_of_date,
        )

    def tool_h2h_and_pedigree(
        self, team_a: str, team_b: str, as_of_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Tool 2: Queries historical Head-to-Head series/games and international knockout pedigree."""

        def pedigree(team_id: str) -> Dict[str, Any]:
            meta = self.repo.get_team(team_id) or {}
            titles = self.repo.get_titles_as_of(team_id, as_of_date=as_of_date)
            return {
                "team_id": meta.get("team_id"),
                "name": meta.get("name"),
                "region": meta.get("region"),
                "worlds_titles": titles["worlds_titles"],
                "msi_titles": titles["msi_titles"],
                "peak_elo": meta.get("peak_elo", 1500),
                "peak_season": meta.get("peak_season", "S1"),
            }

        h2h = self.repo.get_head_to_head(team_a, team_b, as_of_date=as_of_date)
        return {
            "h2h": h2h,
            "team_a_pedigree": pedigree(team_a),
            "team_b_pedigree": pedigree(team_b),
        }

    def tool_roster_and_bp_clash(
        self,
        team_a: str,
        team_b: str,
        season: Optional[str] = None,
        season_a: Optional[str] = None,
        season_b: Optional[str] = None,
        as_of_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Tool 3: Compares 5-man starting rosters role-by-role (including DPM, DTPM, DMG%, TANK%, Conversion) and identifies contested BP champions."""
        prof_a = self.feature_store.get_team_feature_profile(
            team_a, season=season_a or season or "S16", as_of_date=as_of_date
        )
        prof_b = self.feature_store.get_team_feature_profile(
            team_b, season=season_b or season or "S16", as_of_date=as_of_date
        )

        roster_a = {p["role"]: p for p in prof_a["roster"]}
        roster_b = {p["role"]: p for p in prof_b["roster"]}

        roles = ["top", "jng", "mid", "bot", "sup"]
        role_labels = {
            "top": "上单 (Top)",
            "jng": "打野 (Jungle)",
            "mid": "中单 (Mid)",
            "bot": "下路 (Bot/ADC)",
            "sup": "辅助 (Support)",
        }

        lane_comparisons: List[Dict[str, Any]] = []
        contested_picks: List[Dict[str, str]] = []

        for r in roles:
            pa = roster_a.get(r)
            pb = roster_b.get(r)
            if not pa or not pb:
                continue

            overlap = sorted(set(pa.get("signature_champions", [])) & set(pb.get("signature_champions", [])))
            for ch in overlap:
                contested_picks.append({"role": role_labels[r], "champion": ch})

            rating_diff = round(float(pa["rating"]) - float(pb["rating"]), 1)
            gd15_diff = round(float(pa["gd15"]) - float(pb["gd15"]), 0)

            lane_comparisons.append(
                {
                    "role": r,
                    "role_label": role_labels[r],
                    "player_a": pa["player_name"],
                    "player_b": pb["player_name"],
                    "avatar_a": pa.get("avatar_url", ""),
                    "avatar_b": pb.get("avatar_url", ""),
                    "season_a": pa.get("season", "S16"),
                    "season_b": pb.get("season", "S16"),
                    "rating_a": pa["rating"],
                    "rating_b": pb["rating"],
                    "rating_diff": rating_diff,
                    "kda_a": pa["kda"],
                    "kda_b": pb["kda"],
                    "dpm_a": pa["dpm"],
                    "dpm_b": pb["dpm"],
                    "dtpm_a": pa["dtpm"],
                    "dtpm_b": pb["dtpm"],
                    "dmg_share_a": pa["dmg_share"],
                    "dmg_share_b": pb["dmg_share"],
                    "tank_share_a": pa["tank_share"],
                    "tank_share_b": pb["tank_share"],
                    "dmg_conv_a": pa["dmg_conversion"],
                    "dmg_conv_b": pb["dmg_conversion"],
                    "vspm_a": pa["vspm"],
                    "vspm_b": pb["vspm"],
                    "gd15_a": pa["gd15"],
                    "gd15_b": pb["gd15"],
                    "gd15_diff": gd15_diff,
                    "champions_a": pa.get("signature_champions", []),
                    "champions_b": pb.get("signature_champions", []),
                    "champ_icons_a": pa.get("champion_icons", []),
                    "champ_icons_b": pb.get("champion_icons", []),
                    "contested_champions": overlap,
                    "advantage": team_a if rating_diff > 0.5 else (team_b if rating_diff < -0.5 else "EVEN"),
                }
            )

        return {
            "lane_comparisons": lane_comparisons,
            "contested_picks": contested_picks,
        }
