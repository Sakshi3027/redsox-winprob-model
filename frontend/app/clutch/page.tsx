import ClutchClient from "./ClutchClient";

async function getClutchLeaderboard(limit = 15) {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${API_BASE}/leaderboard/clutch?limit=${limit}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch clutch leaderboard");
  return res.json();
}

export default async function ClutchPage() {
  const clutch = await getClutchLeaderboard(15);
  return <ClutchClient data={clutch} />;
}
