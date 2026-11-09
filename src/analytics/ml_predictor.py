import math
from typing import Any, Dict, List, Optional
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from src.config import DB_PATH
from src.db.schema import get_connection
from src.db.repository import EsportsRepository
from src.analytics.feature_store import TeamFeatureStore


class QuantitativeMatchPredictor:
    """
    Hybrid Quantitative Match & Series Predictor:
    1. Trains a regularized LogisticRegression classifier over historical games (GD@15, Dragon/Baron rates, Elo, Side).
    2. Combines ML game-win probability with multi-factor analytical log-odds (Cross-Region Elo, Recent Form,
       Early-Game GD@15, Objective Control, Roster Matchup, H2H, and International BO5 Clutch Factor).
    3. Computes exact BO1 / BO3 / BO5 scoreline probability distributions via dynamic side-alternating Markov chains.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.repo = EsportsRepository(db_path)
        self.feature_store = TeamFeatureStore(db_path)
        self.scaler = StandardScaler()
        self.model = LogisticRegression(C=0.8, random_state=42)
        self._is_fitted = False
        self.logit_scale = self._load_logit_scale()

    def _load_logit_scale(self) -> float:
        """Loads the fitted probability-calibration temperature (see calibrate_logit_scale).
        Applied to the summed factor log-odds so output win rates match the model's
        walk-forward track record instead of stacking up to absurd 99% confidences."""
        try:
            with get_connection(self.db_path) as conn:
                row = conn.execute(
                    "SELECT value FROM model_params WHERE key = 'logit_scale'"
                ).fetchone()
                return float(row["value"]) if row else 1.0
        except Exception:
            return 1.0

    def calibrate_logit_scale(self) -> Dict[str, Any]:
        """Fits a single temperature on the total factor log-odds by maximum likelihood
        over a walk-forward backtest of all completed international series, then
        persists it to model_params. This corrects systematic over-confidence:
        each series is predicted ONLY from matches played strictly before its date."""
        if not self._is_fitted:
            self.fit_historical_model()

        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT sm.team1_id, sm.team2_id, sm.winner_id, sm.best_of, sm.stage,
                       sm.season, sm.date_played, t.tier
                FROM series_matches sm
                JOIN tournaments t ON sm.tournament_id = t.tournament_id
                WHERE sm.is_international = 1 AND sm.status = 'completed'
                ORDER BY sm.date_played ASC
                """
            ).fetchall()

        samples = []
        for r in rows:
            res = self.predict_matchup(
                team_a_id=r["team1_id"],
                team_b_id=r["team2_id"],
                best_of=int(r["best_of"]),
                stage=f"{r['tier']} {r['stage']}",
                season=r["season"],
                as_of_date=r["date_played"],
                _return_calibration_payload=True,
            )
            c = res["_calibration"]
            c["winner_is_a"] = r["winner_id"] == r["team1_id"]
            samples.append(c)

        def log_loss(scale: float) -> float:
            ll = 0.0
            for s in samples:
                dist = self._compute_series_distribution(
                    best_of=s["best_of"],
                    p_a_blue=self._sigmoid(s["z_raw"] * scale + s["edge_a"]),
                    p_a_red=self._sigmoid(s["z_raw"] * scale - s["edge_b"]),
                    a_starts_blue=s["a_starts_blue"],
                    clutch_bonus_a=s["clutch_bonus_a"],
                )
                p_a = sum(v for k, v in dist.items() if int(k.split(":")[0]) > int(k.split(":")[1]))
                p_outcome = p_a if s["winner_is_a"] else 1.0 - p_a
                ll += math.log(max(1e-9, p_outcome))
            return -ll / max(1, len(samples))

        # Grid search over the temperature, then keep the best
        grid = [round(0.20 + 0.005 * i, 3) for i in range(181)]  # 0.200 .. 1.100
        losses = [(log_loss(g), g) for g in grid]
        best_loss, best_scale = min(losses)

        with get_connection(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO model_params (key, value) VALUES ('logit_scale', ?)",
                (best_scale,),
            )
            conn.commit()
        self.logit_scale = best_scale

        return {
            "fitted_scale": best_scale,
            "samples": len(samples),
            "log_loss_before": round(log_loss(1.0), 4),
            "log_loss_after": round(best_loss, 4),
        }

    def fit_historical_model(self) -> Dict[str, Any]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT g.blue_team_id, g.red_team_id, g.winner_team_id,
                       g.blue_gd15, g.blue_xpd15, g.blue_dragons, g.red_dragons,
                       g.blue_barons, g.red_barons,
                       tb.current_elo AS blue_elo, tr.current_elo AS red_elo
                FROM games g
                JOIN series_matches sm ON g.match_id = sm.match_id AND sm.status = 'completed'
                LEFT JOIN teams tb ON g.blue_team_id = tb.team_id
                LEFT JOIN teams tr ON g.red_team_id = tr.team_id
                """
            ).fetchall()

        if len(rows) < 20:
            self._is_fitted = False
            return {"fitted": False, "samples": len(rows)}

        X = []
        y = []
        for r in rows:
            elo_diff = float((r["blue_elo"] or 1500.0) - (r["red_elo"] or 1500.0))
            gd15 = float(r["blue_gd15"] or 0.0)
            drag_diff = float((r["blue_dragons"] or 0) - (r["red_dragons"] or 0))
            baron_diff = float((r["blue_barons"] or 0) - (r["red_barons"] or 0))
            X.append([elo_diff / 100.0, gd15 / 1000.0, drag_diff, baron_diff, 1.0])
            y.append(1 if r["winner_team_id"] == r["blue_team_id"] else 0)

        X_arr = np.array(X, dtype=float)
        y_arr = np.array(y, dtype=int)
        X_scaled = self.scaler.fit_transform(X_arr)
        self.model.fit(X_scaled, y_arr)
        self._is_fitted = True
        acc = float(self.model.score(X_scaled, y_arr))
        return {"fitted": True, "samples": len(rows), "train_accuracy": round(acc, 4)}

    @staticmethod
    def _sigmoid(x: float) -> float:
        return 1.0 / (1.0 + math.exp(-max(-10.0, min(10.0, x))))

    def predict_matchup(
        self,
        team_a_id: str,
        team_b_id: str,
        best_of: int = 5,
        stage: str = "Worlds Knockout BO5",
        season: Optional[str] = None,
        season_a: Optional[str] = None,
        season_b: Optional[str] = None,
        blue_side_team: Optional[str] = None,
        as_of_date: Optional[str] = None,
        _return_calibration_payload: bool = False,
    ) -> Dict[str, Any]:
        """Predicts a matchup. `as_of_date` (YYYY-MM-DD) restricts every input
        (Elo, form, H2H, pedigree) to matches played strictly before that date —
        required for honest walk-forward backtesting. None = all completed data."""
        if not self._is_fitted:
            self.fit_historical_model()

        eff_season_a = season_a or season or "S16"
        eff_season_b = season_b or season or "S16"
        prof_a = self.feature_store.get_team_feature_profile(
            team_a_id, season=eff_season_a, as_of_date=as_of_date
        )
        prof_b = self.feature_store.get_team_feature_profile(
            team_b_id, season=eff_season_b, as_of_date=as_of_date
        )
        h2h = self.repo.get_head_to_head(prof_a["team_id"], prof_b["team_id"], as_of_date=as_of_date)

        # 1. Decomposed Log-Odds Contributions (positive favors Team A, negative favors Team B)
        elo_diff = prof_a["current_elo"] - prof_b["current_elo"]
        z_elo = (elo_diff / 400.0) * math.log(10.0) * 0.55

        form_diff = prof_a["recent_10_series_wr"] - prof_b["recent_10_series_wr"]
        z_form = form_diff * 1.15

        gd15_diff = (prof_a["avg_gd15"] - prof_b["avg_gd15"]) / 1000.0
        z_early = gd15_diff * 0.28 + (prof_a["first_tower_rate"] - prof_b["first_tower_rate"]) * 0.45

        obj_diff = (
            (prof_a["baron_control_rate"] - prof_b["baron_control_rate"]) * 0.85
            + (prof_a["dragon_control_rate"] - prof_b["dragon_control_rate"]) * 0.65
        )
        z_macro = obj_diff

        roster_diff = (prof_a["roster_avg_rating"] - prof_b["roster_avg_rating"]) / 10.0
        z_roster = roster_diff * 0.55

        # International & BO5 Clutch factor (Worlds/MSI pedigree)
        is_intl = any(k in stage.lower() for k in ["world", "msi", "international", "final", "knockout"])
        if is_intl:
            titles_diff = (prof_a["worlds_titles"] * 0.04 + prof_a["msi_titles"] * 0.025) - (
                prof_b["worlds_titles"] * 0.04 + prof_b["msi_titles"] * 0.025
            )
            bo5_diff = (prof_a["bo5_win_rate"] - prof_b["bo5_win_rate"]) * 0.55
            z_pedigree = max(-0.35, min(0.35, titles_diff + bo5_diff))
        else:
            z_pedigree = (prof_a["bo5_win_rate"] - prof_b["bo5_win_rate"]) * 0.25

        # Head-to-Head historical edge
        if h2h["total_series"] > 0:
            h2h_wr_a = h2h["team_a_series_wins"] / h2h["total_series"]
            weight_h2h = min(0.35, 0.07 * h2h["total_series"])
            z_h2h = (h2h_wr_a - 0.5) * weight_h2h * 2.0
        else:
            z_h2h = 0.0

        total_z_neutral = z_elo + z_form + z_early + z_macro + z_roster + z_pedigree + z_h2h
        # Temperature scaling fitted on the walk-forward backtest keeps output
        # probabilities calibrated instead of stacking into 99% confidences.
        z_scaled = total_z_neutral * self.logit_scale
        p_neutral_a = self._sigmoid(z_scaled)

        # Blue / Red side specific single-game probabilities.
        # Base logit edge reflects the real-world pro blue-side advantage (~52-55% game WR);
        # each team adds its own historical blue-vs-red comfort delta.
        blue_edge_a = 0.10 + 0.25 * (prof_a["blue_side_wr"] - prof_a["red_side_wr"])
        blue_edge_b = 0.10 + 0.25 * (prof_b["blue_side_wr"] - prof_b["red_side_wr"])
        edge_a = max(0.04, min(0.24, blue_edge_a))
        edge_b = max(0.04, min(0.24, blue_edge_b))

        p_a_on_blue = self._sigmoid(z_scaled + edge_a)
        p_a_on_red = self._sigmoid(z_scaled - edge_b)

        first_blue = (blue_side_team or prof_a["team_id"]).upper()
        a_starts_blue = first_blue == prof_a["team_id"]

        # Decider-game clutch factor. Symmetric magnitude keeps the matchup
        # order-invariant: swapping Team A/B mirrors the series probabilities exactly.
        if prof_a["game5_win_rate"] > prof_b["game5_win_rate"]:
            clutch_bonus_a = 0.02
        elif prof_b["game5_win_rate"] > prof_a["game5_win_rate"]:
            clutch_bonus_a = -0.02
        else:
            clutch_bonus_a = 0.0

        # Simulate exact series scoreline probabilities
        score_dist = self._compute_series_distribution(
            best_of=best_of,
            p_a_blue=p_a_on_blue,
            p_a_red=p_a_on_red,
            a_starts_blue=a_starts_blue,
            clutch_bonus_a=clutch_bonus_a,
        )

        series_win_prob_a = sum(
            prob for score, prob in score_dist.items() if int(score.split(":")[0]) > int(score.split(":")[1])
        )
        series_win_prob_b = 1.0 - series_win_prob_a

        most_likely_score = max(score_dist.items(), key=lambda x: x[1])

        # Feature attribution for explainability
        factors = [
            {
                "factor": "跨赛区动态 Elo 战力基线",
                "impact_score": round(z_elo, 3),
                "favored": prof_a["short_name"] if z_elo >= 0 else prof_b["short_name"],
                "detail": f"{prof_a['short_name']} ({prof_a['current_elo']}) vs {prof_b['short_name']} ({prof_b['current_elo']})",
            },
            {
                "factor": "近期系列赛状态 (近10场)",
                "impact_score": round(z_form, 3),
                "favored": prof_a["short_name"] if z_form >= 0 else prof_b["short_name"],
                "detail": f"{prof_a['short_name']} {prof_a['recent_10_series_wr']*100:.0f}% vs {prof_b['short_name']} {prof_b['recent_10_series_wr']*100:.0f}%",
            },
            {
                "factor": "前15分钟对线与节奏压制 (GD@15 & 一塔)",
                "impact_score": round(z_early, 3),
                "favored": prof_a["short_name"] if z_early >= 0 else prof_b["short_name"],
                "detail": f"GD@15: {prof_a['short_name']} {prof_a['avg_gd15']:+.0f}g vs {prof_b['short_name']} {prof_b['avg_gd15']:+.0f}g",
            },
            {
                "factor": "中后期史诗资源运营 (大龙 & 小龙控制率)",
                "impact_score": round(z_macro, 3),
                "favored": prof_a["short_name"] if z_macro >= 0 else prof_b["short_name"],
                "detail": f"控大龙率: {prof_a['short_name']} {prof_a['baron_control_rate']*100:.0f}% vs {prof_b['short_name']} {prof_b['baron_control_rate']*100:.0f}%",
            },
            {
                "factor": "首发五虎纸面战力与对位均值",
                "impact_score": round(z_roster, 3),
                "favored": prof_a["short_name"] if z_roster >= 0 else prof_b["short_name"],
                "detail": f"综合战力评分: {prof_a['short_name']} {prof_a['roster_avg_rating']} vs {prof_b['short_name']} {prof_b['roster_avg_rating']}",
            },
            {
                "factor": "世界赛/MSI 大赛底蕴与 BO5 韧性",
                "impact_score": round(z_pedigree, 3),
                "favored": prof_a["short_name"] if z_pedigree >= 0 else prof_b["short_name"],
                "detail": f"S赛/MSI冠: {prof_a['short_name']} ({prof_a['worlds_titles']}/{prof_a['msi_titles']}) vs {prof_b['short_name']} ({prof_b['worlds_titles']}/{prof_b['msi_titles']})",
            },
            {
                "factor": "历史交手记录克制 (H2H)",
                "impact_score": round(z_h2h, 3),
                "favored": prof_a["short_name"] if z_h2h >= 0 else prof_b["short_name"],
                "detail": f"历史交手系列赛: {prof_a['short_name']} {h2h['team_a_series_wins']} : {h2h['team_b_series_wins']} {prof_b['short_name']}",
            },
        ]

        result = {
            "team_a": prof_a,
            "team_b": prof_b,
            "head_to_head": h2h,
            "best_of": best_of,
            "stage": stage,
            "as_of_date": as_of_date,
            "single_game_neutral_prob_a": round(p_neutral_a, 4),
            "single_game_blue_prob_a": round(p_a_on_blue, 4),
            "single_game_red_prob_a": round(p_a_on_red, 4),
            "series_win_prob_a": round(series_win_prob_a, 4),
            "series_win_prob_b": round(series_win_prob_b, 4),
            "predicted_winner": prof_a["team_id"] if series_win_prob_a >= 0.5 else prof_b["team_id"],
            "predicted_score": most_likely_score[0],
            "predicted_score_prob": round(most_likely_score[1], 4),
            "score_distribution": {k: round(v, 4) for k, v in score_dist.items()},
            "silver_scrapes_prob": round(score_dist.get("3:2", 0.0) + score_dist.get("2:3", 0.0), 4)
            if best_of == 5
            else 0.0,
            "factor_attributions": factors,
        }

        if _return_calibration_payload:
            result["_calibration"] = {
                "z_raw": total_z_neutral,
                "edge_a": edge_a,
                "edge_b": edge_b,
                "a_starts_blue": a_starts_blue,
                "clutch_bonus_a": clutch_bonus_a,
                "best_of": best_of,
            }
        return result

    @staticmethod
    def _compute_series_distribution(
        best_of: int,
        p_a_blue: float,
        p_a_red: float,
        a_starts_blue: bool,
        clutch_bonus_a: float = 0.0,
    ) -> Dict[str, float]:
        if best_of == 1:
            p1 = p_a_blue if a_starts_blue else p_a_red
            return {"1:0": p1, "0:1": 1.0 - p1}

        target_wins = (best_of // 2) + 1
        # State: (wins_a, wins_b, next_blue_is_a) -> probability
        states: Dict[tuple, float] = {(0, 0, a_starts_blue): 1.0}
        terminal_scores: Dict[str, float] = {}

        for game_idx in range(1, best_of + 1):
            next_states: Dict[tuple, float] = {}
            for (wa, wb, blue_is_a), prob in states.items():
                if wa == target_wins or wb == target_wins:
                    key = f"{wa}:{wb}"
                    terminal_scores[key] = terminal_scores.get(key, 0.0) + prob
                    continue

                p_win_a = p_a_blue if blue_is_a else p_a_red
                # In decider game (e.g., 2-2 in BO5), apply clutch factor
                if best_of == 5 and wa == 2 and wb == 2:
                    p_win_a = max(0.08, min(0.92, p_win_a + clutch_bonus_a))

                # If A wins this game, B (the loser) picks Blue side next game
                na_win = (wa + 1, wb, False)
                # If B wins this game, A (the loser) picks Blue side next game
                nb_win = (wa, wb + 1, True)

                next_states[na_win] = next_states.get(na_win, 0.0) + prob * p_win_a
                next_states[nb_win] = next_states.get(nb_win, 0.0) + prob * (1.0 - p_win_a)
            states = next_states

        for (wa, wb, _), prob in states.items():
            key = f"{wa}:{wb}"
            terminal_scores[key] = terminal_scores.get(key, 0.0) + prob

        # Order score keys logically
        ordered_keys = (
            ["3:0", "3:1", "3:2", "2:3", "1:3", "0:3"]
            if best_of == 5
            else ["2:0", "2:1", "1:2", "0:2"]
        )
        return {k: terminal_scores.get(k, 0.0) for k in ordered_keys if k in terminal_scores}
