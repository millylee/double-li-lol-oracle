from pathlib import Path
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config import DB_PATH
from src.db.schema import get_connection, init_db
from src.db.repository import EsportsRepository
from src.etl.seed_history import seed_all_historical_data
from src.etl.rosters_catalog import generate_team_logo_svg, generate_player_avatar_svg
from src.etl.leaguepedia_client import LeaguepediaClient
from src.analytics.elo_engine import CrossRegionEloEngine
from src.analytics.feature_store import TeamFeatureStore
from src.agent.predictor_agent import MultiAgentMatchPredictor

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="LoL S1-S16 Global Esports & Multi-Agent Prediction System",
    version="1.0.0",
    description="Covers S1-S16 Worlds, MSI, and LCK/LPL/LEC/LCS regional data with Hybrid Elo/ML + Multi-Agent Match Prediction.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

repo = EsportsRepository(DB_PATH)
feature_store = TeamFeatureStore(DB_PATH)
elo_engine = CrossRegionEloEngine(DB_PATH)
agent_predictor = MultiAgentMatchPredictor(DB_PATH)


def ensure_initialized() -> None:
    init_db(DB_PATH)
    summary = repo.get_database_summary()
    if summary["tournaments_count"] == 0:
        seed_all_historical_data()
        elo_engine.recompute_all_ratings()
        agent_predictor.toolbox.quant.fit_historical_model()
        agent_predictor.toolbox.quant.calibrate_logit_scale()
        # Pick up the freshly fitted calibration temperature
        agent_predictor.toolbox.quant.logit_scale = agent_predictor.toolbox.quant._load_logit_scale()


@app.on_event("startup")
def on_startup() -> None:
    ensure_initialized()


class PredictRequest(BaseModel):
    team_a: str = "BLG"
    team_b: str = "GEN"
    best_of: int = 5
    stage: str = "Worlds Finals BO5"
    season: Optional[str] = None
    season_a: Optional[str] = "S16"
    season_b: Optional[str] = "S16"
    blue_side_team: Optional[str] = None
    use_llm: bool = True
    as_of_date: Optional[str] = None  # YYYY-MM-DD, restrict inputs to matches before this date


class LeaguepediaSyncRequest(BaseModel):
    overview_page: str = "2024 Season World Championship/Main Event"
    tournament_id: str = "LP_WORLDS_2024"
    tournament_name: str = "2024 Season World Championship (Live Sync)"
    season: str = "S14"
    year: int = 2024
    tier: str = "Worlds"
    region: str = "GLOBAL"


@app.get("/")
def serve_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/summary")
def get_summary() -> Dict[str, Any]:
    ensure_initialized()
    return repo.get_database_summary()


@app.get("/api/teams")
def list_teams(region: Optional[str] = Query(default=None)) -> Dict[str, Any]:
    ensure_initialized()
    teams = repo.get_all_teams(region=region)
    return {"count": len(teams), "teams": teams}


@app.get("/api/teams/{team_id}/profile")
def get_team_profile(team_id: str, season: Optional[str] = Query(default=None)) -> Dict[str, Any]:
    ensure_initialized()
    try:
        profile = feature_store.get_team_feature_profile(team_id, season=season)
        trajectory = repo.get_team_elo_trajectory(profile["team_id"])
        recent_matches = repo.get_matches(team_id=profile["team_id"], limit=15)
        return {
            "profile": profile,
            "elo_trajectory": trajectory,
            "recent_matches": recent_matches,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/api/tournaments")
def list_tournaments(
    season: Optional[str] = Query(default=None),
    tier: Optional[str] = Query(default=None),
    region: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    ensure_initialized()
    items = repo.get_tournaments(season=season, tier=tier, region=region)
    return {"count": len(items), "tournaments": items}


@app.get("/api/matches")
def list_matches(
    season: Optional[str] = Query(default=None),
    tournament_id: Optional[str] = Query(default=None),
    team_id: Optional[str] = Query(default=None),
    tier: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
) -> Dict[str, Any]:
    ensure_initialized()
    items = repo.get_matches(
        season=season,
        tournament_id=tournament_id,
        team_id=team_id,
        tier=tier,
        limit=limit,
    )
    return {"count": len(items), "matches": items}


@app.get("/api/avatar/team/{team_id}.svg")
def get_team_logo_svg(team_id: str) -> Response:
    svg = generate_team_logo_svg(team_id)
    return Response(content=svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})


@app.get("/api/avatar/player/{player_name}.svg")
def get_player_avatar_svg(
    player_name: str,
    team: str = Query(default="T1"),
    role: str = Query(default="mid"),
) -> Response:
    svg = generate_player_avatar_svg(player_name=player_name, team_id=team, role=role)
    return Response(content=svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})


@app.post("/api/predict")
def predict_matchup(req: PredictRequest) -> Dict[str, Any]:
    ensure_initialized()
    if req.team_a.upper() == req.team_b.upper() and (req.season_a == req.season_b):
        raise HTTPException(status_code=400, detail="请选择不同的战队或不同赛季时期的阵容进行对阵推演。")
    try:
        return agent_predictor.predict(
            team_a=req.team_a,
            team_b=req.team_b,
            best_of=req.best_of,
            stage=req.stage,
            season=req.season,
            season_a=req.season_a,
            season_b=req.season_b,
            blue_side_team=req.blue_side_team,
            use_llm=req.use_llm,
            as_of_date=req.as_of_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/api/backtest")
def run_backtest_endpoint() -> Dict[str, Any]:
    """Walk-forward backtest: each historical series is predicted using ONLY data
    from matches played strictly before its own date (as_of_date), so no future
    result can leak into Elo, form, H2H, or pedigree features."""
    ensure_initialized()
    with get_connection(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT sm.*, t.name AS tournament_name, t.tier AS tournament_tier
            FROM series_matches sm
            JOIN tournaments t ON sm.tournament_id = t.tournament_id
            WHERE sm.is_international = 1 AND sm.status = 'completed'
            ORDER BY sm.date_played DESC
            """
        ).fetchall()

    correct = 0
    total = 0
    details = []
    for r in rows:
        t1, t2 = r["team1_id"], r["team2_id"]
        actual_winner = r["winner_id"]
        pred = agent_predictor.toolbox.quant.predict_matchup(
            team_a_id=t1,
            team_b_id=t2,
            best_of=int(r["best_of"]),
            stage=f"{r['tournament_tier']} {r['stage']}",
            season=r["season"],
            as_of_date=r["date_played"],
        )
        pred_winner = pred["predicted_winner"]
        is_hit = pred_winner == actual_winner
        if is_hit:
            correct += 1
        total += 1
        if len(details) < 25:
            details.append(
                {
                    "season": r["season"],
                    "tournament": r["tournament_name"],
                    "stage": r["stage"],
                    "matchup": f"{r['team1_raw_name']} vs {r['team2_raw_name']}",
                    "actual_score": f"{r['team1_score']}:{r['team2_score']}",
                    "actual_winner": actual_winner,
                    "predicted_winner": pred_winner,
                    "predicted_prob": round(
                        max(pred["series_win_prob_a"], pred["series_win_prob_b"]) * 100, 1
                    ),
                    "predicted_score": pred["predicted_score"],
                    "correct": is_hit,
                }
            )

    return {
        "total_evaluated": total,
        "correct_predictions": correct,
        "accuracy_pct": round((correct / max(1, total)) * 100, 2),
        "sample_results": details,
    }


@app.post("/api/sync/leaguepedia")
def sync_leaguepedia_endpoint(req: LeaguepediaSyncRequest) -> Dict[str, Any]:
    ensure_initialized()
    client = LeaguepediaClient()
    try:
        res = client.sync_tournament_from_leaguepedia(
            overview_page=req.overview_page,
            tournament_id=req.tournament_id,
            tournament_name=req.tournament_name,
            season=req.season,
            year=req.year,
            tier=req.tier,
            region=req.region,
        )
        elo_engine.recompute_all_ratings()
        return {"status": "ok", "sync_result": res}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Leaguepedia Cargo API 同步失败: {exc}")
