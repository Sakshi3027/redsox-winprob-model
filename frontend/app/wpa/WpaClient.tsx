"use client";

import { useState } from "react";
import Link from "next/link";
import type { WpaEntry } from "@/lib/api";

export default function WpaClient({
  batters,
  pitchers,
}: {
  batters: WpaEntry[];
  pitchers: WpaEntry[];
}) {
  const [role, setRole] = useState<"batter" | "pitcher">("batter");
  const data = role === "batter" ? batters : pitchers;
  const maxWpa = Math.max(...data.map((d) => Math.abs(d.total_wpa)));

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100 px-6 py-10">
      <div className="max-w-3xl mx-auto">
        <Link href="/" className="text-neutral-500 hover:text-neutral-300 text-sm">
          &larr; Back to leaderboard
        </Link>

        <h1 className="text-2xl font-bold mt-3 mb-1">Win Probability Added</h1>
        <p className="text-neutral-500 mb-6">
          2024 season, minimum 200 plate appearances / batters faced. WPA measures
          how much a player&apos;s specific plays moved their team&apos;s win probability.
        </p>

        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setRole("batter")}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              role === "batter" ? "bg-emerald-500 text-neutral-950" : "bg-neutral-900 text-neutral-400"
            }`}
          >
            Batters
          </button>
          <button
            onClick={() => setRole("pitcher")}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              role === "pitcher" ? "bg-emerald-500 text-neutral-950" : "bg-neutral-900 text-neutral-400"
            }`}
          >
            Pitchers
          </button>
        </div>

        <div className="space-y-2">
          {data.map((d, i) => (
            <div key={d.player_id} className="flex items-center gap-3">
              <span className="text-neutral-500 text-sm w-5">{i + 1}</span>
              <span className="text-sm w-40 text-neutral-300">{d.full_name}</span>
              <div className="flex-1 bg-neutral-900 rounded h-6 overflow-hidden">
                <div
                  className="bg-emerald-500 h-full flex items-center justify-end px-2"
                  style={{ width: `${(Math.abs(d.total_wpa) / maxWpa) * 100}%` }}
                >
                  <span className="text-xs font-semibold text-neutral-950">
                    {d.total_wpa.toFixed(2)}
                  </span>
                </div>
              </div>
              <span className="text-xs text-neutral-500 w-16">{d.plate_appearances} PA</span>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
