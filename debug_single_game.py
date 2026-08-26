"""
debug_single_game.py
Traces one real 2024 game pitch by pitch to manually verify WPA logic.
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
        silver[key + ["batter", "pitcher", "player_name", "events", "description"]],
        on=key, how="left"
    )
    df = df.sort_values(["game_pk", "at_bat_number", "pitch_number"])

    game_candidates = df.groupby("game_pk")["home_score_diff"].apply(lambda x: x.abs().max())
    close_game = game_candidates[game_candidates <= 2].index[0]

    g = df[df["game_pk"] == close_game].copy()
    print(f"Tracing game_pk {close_game}: {g['home_team'].iloc[0]} vs {g['away_team'].iloc[0]}, "
          f"{g['game_date'].iloc[0]}")
    print(f"Final: home_win = {g['home_win'].iloc[0]}\n")

    pa_end = g.groupby("at_bat_number").tail(1).copy()
    pa_end = pa_end.sort_values("at_bat_number")

    last_idx = pa_end["at_bat_number"].idxmax()
    pa_end.loc[last_idx, "home_win_prob"] = float(pa_end.loc[last_idx, "home_win"])

    pa_end["prev_home_win_prob"] = pa_end["home_win_prob"].shift(1).fillna(0.527)
    raw_delta = pa_end["home_win_prob"] - pa_end["prev_home_win_prob"]
    pa_end["wpa"] = np.where(pa_end["is_home_batting"] == 1, raw_delta, -raw_delta)

    cols = ["at_bat_number", "inning", "is_home_batting", "home_score_diff",
            "batter", "pitcher", "events", "home_win_prob", "wpa"]
    print(pa_end[cols].to_string(index=False))

    print(f"\nTotal batter-credited WPA this game: {pa_end['wpa'].sum():.4f}")

if __name__ == "__main__":
    main()
