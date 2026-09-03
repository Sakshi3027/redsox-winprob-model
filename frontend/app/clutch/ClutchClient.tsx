"use client";

import Link from "next/link";

interface ClutchEntry {
  player_id: number;
  full_name: string;
  high_leverage_wpa: number;
  high_leverage_pa: number;
}

export default function ClutchClient({ data }: { data: ClutchEntry[] }) {
  const maxWpa = Math.max(...data.map((d) => Math.abs(d.high_leverage_wpa)));

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100 px-6 py-10">
      <div className="max-w-3xl mx-auto">
        <Link href="/" className="text-neutral-500 hover:text-neutral-300 text-sm">
          &larr; Back to leaderboard
        </Link>

        <h1 className="text-2xl font-bold mt-3 mb-1">Clutch Performance</h1>
        <p className="text-neutral-500 mb-6">
          WPA earned specifically in top-quartile leverage situations: late innings, close
          score, runners on. Leverage Index measures how much win probability is at stake
          in a given moment, so this isolates performance when the game actually hangs
          in the balance, not just overall production.
        </p>

        <div className="space-y-2">
          {data.map((d, i) => (
            <div key={d.player_id} className="flex items-center gap-3">
              <span className="text-neutral-500 text-sm w-5">{i + 1}</span>
              <span className="text-sm w-40 text-neutral-300">{d.full_name}</span>
              <div className="flex-1 bg-neutral-900 rounded h-6 overflow-hidden">
                <div
                  className="bg-amber-400 h-full flex items-center justify-end px-2"
                  style={{ width: `${(Math.abs(d.high_leverage_wpa) / maxWpa) * 100}%` }}
                >
                  <span className="text-xs font-semibold text-neutral-950">
                    {d.high_leverage_wpa.toFixed(2)}
                  </span>
                </div>
              </div>
              <span className="text-xs text-neutral-500 w-24">{d.high_leverage_pa} high-lev PA</span>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
