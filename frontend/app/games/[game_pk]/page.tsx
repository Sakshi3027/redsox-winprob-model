import { getGameReplay } from "@/lib/api";
import GameReplayClient from "./GameReplayClient";

export default async function GamePage({
  params,
}: {
  params: Promise<{ game_pk: string }>;
}) {
  const { game_pk } = await params;
  const replay = await getGameReplay(parseInt(game_pk));

  return <GameReplayClient replay={replay} />;
}
