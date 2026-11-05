"use client";
import { useState } from "react";
import Link from "next/link";
import type { GameEvent, GameWithOdds } from "@/lib/types";
import { team } from "@/lib/teams";
import { ageSeconds, health, periodLabel, replayLabel } from "@/lib/slo";
import { HealthDot } from "./HealthDot";

// A score that flashes orange when it changes (not on first render).
// key={value} remounts the <span> on each new score, which replays the CSS animation.
function Score({ value, hidden }: { value: number; hidden: boolean }) {
  const [first] = useState(value);
  const changed = value !== first;
  return (
    <span key={value} className={`rounded-lg px-1.5 font-mono text-3xl font-bold tabular-nums ${changed ? "animate-flash" : ""}`}>
      {hidden ? "–" : value}
    </span>
  );
}

function TeamRow({ game, side }: { game: GameEvent; side: "home" | "away" }) {
  const code = game[side];
  const { name, color } = team(code);
  const mine = side === "home" ? game.home_score : game.away_score;
  const theirs = side === "home" ? game.away_score : game.home_score;
  const trailing = game.status !== "pre" && mine < theirs;
  return (
    <div className={`grid grid-cols-[40px_1fr_auto] items-center gap-3 py-1.5 ${trailing ? "text-slate-400" : ""}`}>
      <div className="grid size-10 place-items-center rounded-xl text-xs font-extrabold text-white shadow-inner" style={{ background: color }}>
        {code}
      </div>
      <div>
        <div className="font-semibold">{code}</div>
        <div className="text-sm text-slate-400">{name}{side === "home" && " · home"}</div>
      </div>
      <Score value={mine} hidden={game.status === "pre"} />
    </div>
  );
}

function Status({ game }: { game: GameEvent }) {
  if (game.status === "in" && game.replay_of)   // honest label: recorded game, not happening now
    return (
      <span className="inline-flex items-center gap-1.5 font-semibold text-amber-300">
        ⏵ Replay {replayLabel(game.replay_of)} · {periodLabel(game.period)} {game.clock}
      </span>
    );
  if (game.status === "in")
    return (
      <span className="inline-flex items-center gap-1.5 font-semibold text-red-400">
        <HealthDot health="bad" pulse /> Live · {periodLabel(game.period)} {game.clock}
      </span>
    );
  if (game.status === "post")
    return <span className="font-semibold">Final{game.period > 4 && ` / ${periodLabel(game.period)}`}</span>;
  return <span className="font-semibold">Tip-off soon</span>;
}

// Win-probability bar: away colour on the left, home colour on the right.
function OddsBar({ game }: { game: GameWithOdds }) {
  const home = Math.round(game.home_wp * 100);
  return (
    <div className="mt-2">
      <div className="flex h-1.5 overflow-hidden rounded-full bg-slate-800">
        <div style={{ width: `${100 - home}%`, background: team(game.away).color }} />
        <div style={{ width: `${home}%`, background: team(game.home).color }} />
      </div>
      <div className="mt-1 flex justify-between font-mono text-[11px] text-slate-400">
        <span>{game.away} {100 - home}%</span><span>win probability</span><span>{game.home} {home}%</span>
      </div>
    </div>
  );
}

export function GameCard({ game, now }: { game: GameWithOdds; now: number }) {
  const age = ageSeconds(game.fetched_at, now);
  return (
    <Link href={`/games/${game.game_id}`} className={`block rounded-2xl border bg-gradient-to-b from-slate-900 to-slate-950 p-4 transition hover:-translate-y-0.5 hover:border-slate-500 ${
      game.status === "in" ? "border-red-500/35" : "border-slate-800"}`}>
      <div className="mb-3 flex items-center justify-between text-xs uppercase tracking-wider text-slate-400">
        <Status game={game} />
        <span>{game.game_id}</span>
      </div>
      <TeamRow game={game} side="away" />
      <TeamRow game={game} side="home" />
      {game.status !== "pre" && <OddsBar game={game} />}
      <div className="mt-2.5 flex justify-between border-t border-dashed border-slate-800 pt-2.5 text-xs text-slate-400">
        <span>Data age</span>
        <span className="inline-flex items-center gap-1.5 font-mono">
          <HealthDot health={health(age)} /> {age.toFixed(0)}s
        </span>
      </div>
    </Link>
  );
}
