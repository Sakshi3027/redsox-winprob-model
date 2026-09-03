"""
model/resolve_names.py
Maps MLBAM player IDs to real names via pybaseball's chadwick register.
"""
import pandas as pd
from pybaseball import playerid_reverse_lookup

def main():
    wpa = pd.read_parquet("data/gold_wpa_leaderboard.parquet")
    clutch = pd.read_parquet("data/gold_clutch_leaderboard.parquet")

    all_ids = pd.concat([wpa["player_id"], clutch["player_id"]]).unique()
    all_ids = [int(x) for x in all_ids]
    print(f"Resolving names for {len(all_ids)} unique player IDs...")

    lookup = playerid_reverse_lookup(all_ids, key_type="mlbam")
    lookup["full_name"] = (
        lookup["name_first"].str.capitalize() + " " + lookup["name_last"].str.capitalize()
    )
    name_map = lookup[["key_mlbam", "full_name"]].rename(columns={"key_mlbam": "player_id"})

    matched = name_map["player_id"].nunique()
    print(f"Matched {matched} of {len(all_ids)} IDs ({100*matched/len(all_ids):.1f}%)")

    name_map.to_parquet("data/player_names.parquet", index=False)
    print("Saved to data/player_names.parquet")
    print("\nSample:")
    print(name_map.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
