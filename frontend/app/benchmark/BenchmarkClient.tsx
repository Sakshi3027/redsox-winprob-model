"use client";

import Link from "next/link";

interface Benchmark {
  n_predictions: number;
  classical_brier: number;
  xgb_brier: number;
}

const SEGMENT_DATA = [
  { label: "Close game (0-1 run)", classical: 0.2308, xgb: 0.2294, improvement: 0.6 },
  { label: "Moderate (2-4 runs)", classical: 0.1169, xgb: 0.1123, improvement: 3.9 },
  { label: "Blowout (5+ runs)", classical: 0.0316, xgb: 0.0232, improvement: 26.4 },
];

export default function BenchmarkClient({ benchmark }: { benchmark: Benchmark }) {
  const overallImprovement =
    (100 * (benchmark.classical_brier - benchmark.xgb_brier)) / benchmark.classical_brier;

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100 px-6 py-10">
      <div className="max-w-3xl mx-auto">
        <Link href="/" className="text-neutral-500 hover:text-neutral-300 text-sm">
          &larr; Back to leaderboard
        </Link>

        <h1 className="text-2xl font-bold mt-3 mb-1">XGBoost vs. Classical Win Expectancy</h1>
        <p className="text-neutral-500 mb-8">
          Before machine learning, sabermetricians built win expectancy from empirical lookup
          tables: bucket every historical game by inning, score, and base-out state, and use
          the actual historical win rate in that bucket. This compares that classical approach,
          trained on the same 2022-2023 data, against the XGBoost model, evaluated on the same
          2024 test set.
        </p>

        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-5">
            <div className="text-neutral-500 text-sm mb-1">Classical lookup table</div>
            <div className="text-3xl font-bold">{benchmark.classical_brier.toFixed(4)}</div>
            <div className="text-neutral-600 text-xs mt-1">Brier score (lower is better)</div>
          </div>
          <div className="bg-neutral-900 border border-emerald-800 rounded-lg p-5">
            <div className="text-emerald-400 text-sm mb-1">XGBoost model</div>
            <div className="text-3xl font-bold text-emerald-400">{benchmark.xgb_brier.toFixed(4)}</div>
            <div className="text-neutral-600 text-xs mt-1">
              {overallImprovement.toFixed(1)}% improvement overall
            </div>
          </div>
        </div>

        <h2 className="text-lg font-semibold mb-3">Where the model actually wins</h2>
        <p className="text-neutral-500 text-sm mb-4">
          The overall improvement is modest, because in close games both methods already
          know it&apos;s close to a coin flip. The real gap opens in lopsided games: the classical
          table has to bucket score margin coarsely to keep enough historical games per bucket,
          so a 6-run game and an 11-run game get treated the same. XGBoost treats score
          differential continuously, so it can tell &quot;still theoretically alive&quot; apart from
          &quot;mathematically over&quot; with far more precision.
        </p>

        <div className="space-y-3">
          {SEGMENT_DATA.map((seg) => (
            <div key={seg.label} className="bg-neutral-900 border border-neutral-800 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">{seg.label}</span>
                <span className="text-emerald-400 text-sm font-semibold">
                  +{seg.improvement.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-neutral-800 rounded h-2 overflow-hidden">
                <div
                  className="bg-emerald-500 h-full"
                  style={{ width: `${seg.improvement * 3.5}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-neutral-600 mt-1">
                <span>classical {seg.classical.toFixed(4)}</span>
                <span>xgb {seg.xgb.toFixed(4)}</span>
              </div>
            </div>
          ))}
        </div>

        <p className="text-neutral-600 text-xs mt-8">
          Evaluated on {benchmark.n_predictions.toLocaleString()} pitches from the 2024 season,
          held out from training entirely.
        </p>
      </div>
    </main>
  );
}
