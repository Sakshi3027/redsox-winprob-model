const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface DramaticGame {
  game_pk: number;
  game_date: string;
  home_team: string;
  away_team: string;
  home_win: number;
  max_single_pitch_swing: number;
  biggest_deficit_overcome: number;
  n_pitches: number;
}

export interface GameReplay {
  game_pk: number;
  home_team: string;
  away_team: string;
  game_date: string;
  home_win: number;
  pitches: {
    inning: number;
    is_home_batting: number;
    outs_when_up: number;
    home_score_diff: number;
    home_win_prob: number;
  }[];
}

export interface WpaEntry {
  player_id: number;
  season: number;
  total_wpa: number;
  plate_appearances: number;
  role: string;
}

export async function getDramaticGames(limit = 20): Promise<DramaticGame[]> {
  const res = await fetch(`${API_BASE}/leaderboard/dramatic?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch dramatic games");
  return res.json();
}

export async function getComebackGames(limit = 20): Promise<DramaticGame[]> {
  const res = await fetch(`${API_BASE}/leaderboard/comebacks?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch comeback games");
  return res.json();
}

export async function getGameReplay(gamePk: number): Promise<GameReplay> {
  const res = await fetch(`${API_BASE}/games/${gamePk}/replay`);
  if (!res.ok) throw new Error("Failed to fetch game replay");
  return res.json();
}

export async function getWpaLeaderboard(role: "batter" | "pitcher", limit = 20): Promise<WpaEntry[]> {
  const res = await fetch(`${API_BASE}/leaderboard/wpa?role=${role}&limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch WPA leaderboard");
  return res.json();
}

export async function getBenchmark(): Promise<{ n_predictions: number; classical_brier: number; xgb_brier: number }> {
  const res = await fetch(`${API_BASE}/benchmark`);
  if (!res.ok) throw new Error("Failed to fetch benchmark");
  return res.json();
}
