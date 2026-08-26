"""
model/calibrate.py
Validates calibration of the win probability model.
"""
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve

FEATURES = [
    "inning", "is_home_batting", "half_inning_num",
    "outs_when_up", "base_state", "base_out_state",
    "balls", "strikes", "home_score_diff",
]

def main():
    df = pd.read_parquet("data/gold_features.parquet")
    test = df[df["season"] == 2024]

    model = joblib.load("model/winprob_model.pkl")
    probs = model.predict_proba(test[FEATURES])[:, 1]
    y_true = test["home_win"].values

    frac_pos, mean_pred = calibration_curve(y_true, probs, n_bins=10, strategy="quantile")

    print("Overall calibration (predicted vs actual):")
    for p, a in zip(mean_pred, frac_pos):
        print(f"  Predicted {p:.3f} -> Actual {a:.3f} (diff: {abs(p-a):.3f})")

    print("\nCalibration by inning group:")
    for label, mask in [
        ("Innings 1-3", test["inning"] <= 3),
        ("Innings 4-6", (test["inning"] > 3) & (test["inning"] <= 6)),
        ("Innings 7-9+", test["inning"] > 6),
    ]:
        phase_probs = probs[mask.values]
        phase_true = y_true[mask.values]
        if len(phase_probs) > 0:
            frac_pos_p, mean_pred_p = calibration_curve(
                phase_true, phase_probs, n_bins=10, strategy="quantile"
            )
            avg_diff = np.mean(np.abs(frac_pos_p - mean_pred_p))
            print(f"  {label}: avg calibration error = {avg_diff:.4f}")

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    ax.plot(mean_pred, frac_pos, "o-", label="Model")
    ax.set_xlabel("Predicted win probability")
    ax.set_ylabel("Actual win rate")
    ax.set_title("Win Probability Calibration (2024 test set)")
    ax.legend()
    plt.tight_layout()
    plt.savefig("model/calibration_curve.png", dpi=150)
    print("\nSaved calibration_curve.png")

if __name__ == "__main__":
    main()
