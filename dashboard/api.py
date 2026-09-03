"""
dashboard/api.py
FastAPI backend serving the win probability dashboard.
"""
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI(title="Red Sox Win Probability API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("data")

# Load once at startup, not per-request
replay_df = pd.read_parquet(DATA_DIR / "gold_replay_timeseries.parquet")
leaderboard_df = pd.read_parquet(DATA_DIR / "gold_leaderboard.parquet")
wpa_df = pd.read_parquet(DATA_DIR / "gold_wpa_leaderboard.parquet")
clutch_df = pd.read_parquet(DATA_DIR / "gold_clutch_leaderboard.parquet")
leverage_table_df = pd.read_parquet(DATA_DIR / "gold_leverage_table.parquet")
baseline_df = pd.read_parquet(DATA_DIR / "gold_baseline_comparison.parquet")
names_df = pd.read_parquet(DATA_DIR / "player_names.parquet")

wpa_df = wpa_df.merge(names_df, on="player_id", how="left")
wpa_df["full_name"] = wpa_df["full_name"].fillna("Unknown Player")

clutch_df = clutch_df.merge(names_df, on="player_id", how="left")
clutch_df["full_name"] = clutch_df["full_name"].fillna("Unknown Player")

@app.get("/")
def root():
    return {"status": "ok", "games_available": int(replay_df["game_pk"].nunique())}


@app.get("/games")
def list_games(limit: int = 50):
    games = replay_df[["game_pk", "game_date", "home_team", "away_team"]].drop_duplicates()
    games = games.sort_values("game_date", ascending=False).head(limit)
    return games.to_dict(orient="records")


@app.get("/games/{game_pk}/replay")
def get_game_replay(game_pk: int):
    game = replay_df[replay_df["game_pk"] == game_pk].copy()
    if game.empty:
        raise HTTPException(status_code=404, detail="Game not found")
    game = game.sort_values(["inning", "is_home_batting"])
    return {
        "game_pk": game_pk,
        "home_team": game["home_team"].iloc[0],
        "away_team": game["away_team"].iloc[0],
        "game_date": str(game["game_date"].iloc[0]),
        "home_win": int(game["home_win"].iloc[0]),
        "pitches": game[[
            "inning", "is_home_batting", "outs_when_up",
            "home_score_diff", "home_win_prob"
        ]].to_dict(orient="records"),
    }


@app.get("/leaderboard/dramatic")
def get_dramatic_games(limit: int = 20):
    top = leaderboard_df.sort_values("max_single_pitch_swing", ascending=False).head(limit)
    return top.to_dict(orient="records")


@app.get("/leaderboard/comebacks")
def get_biggest_comebacks(limit: int = 20):
    top = leaderboard_df.sort_values("biggest_deficit_overcome", ascending=False).head(limit)
    return top.to_dict(orient="records")


@app.get("/leaderboard/wpa")
def get_wpa_leaderboard(role: str = "batter", limit: int = 20):
    if role not in ("batter", "pitcher"):
        raise HTTPException(status_code=400, detail="role must be 'batter' or 'pitcher'")
    top = wpa_df[wpa_df["role"] == role].sort_values("total_wpa", ascending=False).head(limit)
    return top.to_dict(orient="records")


@app.get("/leaderboard/clutch")
def get_clutch_leaderboard(limit: int = 20):
    top = clutch_df.sort_values("high_leverage_wpa", ascending=False).head(limit)
    return top.to_dict(orient="records")


@app.get("/leverage/table")
def get_leverage_table():
    return leverage_table_df.sort_values("leverage_index", ascending=False).to_dict(orient="records")


@app.get("/benchmark")
def get_benchmark():
    from sklearn.metrics import brier_score_loss
    y = baseline_df["home_win"]
    return {
        "n_predictions": len(baseline_df),
        "classical_brier": round(brier_score_loss(y, baseline_df["classical_win_prob"]), 4),
        "xgb_brier": round(brier_score_loss(y, baseline_df["xgb_win_prob"]), 4),
    }
