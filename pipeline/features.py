"""
pipeline/features.py
Engineers game-state features for win probability modeling.
"""
import pandas as pd

def encode_base_state(row):
    return (
        (1 if pd.notna(row["on_1b"]) else 0) * 1 +
        (1 if pd.notna(row["on_2b"]) else 0) * 2 +
        (1 if pd.notna(row["on_3b"]) else 0) * 4
    )

def main():
    df = pd.read_parquet("data/silver_gamestate_labeled.parquet")
    print(f"Loaded {len(df):,} pitches")

    df["base_state"] = df.apply(encode_base_state, axis=1)
    df["base_out_state"] = df["base_state"] * 3 + df["outs_when_up"]

    df["score_diff"] = df["bat_score"] - df["fld_score"]
    df["is_home_batting"] = (df["inning_topbot"] == "Bot").astype(int)

    df["home_score_diff"] = df.apply(
        lambda r: r["score_diff"] if r["is_home_batting"] == 1 else -r["score_diff"],
        axis=1
    )

    df["half_inning_num"] = df["inning"] + (df["is_home_batting"] * 0.5)

    feature_cols = [
        "game_pk", "game_date", "season", "home_team", "away_team",
        "at_bat_number", "pitch_number",
        "inning", "is_home_batting", "half_inning_num",
        "outs_when_up", "base_state", "base_out_state",
        "balls", "strikes",
        "home_score_diff",
        "home_win",
    ]
    out = df[feature_cols].copy()

    out.to_parquet("data/gold_features.parquet", index=False)
    print(f"Saved {len(out):,} rows to data/gold_features.parquet")
    print(f"\nFeature preview:")
    print(out.head(10).to_string())

if __name__ == "__main__":
    main()
