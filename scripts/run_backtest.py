import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.api.main import ensure_initialized, run_backtest_endpoint
from src.agent.predictor_agent import MultiAgentMatchPredictor


def main() -> None:
    ensure_initialized()
    print("=" * 76)
    print("  LoL S1-S16 International Knockout Series Backtest & Agent Verification")
    print("=" * 76)

    bt = run_backtest_endpoint()
    print(
        f"Total International Series Evaluated : {bt['total_evaluated']}\n"
        f"Correct Winner Predictions           : {bt['correct_predictions']}\n"
        f"Historical Backtest Accuracy         : {bt['accuracy_pct']}%\n"
    )
    print("Recent International Series Backtest Sample:")
    for item in bt["sample_results"][:10]:
        mark = "HIT " if item["correct"] else "MISS"
        print(
            f"  [{mark}] {item['season']:3s} | {item['tournament']:34s} | {item['stage']:15s} | "
            f"{item['matchup']:32s} | Actual {item['actual_score']} | Pred: {item['predicted_winner']} ({item['predicted_prob']}%)"
        )

    print("\n" + "=" * 76)
    print("  Sample Multi-Agent Matchup Prediction: T1 vs BLG (BO5 Worlds Finals)")
    print("=" * 76)
    agent = MultiAgentMatchPredictor()
    res = agent.predict(team_a="T1", team_b="BLG", best_of=5, stage="Worlds Finals BO5")
    pred = res["prediction"]
    print(
        f"Predicted Winner      : {pred['winner_name']} ({pred['winner_id']})\n"
        f"Series Win Prob       : T1 {pred['team_a_win_prob']*100:.1f}% vs BLG {pred['team_b_win_prob']*100:.1f}%\n"
        f"Most Likely Scoreline : T1 {pred['most_likely_score']} BLG ({pred['most_likely_score_prob']*100:.1f}%)\n"
        f"Silver Scrapes (G5) % : {pred['silver_scrapes_prob']*100:.1f}%\n"
        f"Score Distribution    : {pred['score_distribution']}"
    )
    print("\nAgent Tool Execution Trace:")
    for step in res["agent_execution_trace"]:
        print(f"  - [{step['latency_ms']}ms] {step['agent']} -> {step['summary']}")


if __name__ == "__main__":
    main()
