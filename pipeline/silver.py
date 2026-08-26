"""
pipeline/silver.py
Derives game outcomes from bronze data and filters to complete, valid games.
"""
import pandas as pd

def main():
    df = pd.read_parquet("data/bronze_statcast_gamestate.parquet")
    print(f"Loaded {len(df):,} pitches across {df['game_pk'].nunique():,} games")

    final_pitches = df.groupby("game_pk").tail(1)[
        ["game_pk", "home_team", "away_team", "post_home_score", "post_away_score"]
    ].copy()

    final_pitches["home_win"] = (
        final_pitches["post_home_score"] > final_pitches["post_away_score"]
    ).astype(int)

    ties = final_pitches[
        final_pitches["post_home_score"] == final_pitches["post_away_score"]
    ]
    print(f"Dropping {len(ties)} games with no clear final score (ties/incomplete)")
    valid_games = final_pitches[
        final_pitches["post_home_score"] != final_pitches["post_away_score"]
    ]["game_pk"]

    df = df[df["game_pk"].isin(valid_games)].copy()

    outcome_map = final_pitches.set_index("game_pk")["home_win"]
    df["home_win"] = df["game_pk"].map(outcome_map)

    pitch_counts = df.groupby("game_pk").size()
    thin_games = pitch_counts[pitch_counts < 100].index
    print(f"Dropping {len(thin_games)} games with under 100 pitches (likely incomplete)")
    df = df[~df["game_pk"].isin(thin_games)]

    print(f"\nFinal: {len(df):,} pitches across {df['game_pk'].nunique():,} valid games")
    print(f"Home team win rate: {df.groupby('game_pk')['home_win'].first().mean():.3f}")

    df.to_parquet("data/silver_gamestate_labeled.parquet", index=False)
    print("Saved to data/silver_gamestate_labeled.parquet")

if __name__ == "__main__":
    main()
