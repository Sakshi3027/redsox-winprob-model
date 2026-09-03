import Link from "next/link";
import { getDramaticGames } from "@/lib/api";

export default async function Home() {
  const games = await getDramaticGames(20);

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100 px-6 py-10">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Win Probability Model</h1>
        <p className="text-neutral-400 mb-6">
          Most dramatic games of the 2024 MLB season, ranked by the biggest single-pitch
          win probability swing.
        </p>

        <nav className="flex gap-3 mb-8">
          <Link
            href="/wpa"
            className="px-4 py-2 bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 rounded-lg text-sm font-medium"
          >
            WPA Leaderboard
          </Link>
          <Link
            href="/clutch"
            className="px-4 py-2 bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 rounded-lg text-sm font-medium"
          >
            Clutch Performance
          </Link>
          <Link
            href="/benchmark"
            className="px-4 py-2 bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 rounded-lg text-sm font-medium"
          >
            Model Benchmark
          </Link>
        </nav>

        <div className="space-y-2">
          {games.map((g) => (
            <Link
              key={g.game_pk}
              href={`/games/${g.game_pk}`}
              className="block bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 rounded-lg px-5 py-4 transition"
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-semibold">{g.away_team}</span>
                  <span className="text-neutral-500 mx-2">@</span>
                  <span className="font-semibold">{g.home_team}</span>
                  <span className="text-neutral-500 ml-3 text-sm">{g.game_date}</span>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-emerald-400">
                    {(g.max_single_pitch_swing * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-neutral-500">win prob swing</div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
