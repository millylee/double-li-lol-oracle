import sqlite3
from pathlib import Path
from src.config import DB_PATH


SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS teams (
    team_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    short_name TEXT NOT NULL,
    region TEXT NOT NULL,
    founded_season TEXT DEFAULT 'S1',
    worlds_titles INTEGER DEFAULT 0,
    msi_titles INTEGER DEFAULT 0,
    aliases_json TEXT DEFAULT '[]',
    current_elo REAL DEFAULT 1500.0,
    peak_elo REAL DEFAULT 1500.0,
    peak_season TEXT DEFAULT 'S1'
);

CREATE TABLE IF NOT EXISTS tournaments (
    tournament_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    season TEXT NOT NULL,
    year INTEGER NOT NULL,
    tier TEXT NOT NULL,        -- 'Worlds', 'MSI', 'Regional'
    region TEXT NOT NULL,      -- 'GLOBAL', 'LCK', 'LPL', 'LEC', 'LCS'
    split TEXT DEFAULT 'Main', -- 'Spring', 'Summer', 'Main'
    champion_team_id TEXT,
    runner_up_team_id TEXT,
    patch TEXT DEFAULT '',
    location TEXT DEFAULT '',
    mvp_player TEXT DEFAULT '',
    summary TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS series_matches (
    match_id TEXT PRIMARY KEY,
    tournament_id TEXT NOT NULL,
    season TEXT NOT NULL,
    year INTEGER NOT NULL,
    date_played TEXT NOT NULL,
    stage TEXT NOT NULL,
    best_of INTEGER NOT NULL DEFAULT 5,
    team1_id TEXT NOT NULL,
    team2_id TEXT NOT NULL,
    team1_raw_name TEXT NOT NULL,
    team2_raw_name TEXT NOT NULL,
    team1_score INTEGER NOT NULL,
    team2_score INTEGER NOT NULL,
    winner_id TEXT NOT NULL,
    patch TEXT DEFAULT '',
    is_international INTEGER DEFAULT 0,
    source TEXT DEFAULT 'seed',
    status TEXT NOT NULL DEFAULT 'completed',  -- 'completed' | 'scheduled'
    FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id)
);

CREATE TABLE IF NOT EXISTS games (
    game_id TEXT PRIMARY KEY,
    match_id TEXT NOT NULL,
    tournament_id TEXT NOT NULL,
    season TEXT NOT NULL,
    year INTEGER NOT NULL,
    date_played TEXT NOT NULL,
    game_number INTEGER NOT NULL,
    blue_team_id TEXT NOT NULL,
    red_team_id TEXT NOT NULL,
    winner_team_id TEXT NOT NULL,
    duration_sec INTEGER DEFAULT 1950,
    patch TEXT DEFAULT '',
    blue_kills INTEGER DEFAULT 0,
    red_kills INTEGER DEFAULT 0,
    blue_gold INTEGER DEFAULT 0,
    red_gold INTEGER DEFAULT 0,
    blue_gd15 REAL DEFAULT 0.0,
    blue_xpd15 REAL DEFAULT 0.0,
    blue_csd15 REAL DEFAULT 0.0,
    first_blood_team_id TEXT DEFAULT '',
    first_tower_team_id TEXT DEFAULT '',
    first_dragon_team_id TEXT DEFAULT '',
    blue_dragons INTEGER DEFAULT 0,
    red_dragons INTEGER DEFAULT 0,
    blue_barons INTEGER DEFAULT 0,
    red_barons INTEGER DEFAULT 0,
    blue_towers INTEGER DEFAULT 0,
    red_towers INTEGER DEFAULT 0,
    blue_bans_json TEXT DEFAULT '[]',
    red_bans_json TEXT DEFAULT '[]',
    blue_picks_json TEXT DEFAULT '[]',
    red_picks_json TEXT DEFAULT '[]',
    FOREIGN KEY (match_id) REFERENCES series_matches(match_id)
);

CREATE TABLE IF NOT EXISTS player_rosters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id TEXT NOT NULL,
    season TEXT NOT NULL,
    role TEXT NOT NULL, -- 'top', 'jng', 'mid', 'bot', 'sup'
    player_name TEXT NOT NULL,
    kda REAL DEFAULT 3.5,
    dpm REAL DEFAULT 520.0,
    gd15 REAL DEFAULT 0.0,
    cs_per_min REAL DEFAULT 8.5,
    kp_pct REAL DEFAULT 68.0,
    signature_champions_json TEXT DEFAULT '[]',
    rating REAL DEFAULT 82.0,
    UNIQUE(team_id, season, role)
);

CREATE TABLE IF NOT EXISTS elo_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id TEXT NOT NULL,
    date_played TEXT NOT NULL,
    season TEXT NOT NULL,
    team_id TEXT NOT NULL,
    elo_before REAL NOT NULL,
    elo_after REAL NOT NULL,
    opponent_id TEXT NOT NULL,
    is_international INTEGER DEFAULT 0,
    stage TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS model_params (
    key TEXT PRIMARY KEY,
    value REAL NOT NULL,
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_series_season ON series_matches(season, year);
CREATE INDEX IF NOT EXISTS idx_series_teams ON series_matches(team1_id, team2_id);
CREATE INDEX IF NOT EXISTS idx_series_tournament ON series_matches(tournament_id);
CREATE INDEX IF NOT EXISTS idx_games_teams ON games(blue_team_id, red_team_id);
CREATE INDEX IF NOT EXISTS idx_games_season ON games(season);
CREATE INDEX IF NOT EXISTS idx_elo_team ON elo_history(team_id, date_played);
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        # Migration for databases created before the 'status' column existed
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(series_matches)").fetchall()]
        if "status" not in cols:
            conn.execute(
                "ALTER TABLE series_matches ADD COLUMN status TEXT NOT NULL DEFAULT 'completed'"
            )
        conn.commit()
