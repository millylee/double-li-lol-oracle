import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.etl.seed_history import seed_all_historical_data
from src.etl.leaguepedia_client import LeaguepediaClient
from src.etl.oracles_elixir import OraclesElixirImporter
from src.analytics.elo_engine import CrossRegionEloEngine
from src.analytics.ml_predictor import QuantitativeMatchPredictor


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LoL S1-S16 Data Pipeline: Seed historical archive, import Oracle's Elixir CSV, or sync Leaguepedia API."
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        default=True,
        help="Initialize and seed S1-S16 Worlds, MSI, and LCK/LPL/LEC/LCS historical dataset (default: True)",
    )
    parser.add_argument(
        "--oe-csv",
        type=str,
        default="",
        help="Path to an Oracle's Elixir CSV file (e.g., 2024_LoL_esports_match_data_from_OraclesElixir.csv) to import",
    )
    parser.add_argument(
        "--leaguepedia-page",
        type=str,
        default="",
        help="Leaguepedia OverviewPage to fetch live via Cargo API (e.g. '2024 Season World Championship/Main Event')",
    )
    args = parser.parse_args()

    if args.seed:
        print("[1/3] Seeding S1-S16 Worlds, MSI, and Regional (LCK/LPL/LEC/LCS) database...")
        stats = seed_all_historical_data()
        print(f"      -> Inserted/Updated: {stats}")

    if args.oe_csv:
        csv_path = Path(args.oe_csv)
        print(f"[OE] Importing Oracle's Elixir CSV from {csv_path}...")
        importer = OraclesElixirImporter()
        oe_res = importer.import_csv(csv_path)
        print(f"      -> Oracle's Elixir Import Result: {oe_res}")

    if args.leaguepedia_page:
        print(f"[LP] Fetching Leaguepedia Cargo API page: {args.leaguepedia_page}...")
        lp = LeaguepediaClient()
        lp_res = lp.sync_tournament_from_leaguepedia(
            overview_page=args.leaguepedia_page,
            tournament_id="LP_CUSTOM_SYNC",
            tournament_name=args.leaguepedia_page,
            season="S14",
            year=2024,
        )
        print(f"      -> Leaguepedia Sync Result: {lp_res}")

    print("[2/3] Recomputing chronological S1-S16 Cross-Region Elo ratings...")
    elo = CrossRegionEloEngine()
    elo_res = elo.recompute_all_ratings()
    print(f"      -> Processed {elo_res['matches_processed']} series matches.")
    print(f"      -> Calibrated Regional Base Elo: {elo_res['calibrated_region_ratings']}")
    print("      -> Top 8 Global Teams by Current Calibrated Elo:")
    for idx, item in enumerate(elo_res["top_10_elo"][:8], start=1):
        print(f"         #{idx} {item['team_id']:4s} | Current Elo: {item['elo']:7.2f} | Peak Elo: {item['peak_elo']:7.2f}")

    print("[3/4] Fitting Quantitative ML Game Classifier...")
    quant = QuantitativeMatchPredictor()
    ml_res = quant.fit_historical_model()
    print(f"      -> ML Model Status: {ml_res}")

    print("[4/4] Calibrating win-probability temperature on walk-forward backtest...")
    cal_res = quant.calibrate_logit_scale()
    print(
        f"      -> Fitted logit scale: {cal_res['fitted_scale']} "
        f"(log loss {cal_res['log_loss_before']} -> {cal_res['log_loss_after']} on {cal_res['samples']} series)"
    )


if __name__ == "__main__":
    main()
