"use client";
import { useState } from "react";
import type { GameStatus } from "@/lib/types";
import { useGameStream, useNow } from "@/hooks/useGameStream";
import { ageSeconds, health, FRESHNESS_SLO_SECONDS, replayLabel } from "@/lib/slo";
import { GameCard } from "./GameCard";
import { HealthDot } from "./HealthDot";

type Filter = "all" | GameStatus;
const FILTERS: { id: Filter; label: string }[] = [
  { id: "all", label: "All" }, { id: "in", label: "Live" }, { id: "post", label: "Final" },
];

function Pill({ children, title }: { children: React.ReactNode; title?: string }) {
  return (
    <span title={title} className="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900 px-3 py-1.5 text-sm text-slate-400">
      {children}
    </span>
  );
}

export function Scoreboard() {
  const { games, connection } = useGameStream();
  const now = useNow();
  const [filter, setFilter] = useState<Filter>("all");

  const live = games.filter((g) => g.status === "in");
  // The SLO is about LIVE games: a final score that's an hour old is fine.
  const worst = Math.max(0, ...live.map((g) => ageSeconds(g.fetched_at, now)));
  const shown = games.filter((g) => filter === "all" || g.status === filter);

  return (
    <>
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex gap-1.5" role="group" aria-label="Filter games">
          {FILTERS.map((f) => (
            <button key={f.id} onClick={() => setFilter(f.id)} aria-pressed={filter === f.id}
              className="rounded-lg border border-slate-800 px-3.5 py-1.5 text-sm text-slate-400 aria-pressed:border-slate-600 aria-pressed:bg-slate-800 aria-pressed:text-white">
              {f.label}
            </button>
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          <Pill>
            <HealthDot health={connection === "live" ? "ok" : connection === "reconnecting" ? "warn" : "idle"} pulse={connection === "live"} />
            {connection === "live" ? "Live" : connection === "reconnecting" ? "Reconnecting…" : "Connecting…"}
          </Pill>
          <Pill title={`Freshness SLO: live scores no more than ${FRESHNESS_SLO_SECONDS}s behind`}>
            <HealthDot health={live.length ? health(worst) : "idle"} />
            Freshness <b className="font-mono text-white">{live.length ? `${worst.toFixed(0)}s` : "–"}</b> / {FRESHNESS_SLO_SECONDS}s
          </Pill>
        </div>
      </div>

      {games.some((g) => g.replay_of) && (
        <div className="mb-4 rounded-xl border border-amber-400/30 bg-amber-400/10 px-4 py-2.5 text-sm text-amber-200">
          ⏵ <b>Replay mode:</b> real games from {replayLabel(games.find((g) => g.replay_of)!.replay_of!)}, played back through the live pipeline.
          Tonight&apos;s games appear live when ingest runs with <code className="rounded bg-black/30 px-1">SOURCE=espn</code>.
        </div>
      )}

      {shown.length ? (
        <div className="grid gap-3.5 [grid-template-columns:repeat(auto-fill,minmax(300px,1fr))]">
          {shown.map((g) => <GameCard key={g.game_id} game={g} now={now} />)}
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-slate-800 px-4 py-16 text-center text-slate-400">
          No games here yet.
          <div className="mt-3">Replay a real night with <code className="rounded bg-slate-800 px-1.5 py-0.5 text-white">make record && make ingest</code></div>
        </div>
      )}
    </>
  );
}
