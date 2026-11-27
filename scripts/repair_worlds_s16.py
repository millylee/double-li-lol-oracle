"""Repair the original Worlds S16 seed in an existing SQLite database."""
import argparse
import random
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analytics.elo_engine import CrossRegionEloEngine
from src.db.schema import get_connection
from src.etl.seed_history import (
    HISTORICAL_SEED,
    LEGACY_S16_MATCHES,
    WORLDS_CATALOG,
    _generate_games_for_series,
    _is_future_fixture,
    seed_all_historical_data,
)

TOURNAMENT_ID = "WORLDS_S16"
COLUMNS = (
    "date_played", "stage", "best_of", "team1_id", "team1_raw_name",
    "team2_id", "team2_raw_name", "team1_score", "team2_score",
)
LEGACY_SUMMARY = (
    "无畏征召（全局 BP）全面实装的世界赛舞台！八强战 iG 3:1 力克 TES、BLG 击败 DK，"
    "Gen.G 与 BLG 会师纽约巴克莱中心总决赛。"
)


def legacy_games(scheduled_ids):
    """Recreate the original game rows, including seeds run before the final."""
    rng = random.Random(HISTORICAL_SEED)
    for worlds in WORLDS_CATALOG:
        season, year, patch = (worlds[key] for key in ("season", "year", "patch"))
        tournament_id = f"WORLDS_{season}"
        for index, match in enumerate(worlds["matches"], 1):
            match_id = f"{tournament_id}_M{index:02d}"
            if season == "S16":
                match = LEGACY_S16_MATCHES.get(index, match)
            day, _, _, t1, _, t2, _, s1, s2 = match
            games = [] if match_id in scheduled_ids else _generate_games_for_series(
                rng, match_id, tournament_id, season, year, day, patch, t1, t2, s1, s2
            )
            if season == "S16":
                yield match_id, games


def repair_worlds_s16(db_path: Path, backup: Path | None = None) -> int | None:
    """Dry-run by default. With a backup path, back up then commit atomically."""
    db_path = db_path.resolve(strict=True)
    if not db_path.is_file():
        raise ValueError("Expected an existing SQLite file")
    worlds = next(w for w in WORLDS_CATALOG if w["season"] == "S16")
    if any(_is_future_fixture(match[0]) for match in worlds["matches"]):
        raise ValueError("Cannot migrate before all S16 knockout fixtures have been played")

    with TemporaryDirectory(prefix="worlds-s16-") as tmp:
        reference_path = Path(tmp) / "corrected.db"
        seed_all_historical_data(reference_path)
        with closing(get_connection(reference_path)) as reference, closing(get_connection(db_path)) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("BEGIN IMMEDIATE")
            tournament = conn.execute(
                "SELECT * FROM tournaments WHERE tournament_id = ?", (TOURNAMENT_ID,)
            ).fetchone()
            if not tournament or (tournament["season"], tournament["tier"], tournament["year"]) != ("S16", "Worlds", 2026):
                raise ValueError("No compatible Worlds S16 seed found")
            original = ("GEN", "BLG", "Chovy", LEGACY_SUMMARY)
            pending = (None, None, "", LEGACY_SUMMARY)
            corrected = ("BLG", "GEN", "Knight", worlds["summary"])
            keys = ("champion_team_id", "runner_up_team_id", "mvp_player", "summary")
            metadata = tuple(tournament[key] for key in keys)
            if metadata not in (original, pending, corrected):
                raise ValueError("Worlds S16 tournament metadata differs from the known seed; no changes made")

            rows = conn.execute(
                "SELECT * FROM series_matches WHERE tournament_id = ?", (TOURNAMENT_ID,)
            ).fetchall()
            by_id = {row["match_id"]: row for row in rows}
            expected_slots = {(match[0], match[1]) for match in worlds["matches"]}
            expected_ids = {f"{TOURNAMENT_ID}_M{i:02d}" for i in range(1, 8)}
            if any((row["date_played"], row["stage"]) in expected_slots
                   for row in rows if row["match_id"] not in expected_ids):
                raise ValueError("Additional matches overlap the original knockout slots; no changes made")
            if not expected_ids.issubset(by_id):
                raise ValueError("The database is missing one or more original S16 knockout IDs")
            completed = [r["date_played"] for r in rows if r["match_id"] in expected_ids and r["status"] == "completed"]
            scheduled = [r["date_played"] for r in rows if r["match_id"] in expected_ids and r["status"] == "scheduled"]
            if completed and scheduled and max(completed) >= min(scheduled):
                raise ValueError("Unexpected mix of scheduled and completed rows; no changes made")
            old_games = dict(legacy_games({
                r["match_id"] for r in rows if r["match_id"] in expected_ids and r["status"] == "scheduled"
            }))

            changed = 0
            for index, match in enumerate(worlds["matches"], 1):
                match_id = f"{TOURNAMENT_ID}_M{index:02d}"
                row = by_id[match_id]
                found = tuple(row[key] for key in COLUMNS)
                if (row["source"], row["season"], row["year"], row["patch"], row["is_international"]) != (
                    "historical_archive", "S16", 2026, worlds["patch"], 1
                ):
                    raise ValueError(f"{match_id} differs from the original seed; no changes made")
                if found == match and row["status"] == "completed" and row["winner_id"] == match[3]:
                    continue
                legacy = LEGACY_S16_MATCHES.get(index, match)
                if not (
                    (row["status"], found, row["winner_id"]) == ("completed", legacy, legacy[3])
                    or (row["status"], found, row["winner_id"]) == ("scheduled", (*legacy[:-2], 0, 0), "")
                ):
                    raise ValueError(f"{match_id} differs from the original seed; no changes made")
                games_sql = "SELECT * FROM games WHERE match_id = ? ORDER BY game_number"
                if [tuple(game) for game in conn.execute(games_sql, (match_id,))] != old_games[match_id]:
                    raise ValueError(f"{match_id} contains non-seed game data; no changes made")
                conn.execute(
                    "UPDATE series_matches SET " + ", ".join(f"{key} = ?" for key in COLUMNS)
                    + ", winner_id = ?, status = 'completed' WHERE match_id = ?",
                    (*match, match[3], match_id),
                )
                conn.execute("DELETE FROM games WHERE match_id = ?", (match_id,))
                games = [tuple(game) for game in reference.execute(games_sql, (match_id,))]
                conn.executemany("INSERT INTO games VALUES (" + ",".join("?" * 32) + ")", games)
                changed += 1

            if not changed and metadata == corrected:
                return None

            for team in reference.execute(
                "SELECT team_id, name, short_name, region, founded_season, aliases_json "
                "FROM teams WHERE team_id IN ('KC', 'LYON')"
            ):
                conn.execute(
                    "INSERT OR IGNORE INTO teams (team_id, name, short_name, region, founded_season, aliases_json) "
                    "VALUES (?, ?, ?, ?, ?, ?)", tuple(team),
                )
                existing = conn.execute(
                    "SELECT name, region FROM teams WHERE team_id = ?", (team["team_id"],)
                ).fetchone()
                if tuple(existing) != (team["name"], team["region"]):
                    raise ValueError(f"Team ID {team['team_id']} is already used differently; no changes made")

            conn.execute(
                "UPDATE tournaments SET champion_team_id = ?, runner_up_team_id = ?, mvp_player = ?, summary = ? "
                "WHERE tournament_id = ?", (*corrected, TOURNAMENT_ID),
            )
            conn.execute(
                "UPDATE teams SET worlds_titles = "
                "(SELECT COUNT(*) FROM tournaments WHERE tier = 'Worlds' AND champion_team_id = teams.team_id) "
                "WHERE team_id IN ('BLG', 'GEN')"
            )
            CrossRegionEloEngine(db_path).recompute_all_ratings(connection=conn)

            if backup is None:
                conn.rollback()
            else:
                # BEGIN IMMEDIATE blocks other writers; this read-only connection
                # backs up the committed pre-migration state, including WAL content.
                with backup.open("xb"), closing(sqlite3.connect(backup)) as target:
                    with closing(sqlite3.connect(f"{db_path.as_uri()}?mode=ro", uri=True)) as source:
                        source.backup(target)
                    if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise ValueError("Backup integrity check failed; no changes made")
                conn.commit()
            return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True, help="Path to an existing SQLite database")
    parser.add_argument("--backup", type=Path, help="A new backup file; only supplying it commits the change")
    args = parser.parse_args()
    try:
        count = repair_worlds_s16(args.db, args.backup)
    except (OSError, ValueError, sqlite3.Error) as exc:
        parser.exit(1, f"Repair stopped: {exc}\n")
    if count is None:
        print("Worlds S16 already up to date.")
    elif args.backup:
        print(f"Updated {count} series and rebuilt Elo. Backup: {args.backup}")
    else:
        print(f"Dry run: {count} series would be updated and Elo rebuilt; database unchanged.")


if __name__ == "__main__":
    main()
