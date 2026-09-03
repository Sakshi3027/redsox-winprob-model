# MLB Win Probability Model

A machine learning system that predicts each team's real-time win probability during an MLB game, built end to end: data pipeline, model, sabermetric analytics layer, and a live dashboard with pitch-by-pitch game replay.

**Live dashboard:** https://redsox-winprob-model-rosy.vercel.app
**API:** https://redsox-winprob-api.onrender.com

Built as a follow-up to [Stuff Model](https://github.com/Sakshi3027/stuff-model), a pitch-quality grading system. Where Stuff Model evaluates pitch physics in isolation, this project models the game itself: score, inning, base-out state, and count, predicting who wins from any point in the game.

## What it does

Given the game state at any pitch (inning, score differential, outs, baserunners, count), the model outputs the home team's probability of winning. This powers:

- **Live-style win probability bar** that updates pitch by pitch on replay
- **Dramatic games leaderboard**, ranked by the biggest single-pitch win probability swing
- **Win Probability Added (WPA)**, crediting individual batters and pitchers for how much their specific plays moved their team's win probability
- **Leverage Index**, quantifying how much win probability is at stake in a given moment, and a resulting clutch performance leaderboard
- **A head-to-head benchmark** against the classical, pre-ML sabermetric approach (empirical win expectancy tables)

## Data and methodology

Built on 2,309,617 real Statcast pitches across 8,033 MLB games (2022-2024 seasons), pulled via `pybaseball`. After filtering incomplete or invalid games, 7,964 games remained, with a 52.7% home win rate, matching MLB's known home field advantage baseline.

**Model:** XGBoost binary classifier, trained on 2022-2023 (1.54M pitches), tested on 2024 (756K pitches held out entirely from training).

**Features:** inning, half-inning, outs, base-out state (24-state encoding standard in sabermetrics), balls, strikes, and score differential from the home team's perspective.

**Results on the 2024 test set:**
- Brier score: 0.158 (in line with published MLB win probability models)
- AUC: 0.849
- Calibration: predicted vs. actual win rate within 2.2 percentage points across every probability bucket, and consistent across early, middle, and late innings

## Beating the classical baseline

Before machine learning, sabermetricians computed win expectancy from empirical lookup tables: bucket every historical game by inning, score, and base-out state, and use the actual historical win rate in that bucket. I built that classical table from the same training data and benchmarked it against the XGBoost model on the same test set.

XGBoost wins by 2.2% overall, but the real story is in the breakdown by score margin:

| Game state | Improvement over classical |
|---|---|
| Close game (0-1 run) | 0.6% |
| Moderate (2-4 runs) | 3.9% |
| Blowout (5+ runs) | 26.4% |

In close games, both methods already know it's close to a coin flip, so there's little room to improve. The gap opens in lopsided games: the classical table has to bucket score margin coarsely to keep enough historical games per bucket, so a 6-run game and an 11-run game get treated identically. XGBoost treats score differential continuously, so it distinguishes "still theoretically alive" from "mathematically over" with far more precision. That's a specific, defensible mechanism, not just "the model is smarter."

## Win Probability Added: a debugging story worth telling

My first WPA implementation put a large win probability swing on an ordinary groundout instead of the play that actually caused it. I traced a single real game pitch by pitch, comparing my computed values against what actually happened, and found the bug: I was reading model predictions from the state *before* the decisive pitch of a plate appearance, not after it resolved. The fix was to anchor each plate appearance's win probability to the state at the start of the *next* plate appearance, since that's where the count resets and the score, outs, and baserunners reflect what actually happened.

After the fix, the top 2024 batter (8.88 WPA) sits just below Barry Bonds' all-time single-season record (12.96, 2004), and the leaderboard's top names are Shohei Ohtani, Juan Soto, and Aaron Judge, the actual top of the 2024 MVP conversation. Pitcher WPA also resolved into a correctly symmetric distribution (top closers and aces in the +3 to +5 range, matching published figures), rather than the uniformly negative, obviously broken numbers the bug had produced.

## Tech stack

**Pipeline:** Python, pandas, pybaseball (Statcast data), bronze/silver/gold medallion architecture
**Model:** XGBoost, scikit-learn (calibration, metrics)
**Validation:** manual game-by-game tracing, calibration curves, classical baseline benchmark
**Backend:** FastAPI, served on Render
**Frontend:** Next.js, TypeScript, Tailwind CSS, Recharts, deployed on Vercel

## Repo structure
pipeline/ bronze (raw Statcast pull) -> silver (outcome labeling) -> gold (features)
model/ training, calibration, WPA, Leverage Index, classical baseline
dashboard/ FastAPI backend
frontend/ Next.js dashboard (leaderboard, replay, WPA, clutch, benchmark)

## Running locally

```bash
# Backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn dashboard.api:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Author

Sakshi Chavan
sakshchavan30@gmail.com
[GitHub](https://github.com/Sakshi3027)
