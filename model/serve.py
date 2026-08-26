"""
model/serve.py
Runs the trained model over every pitch to build:
1. Full win-prob time series per game (for replay)
2. Per-game summary table with dramatic-swing metrics (for leaderboard)
"""
import pandas as pd
import numpy as np
import joblib

FEATURES = [
    "inning", "is_home_batting", "half_inning_num",
    "outs_when_up", "base_state", "base_out_state",
    "balls", "strikes", "home_score_diff",
]

def main():
    df = pd.read_parquet("data/gold_features.parquet")
    test = df[df["season"] == 2024].copy()

    model = joblib.load("model/winprob_model.pkl")
    test["home_win_prob"] = model.predict_proba(test[FEATURES])[:, 1]
    test = test.sort_values(["game_pk", "at_bat_number", "pitch_number"])

    replay = test[[
        "game_pk", "game_date", "home_team", "away_team",
        "inning", "is_home_batting", "outs_when_up",
        "home_score_diff", "home_win_prob", "home_win",
    ]].copy()
    replay.to_parquet("data/gold_replay_timeseries.parquet", index=False)
    print(f"Saved replay time series: {len(replay):,} rows across {replay['game_pk'].nunique():,} games")

    def game_summary(g):
        probs = g["home_win_prob"].values
        swings = np.abs(np.diff(probs))
        max_swing = swings.max() if len(swings) > 0 else 0.0

        home_won = g["home_win"].iloc[0] == 1
        relevant_probs = probs if home_won else (1 - probs)
        min_prob_for_winner = relevant_probs.min()
        biggest_deficit_overcome = max(0.0, 0.5 - min_prob_for_winner)

        return pd.Series({
            "game_date": g["game_date"].iloc[0],
            "home_team": g["home_team"].iloc[0],
            "away_team": g["away_team"].iloc[0],
            "home_win": g["home_win"].iloc[0],
            "max_single_pitch_swing": max_swing,
            "biggest_deficit_overcome": biggest_deficit_overcome,
            "n_pitches": len(g),
        })

    leaderboard = test.groupby("game_pk").apply(game_summary, include_groups=False).reset_index()
    leaderboard = leaderboard.sort_values("max_single_pitch_swing", ascending=False)
    leaderboard.to_parquet("data/gold_leaderboard.parquet", index=False)

    print(f"\nSaved leaderboard: {len(leaderboard):,} games")
    print("\nTop 5 most dramatic single-pitch swings:")
    print(leaderboard.head(5)[[
        "game_date", "home_team", "away_team", "max_single_pitch_swing"
    ]].to_string(index=False))

if __name__ == "__main__":
    main()
