"use client";

import { useState } from "react";
import Link from "next/link";
import { LineChart, Line, XAxis, YAxis, ReferenceLine, ResponsiveContainer, Tooltip } from "recharts";
import type { GameReplay } from "@/lib/api";

export default function GameReplayClient({ replay }: { replay: GameReplay }) {
  const [pitchIndex, setPitchIndex] = useState(replay.pitches.length - 1);

  const current = replay.pitches[pitchIndex];
  const homeProb = current.home_win_prob;
  const awayProb = 1 - homeProb;

  const chartData = replay.pitches.map((p, i) => ({
    idx: i,
    winProb: p.home_win_prob * 100,
  }));

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100 px-6 py-10">
      <div className="max-w-3xl mx-auto">
        <Link href="/" className="text-neutral-500 hover:text-neutral-300 text-sm">
          &larr; Back to leaderboard
        </Link>

        <h1 className="text-2xl font-bold mt-3 mb-1">
          {replay.away_team} @ {replay.home_team}
        </h1>
        <p className="text-neutral-500 mb-8">{replay.game_date}</p>

        {/* Live-style win probability bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm mb-2">
            <span className="font-semibold">{replay.away_team} {(awayProb * 100).toFixed(1)}%</span>
            <span className="font-semibold">{replay.home_team} {(homeProb * 100).toFixed(1)}%</span>
          </div>
          <div className="h-10 rounded-lg overflow-hidden flex border border-neutral-800">
            <div
              className="bg-red-500 transition-all duration-200"
              style={{ width: `${awayProb * 100}%` }}
            />
            <div
              className="bg-emerald-500 transition-all duration-200"
              style={{ width: `${homeProb * 100}%` }}
            />
          </div>
          <div className="text-xs text-neutral-500 mt-2">
            Inning {current.inning}, {current.is_home_batting ? "bottom" : "top"},{" "}
            {current.outs_when_up} out{current.outs_when_up !== 1 ? "s" : ""}
          </div>
        </div>

        {/* Full game trajectory chart */}
        <div className="h-64 mb-6 bg-neutral-900 rounded-lg border border-neutral-800 p-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <XAxis dataKey="idx" hide />
              <YAxis domain={[0, 100]} stroke="#666" tick={{ fontSize: 11 }} />
              <ReferenceLine y={50} stroke="#444" strokeDasharray="3 3" />
              <Tooltip
                contentStyle={{ background: "#171717", border: "1px solid #333" }}
                labelFormatter={() => ""}
                formatter={(v) => [`${Number(v).toFixed(1)}%`, `${replay.home_team} win prob`]}
              />
              <Line
                type="monotone"
                dataKey="winProb"
                stroke="#34d399"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Scrubber */}
        <input
          type="range"
          min={0}
          max={replay.pitches.length - 1}
          value={pitchIndex}
          onChange={(e) => setPitchIndex(parseInt(e.target.value))}
          className="w-full accent-emerald-500"
        />
        <div className="flex justify-between text-xs text-neutral-500 mt-1">
          <span>Start of game</span>
          <span>Plate appearance {pitchIndex + 1} of {replay.pitches.length}</span>
          <span>Final</span>
        </div>
      </div>
    </main>
  );
}
