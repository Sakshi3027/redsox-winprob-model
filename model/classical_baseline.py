"""
model/classical_baseline.py
Builds classical empirical win expectancy table and benchmarks XGBoost against it.
"""
import pandas as pd
import numpy as np
from sklearn.metrics import brier_score_loss, log_loss
import joblib

FEATURES = [
    "inning", "is_home_batting", "half_inning_num",
    "outs_when_up", "base_state", "base_out_state",
    "balls", "strikes", "home_score_diff",
]

def main():
    df = pd.read_parquet("data/gold_features.parquet")

    train = df[df["season"].isin([2022, 2023])].copy()
    test = df[df["season"] == 2024].copy()

    train["score_bucket"] = train["home_score_diff"].clip(-6, 6)
    test["score_bucket"] = test["home_score_diff"].clip(-6, 6)

    lookup_cols = ["inning", "is_home_batting", "outs_when_up", "base_state", "score_bucket"]
    lookup_table = train.groupby(lookup_cols)["home_win"].agg(["mean", "count"]).reset_index()
    lookup_table.columns = lookup_cols + ["classical_win_prob", "n_obs"]

    print(f"Classical lookup table: {len(lookup_table):,} distinct states from training data")
    print(f"States with under 30 observations: {(lookup_table['n_obs'] < 30).sum():,}")

    inning_fallback = train.groupby("inning")["home_win"].mean().to_dict()
    global_fallback = train["home_win"].mean()

    test = test.merge(lookup_table[lookup_cols + ["classical_win_prob", "n_obs"]], on=lookup_cols, how="left")

    unreliable = test["n_obs"].isna() | (test["n_obs"] < 30)
    test.loc[unreliable, "classical_win_prob"] = test.loc[unreliable, "inning"].map(inning_fallback).fillna(global_fallback)
    print(f"\n{unreliable.sum():,} test rows ({100*unreliable.mean():.1f}%) used the fallback")

    model = joblib.load("model/winprob_model.pkl")
    test["xgb_win_prob"] = model.predict_proba(test[FEATURES])[:, 1]

    y_test = test["home_win"]

    classical_brier = brier_score_loss(y_test, test["classical_win_prob"])
    xgb_brier = brier_score_loss(y_test, test["xgb_win_prob"])
    classical_logloss = log_loss(y_test, test["classical_win_prob"].clip(0.001, 0.999))
    xgb_logloss = log_loss(y_test, test["xgb_win_prob"])

    print(f"\n{'Metric':<20}{'Classical lookup':>20}{'XGBoost':>15}{'Improvement':>15}")
    print(f"{'Brier score':<20}{classical_brier:>20.4f}{xgb_brier:>15.4f}{100*(classical_brier-xgb_brier)/classical_brier:>14.1f}%")
    print(f"{'Log loss':<20}{classical_logloss:>20.4f}{xgb_logloss:>15.4f}{100*(classical_logloss-xgb_logloss)/classical_logloss:>14.1f}%")

    print("\nBrier score by score margin:")
    for label, mask in [
        ("Close game (0-1 run)", test["home_score_diff"].abs() <= 1),
        ("Moderate (2-4 runs)", (test["home_score_diff"].abs() > 1) & (test["home_score_diff"].abs() <= 4)),
        ("Blowout (5+ runs)", test["home_score_diff"].abs() > 4),
    ]:
        c_brier = brier_score_loss(y_test[mask], test.loc[mask, "classical_win_prob"])
        x_brier = brier_score_loss(y_test[mask], test.loc[mask, "xgb_win_prob"])
        print(f"  {label:<25}: classical={c_brier:.4f}, xgb={x_brier:.4f}, "
              f"improvement={100*(c_brier-x_brier)/c_brier:.1f}%")

    test[["game_pk", "inning", "home_score_diff", "classical_win_prob", "xgb_win_prob", "home_win"]].to_parquet(
        "data/gold_baseline_comparison.parquet", index=False
    )
    print("\nSaved comparison data to data/gold_baseline_comparison.parquet")

if __name__ == "__main__":
    main()
