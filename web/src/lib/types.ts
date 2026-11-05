// Mirrors the GameEvent contract in services/ingest/models.py.
// If one changes, the other must too: that's what a contract means.
export type GameStatus = "pre" | "in" | "post";

export interface GameEvent {
  game_id: string;
  home: string;
  away: string;
  home_score: number;
  away_score: number;
  status: GameStatus;
  period: number;
  clock: string;
  fetched_at: string; // ISO time WE fetched it: the freshness SLO clock
}

// The API adds this to every game: probability the HOME team wins (0..1).
export type GameWithOdds = GameEvent & { home_wp: number };

// Mirrors the Play contract in services/ingest/models.py, plus the API's home_wp.
export interface Play {
  game_id: string;
  seq: number;
  period: number;
  clock: string;
  home_score: number;
  away_score: number;
  team: string | null;
  scoring: boolean;
  points: number;
  text: string;
  wallclock: string;
  home_wp: number;
}

export interface WinProbPoint {
  seq: number;
  t: number;        // game seconds elapsed (0..2880)
  home_wp: number;
}

export interface GameDetail {
  game: GameWithOdds;
  plays: Play[];    // newest first
  wp: WinProbPoint[];
}
