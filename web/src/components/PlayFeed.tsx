import type { Play } from "@/lib/types";
import { team } from "@/lib/teams";
import { periodLabel } from "@/lib/slo";

// Newest play on top. Scoring plays get the team's colour and the points scored.
export function PlayFeed({ plays }: { plays: Play[] }) {
  if (!plays.length) return <p className="py-8 text-center text-slate-400">Waiting for the first play…</p>;
  return (
    <ol className="divide-y divide-slate-800/70">
      {plays.map((p) => (
        <li key={p.seq} className="grid grid-cols-[64px_1fr_auto] items-start gap-3 py-2.5 text-sm">
          <span className="font-mono text-xs text-slate-500">{periodLabel(p.period)} {p.clock}</span>
          <span className={p.scoring ? "font-medium text-white" : "text-slate-300"}>
            {p.scoring && p.team && (
              <span className="mr-2 rounded px-1.5 py-0.5 text-[11px] font-bold text-white" style={{ background: team(p.team).color }}>
                +{p.points} {p.team}
              </span>
            )}
            {p.text}
          </span>
          <span className="font-mono text-xs tabular-nums text-slate-400">{p.away_score}–{p.home_score}</span>
        </li>
      ))}
    </ol>
  );
}
