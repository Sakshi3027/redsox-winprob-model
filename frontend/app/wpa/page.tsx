import WpaClient from "./WpaClient";
import { getWpaLeaderboard } from "@/lib/api";

export default async function WpaPage() {
  const [batters, pitchers] = await Promise.all([
    getWpaLeaderboard("batter", 15),
    getWpaLeaderboard("pitcher", 15),
  ]);

  return <WpaClient batters={batters} pitchers={pitchers} />;
}
