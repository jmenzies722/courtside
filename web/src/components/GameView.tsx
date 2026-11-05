"use client";
import Link from "next/link";
import { useGameDetail } from "@/hooks/useGameStream";
import { team } from "@/lib/teams";
import { periodLabel, replayLabel } from "@/lib/slo";
import { WinProbChart } from "./WinProbChart";
import { PlayFeed } from "./PlayFeed";
import { HealthDot } from "./HealthDot";

export function GameView({ id }: { id: string }) {
  const { data, connection } = useGameDetail(id);

  if (!data) {
    return <p className="py-16 text-center text-slate-400">{connection === "reconnecting" ? "Game not found or API down…" : "Loading game…"}</p>;
  }
  const { game, plays, wp } = data;
  const home = team(game.home), away = team(game.away);
  const homePct = Math.round(game.home_wp * 100);
  // Clutch time: last 5 minutes (or overtime) and within 5 points
  const clutch = game.status === "in" && game.period >= 4 && Math.abs(game.home_score - game.away_score) <= 5
    && (game.period > 4 || parseInt(game.clock) < 5);

  return (
    <>
      <Link href="/" className="text-sm text-slate-400 hover:text-white">← Scoreboard</Link>

      <section className="mt-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
        <div className="mb-4 flex items-center justify-between text-xs uppercase tracking-wider text-slate-400">
          <span className="inline-flex items-center gap-1.5">
            {game.status === "in" && !game.replay_of && <HealthDot health="bad" pulse />}
            {game.status === "in"
              ? `${game.replay_of ? `⏵ Replay of ${replayLabel(game.replay_of)}` : "Live"} · ${periodLabel(game.period)} ${game.clock}`
              : game.status === "post" ? `Final${game.replay_of ? ` · ${replayLabel(game.replay_of)}` : ""}` : "Tip-off soon"}
          </span>
          {clutch && <span className="animate-pulse rounded-full bg-orange-500/20 px-3 py-1 font-bold text-orange-300">🔥 Clutch time</span>}
        </div>
        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4 text-center">
          <div>
            <div className="mx-auto mb-2 grid size-14 place-items-center rounded-2xl text-sm font-extrabold text-white" style={{ background: away.color }}>{game.away}</div>
            <div className="text-slate-400">{away.name}</div>
          </div>
          <div className="font-mono text-5xl font-bold tabular-nums">{game.away_score}<span className="mx-3 text-slate-600">–</span>{game.home_score}</div>
          <div>
            <div className="mx-auto mb-2 grid size-14 place-items-center rounded-2xl text-sm font-extrabold text-white" style={{ background: home.color }}>{game.home}</div>
            <div className="text-slate-400">{home.name} · home</div>
          </div>
        </div>
      </section>

      <section className="mt-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
        <div className="mb-2 flex items-baseline justify-between">
          <h2 className="font-semibold">Win probability</h2>
          <span className="font-mono text-sm">
            <span style={{ color: homePct >= 50 ? "white" : undefined }} className="text-slate-400">{game.home} {homePct}%</span>
            <span className="mx-2 text-slate-600">·</span>
            <span className="text-slate-400">{game.away} {100 - homePct}%</span>
          </span>
        </div>
        <WinProbChart points={wp} home={game.home} away={game.away} homeColor={home.color} awayColor={away.color} />
      </section>

      <section className="mt-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
        <h2 className="mb-2 font-semibold">Play-by-play</h2>
        <PlayFeed plays={plays} />
      </section>
    </>
  );
}
