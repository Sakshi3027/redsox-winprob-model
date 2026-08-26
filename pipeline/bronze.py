"""
pipeline/bronze.py
Pulls raw Statcast data for 2022-2024, keeping only game-state columns
needed for win probability modeling (not pitch physics).
"""
import pandas as pd
from pybaseball import statcast
import time

SEASONS = {
    2022: ("2022-03-01", "2022-11-30"),
    2023: ("2023-03-01", "2023-11-30"),
    2024: ("2024-03-01", "2024-11-30"),
}

KEEP_COLS = [
    "game_pk", "game_date", "game_year",
    "home_team", "away_team",
    "inning", "inning_topbot",
    "outs_when_up",
    "on_1b", "on_2b", "on_3b",
    "balls", "strikes",
    "home_score", "away_score",
    "post_home_score", "post_away_score",
    "bat_score", "fld_score",
    "at_bat_number", "pitch_number",
    "batter", "pitcher", "player_name",
    "events", "description",
]

def pull_season(year, start, end):
    print(f"Pulling {year} ({start} to {end})...")
    df = statcast(start_dt=start, end_dt=end)
    df = df[KEEP_COLS].copy()
    df["season"] = year
    df = df.sort_values(["game_pk", "at_bat_number", "pitch_number"])
    return df

def main():
    all_seasons = []
    for year, (start, end) in SEASONS.items():
        df = pull_season(year, start, end)
        print(f"  {year}: {len(df):,} pitches, {df['game_pk'].nunique():,} games")
        all_seasons.append(df)
        time.sleep(2)

    full = pd.concat(all_seasons, ignore_index=True)
    print(f"\nTotal: {len(full):,} pitches across {full['game_pk'].nunique():,} games")

    full.to_parquet("data/bronze_statcast_gamestate.parquet", index=False)
    print("Saved to data/bronze_statcast_gamestate.parquet")

if __name__ == "__main__":
    main()
