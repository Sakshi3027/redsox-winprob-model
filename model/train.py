"""
model/train.py
Trains XGBoost classifier for win probability, temporal split by season.
"""
import pandas as pd
import xgboost as xgb
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
import joblib

FEATURES = [
    "inning", "is_home_batting", "half_inning_num",
    "outs_when_up", "base_state", "base_out_state",
    "balls", "strikes", "home_score_diff",
]

def main():
    df = pd.read_parquet("data/gold_features.parquet")

    train = df[df["season"].isin([2022, 2023])]
    test = df[df["season"] == 2024]
    print(f"Train: {len(train):,} pitches | Test: {len(test):,} pitches")

    X_train, y_train = train[FEATURES], train["home_win"]
    X_test, y_test = test[FEATURES], test["home_win"]

    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    probs = model.predict_proba(X_test)[:, 1]

    print(f"\nBrier score: {brier_score_loss(y_test, probs):.4f}")
    print(f"Log loss: {log_loss(y_test, probs):.4f}")
    print(f"AUC: {roc_auc_score(y_test, probs):.4f}")

    first_pitch = test.groupby("game_pk").head(1)
    first_pitch_probs = model.predict_proba(first_pitch[FEATURES])[:, 1]
    print(f"\nMean predicted win prob at first pitch: {first_pitch_probs.mean():.4f}")
    print(f"(Should be close to home field advantage baseline ~0.527)")

    joblib.dump(model, "model/winprob_model.pkl")
    print("\nSaved model to model/winprob_model.pkl")

if __name__ == "__main__":
    main()
