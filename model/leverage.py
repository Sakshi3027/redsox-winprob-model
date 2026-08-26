"""
model/leverage.py
Computes Leverage Index per game state and a high-leverage ("clutch") leaderboard.
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
    pa_start["abs_wpa"] = pa_start["wpa"].abs()

    pa_start["score_bucket"] = pa_start["home_score_diff"].clip(-4, 4)

    league_avg_swing = pa_start["abs_wpa"].mean()
    print(f"League average |WPA| per PA: {league_avg_swing:.5f}")

    state_cols = ["inning", "base_out_state", "score_bucket"]
    state_leverage = pa_start.groupby(state_cols)["abs_wpa"].agg(["mean", "count"]).reset_index()
    state_leverage.columns = state_cols + ["avg_swing", "n_pa"]
    state_leverage = state_leverage[state_leverage["n_pa"] >= 30]
    state_leverage["leverage_index"] = state_leverage["avg_swing"] / league_avg_swing

    pa_start = pa_start.merge(state_leverage[state_cols + ["leverage_index"]], on=state_cols, how="left")

    pa_start.to_parquet("data/gold_pa_leverage.parquet", index=False)
    state_leverage.to_parquet("data/gold_leverage_table.parquet", index=False)

    print(f"\nComputed leverage index for {len(state_leverage):,} distinct game states")
    print("\nHighest leverage states:")
    top_states = state_leverage.sort_values("leverage_index", ascending=False).head(10)
    print(top_states.to_string(index=False))
    print("\nLowest leverage states:")
    bottom_states = state_leverage.sort_values("leverage_index", ascending=True).head(10)
    print(bottom_states.to_string(index=False))

    high_lev_threshold = pa_start["leverage_index"].quantile(0.75)
    high_lev = pa_start[pa_start["leverage_index"] >= high_lev_threshold]
    clutch_batters = high_lev.groupby("batter")["wpa"].agg(["sum", "count"]).reset_index()
    clutch_batters.columns = ["player_id", "high_leverage_wpa", "high_leverage_pa"]
    clutch_batters = clutch_batters[clutch_batters["high_leverage_pa"] >= 30]
    clutch_batters = clutch_batters.sort_values("high_leverage_wpa", ascending=False)
    clutch_batters.to_parquet("data/gold_clutch_leaderboard.parquet", index=False)

    print(f"\nTop 10 batters by high-leverage WPA (top-quartile leverage, min 30 PA):")
    print(clutch_batters.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
