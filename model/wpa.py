"""
model/wpa.py
Computes Win Probability Added (WPA) per player, 2024 test set only.
Uses FIRST pitch of each PA (clean post-previous-PA state), not the last.
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
    gold = pd.read_parquet("data/gold_features.parquet")
    gold = gold[gold["season"] == 2024].copy()
    silver = pd.read_parquet("data/silver_gamestate_labeled.parquet")

    model = joblib.load("model/winprob_model.pkl")
    gold["home_win_prob"] = model.predict_proba(gold[FEATURES])[:, 1]

    key = ["game_pk", "at_bat_number", "pitch_number"]
    df = gold.merge(
        silver[key + ["batter", "pitcher", "player_name"]],
        on=key, how="left"
    )
    df = df.sort_values(["game_pk", "at_bat_number", "pitch_number"])

    pa_start = df.groupby(["game_pk", "at_bat_number"]).head(1).copy()
    pa_start = pa_start.sort_values(["game_pk", "at_bat_number"])

    pa_start["win_prob_after"] = pa_start.groupby("game_pk")["home_win_prob"].shift(-1)

    last_idx = pa_start.groupby("game_pk")["at_bat_number"].idxmax()
    pa_start.loc[last_idx, "win_prob_after"] = pa_start.loc[last_idx, "home_win"].astype(float)

    raw_delta = pa_start["win_prob_after"] - pa_start["home_win_prob"]
    pa_start["wpa"] = np.where(pa_start["is_home_batting"] == 1, raw_delta, -raw_delta)

    batter_wpa = pa_start.groupby(["batter", "season"])["wpa"].agg(["sum", "count"]).reset_index()
    batter_wpa.columns = ["player_id", "season", "total_wpa", "plate_appearances"]
    batter_wpa["role"] = "batter"

    pitcher_wpa = pa_start.groupby(["pitcher", "season"])["wpa"].agg(["sum", "count"]).reset_index()
    pitcher_wpa.columns = ["player_id", "season", "total_wpa", "plate_appearances"]
    pitcher_wpa["total_wpa"] = -pitcher_wpa["total_wpa"]
    pitcher_wpa["role"] = "pitcher"

    wpa_leaderboard = pd.concat([batter_wpa, pitcher_wpa], ignore_index=True)
    wpa_leaderboard = wpa_leaderboard[wpa_leaderboard["plate_appearances"] >= 200]
    wpa_leaderboard = wpa_leaderboard.sort_values("total_wpa", ascending=False)

    wpa_leaderboard.to_parquet("data/gold_wpa_leaderboard.parquet", index=False)

    print(f"Computed WPA for {len(wpa_leaderboard):,} player-seasons (min 200 PA/batters faced)")
    print("\nTop 10 batter-seasons by WPA:")
    print(wpa_leaderboard[wpa_leaderboard["role"] == "batter"].head(10).to_string(index=False))
    print("\nTop 10 pitcher-seasons by WPA:")
    print(wpa_leaderboard[wpa_leaderboard["role"] == "pitcher"].head(10).to_string(index=False))
    print("\nBottom 5 pitcher-seasons for contrast:")
    print(wpa_leaderboard[wpa_leaderboard["role"] == "pitcher"].tail(5).to_string(index=False))

if __name__ == "__main__":
    main()
