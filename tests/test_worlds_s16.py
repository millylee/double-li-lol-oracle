import copy
import sqlite3
import unittest
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.repair_worlds_s16 import LEGACY_SUMMARY, repair_worlds_s16
from src.analytics.elo_engine import CrossRegionEloEngine
from src.etl import seed_history

DATE = "2026-11-27"
WORLDS = "WORLDS_S16"


def query(db, sql):
    with closing(sqlite3.connect(db)) as conn:
        return conn.execute(sql).fetchall()


def seed(db, *, legacy=False, today=DATE):
    catalog = copy.deepcopy(seed_history.WORLDS_CATALOG)
    if legacy:
        worlds = catalog[-1]
        for index, match in seed_history.LEGACY_S16_MATCHES.items():
            worlds["matches"][index - 1] = match
        worlds.update(
            champion=("GEN", "Gen.G"), runner_up=("BLG", "Bilibili Gaming"),
            mvp="Chovy", summary=LEGACY_SUMMARY,
        )
    with patch.object(seed_history, "WORLDS_CATALOG", catalog), patch.object(seed_history, "_today_str", return_value=today):
        if legacy:
            with patch.object(seed_history, "LEGACY_S16_MATCHES", {}):
                seed_history.seed_all_historical_data(db)
        else:
            seed_history.seed_all_historical_data(db)
    if legacy:
        with closing(sqlite3.connect(db)) as conn, conn:
            conn.execute("DELETE FROM teams WHERE team_id IN ('KC', 'LYON')")
            conn.execute("UPDATE tournaments SET summary = ? WHERE tournament_id = 'WORLDS_S16'", (LEGACY_SUMMARY,))
    CrossRegionEloEngine(db).recompute_all_ratings()


class WorldsS16Test(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.db = self.root / "database.sqlite"
        self.backup = self.root / "backup.sqlite"

    def test_fresh_seed_and_elo_cutoff(self):
        seed(self.db)
        self.assertEqual(query(self.db, "SELECT champion_team_id, runner_up_team_id, mvp_player "
                         "FROM tournaments WHERE tournament_id = 'WORLDS_S16'"), [("BLG", "GEN", "Knight")])
        self.assertEqual(query(self.db, "SELECT team1_id, team2_id, team1_score, team2_score FROM series_matches "
                         "WHERE tournament_id = 'WORLDS_S16' ORDER BY match_id"), [
            ("BLG", "GEN", 3, 1), ("BLG", "T1", 3, 1), ("GEN", "IG", 3, 0),
            ("T1", "KC", 3, 1), ("BLG", "DK", 3, 0), ("GEN", "LYON", 3, 0), ("IG", "TES", 3, 1),
        ])
        self.assertEqual(query(self.db, "SELECT COUNT(*) FROM games WHERE tournament_id = 'WORLDS_S16'"), [(25,)])
        self.assertEqual(query(self.db, "SELECT worlds_titles FROM teams WHERE team_id = 'BLG'"), [(1,)])
        before, after = query(self.db, "SELECT elo_before, elo_after FROM elo_history "
                              "WHERE match_id = 'WORLDS_S16_M01' AND team_id = 'BLG'")[0]
        engine = CrossRegionEloEngine(self.db)
        self.assertGreater(after, before)
        self.assertEqual(engine.get_elo_as_of(["BLG"], "2026-11-14")["BLG"], before)
        self.assertEqual(engine.get_elo_as_of(["BLG"], "2026-11-15")["BLG"], after)

    def test_protect_future_final(self):
        seed(self.db, today="2026-11-13")
        self.assertEqual(query(self.db, "SELECT champion_team_id, mvp_player, summary FROM tournaments "
                         "WHERE tournament_id = 'WORLDS_S16'"), [(None, "", "S16 全球总决赛尚未结束。")])
        self.assertEqual(query(self.db, "SELECT status, winner_id FROM series_matches "
                         "WHERE match_id = 'WORLDS_S16_M01'"), [("scheduled", "")])
        self.assertEqual(query(self.db, "SELECT COUNT(*) FROM elo_history WHERE match_id = 'WORLDS_S16_M01'"), [(0,)])

    def test_migration_backup_and_seed_compatibility(self):
        seed(self.db, legacy=True)
        fresh = self.root / "fresh.sqlite"
        seed(fresh)
        legacy_final = query(self.db, "SELECT * FROM series_matches WHERE match_id = 'WORLDS_S16_M01'")
        with patch.object(seed_history, "_today_str", return_value=DATE):
            self.assertEqual(repair_worlds_s16(self.db), 6)
            self.assertEqual(query(self.db, "SELECT * FROM series_matches WHERE match_id = 'WORLDS_S16_M01'"), legacy_final)
            self.assertEqual(repair_worlds_s16(self.db, self.backup), 6)
            self.assertIsNone(repair_worlds_s16(self.db, self.backup))
        self.assertEqual(query(self.backup, "SELECT * FROM series_matches WHERE match_id = 'WORLDS_S16_M01'"), legacy_final)
        for table, key in (("series_matches", "match_id"), ("games", "game_id")):
            sql = f"SELECT * FROM {table} ORDER BY {key}"
            self.assertEqual(query(self.db, sql), query(fresh, sql), table)
            non_s16 = f"SELECT * FROM {table} WHERE tournament_id <> '{WORLDS}' ORDER BY {key}"
            self.assertEqual(query(self.backup, non_s16), query(fresh, non_s16), table)
        self.assertEqual(query(self.db, "PRAGMA integrity_check"), [("ok",)])

    def test_repairs_legacy_scheduled_rows(self):
        seed(self.db, legacy=True, today="2026-11-05")
        with patch.object(seed_history, "_today_str", return_value=DATE):
            self.assertEqual(repair_worlds_s16(self.db, self.backup), 6)
        self.assertEqual(query(self.db, "SELECT COUNT(*) FROM series_matches "
                         "WHERE tournament_id = 'WORLDS_S16' AND status = 'completed'"), [(7,)])

    def test_conflict_rolls_back_earlier_changes(self):
        seed(self.db, legacy=True)
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute("UPDATE games SET duration_sec = 9999 WHERE game_id = 'WORLDS_S16_M06_G1'")
        with patch.object(seed_history, "_today_str", return_value=DATE):
            with self.assertRaisesRegex(ValueError, "contains non-seed game data"):
                repair_worlds_s16(self.db, self.backup)
        self.assertFalse(self.backup.exists())
        self.assertEqual(query(self.db, "SELECT winner_id FROM series_matches WHERE match_id = 'WORLDS_S16_M01'"), [("GEN",)])


if __name__ == "__main__":
    unittest.main()
