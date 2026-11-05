import type { WinProbPoint } from "@/lib/types";

// Hand-drawn SVG line chart: no chart library needed for one line.
// Above the 50% line = home team favored, below = away team favored.
const W = 640, H = 220, PAD = 24;
const GAME = 2880;

export function WinProbChart({ points, home, away, homeColor, awayColor }: {
  points: WinProbPoint[]; home: string; away: string; homeColor: string; awayColor: string;
}) {
  const x = (t: number) => PAD + (Math.min(t, GAME) / GAME) * (W - 2 * PAD);
  const y = (p: number) => PAD + (1 - p) * (H - 2 * PAD);
  const line = points.map((p, i) => `${i ? "L" : "M"}${x(p.t).toFixed(1)},${y(p.home_wp).toFixed(1)}`).join(" ");
  const last = points.at(-1);
  const mid = y(0.5);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={`Win probability: ${home} vs ${away}`}>
      <defs>
        {/* colour the area by who's ahead: home colour above 50%, away colour below */}
        <clipPath id="above"><rect x="0" y="0" width={W} height={mid} /></clipPath>
        <clipPath id="below"><rect x="0" y={mid} width={W} height={H - mid} /></clipPath>
      </defs>
      {[1, 2, 3].map((q) => (
        <line key={q} x1={x(q * 720)} x2={x(q * 720)} y1={PAD} y2={H - PAD} className="stroke-slate-800" strokeDasharray="3 4" />
      ))}
      <line x1={PAD} x2={W - PAD} y1={mid} y2={mid} className="stroke-slate-600" />
      <text x={PAD} y={PAD - 8} className="fill-slate-400 text-[11px]">{home} 100%</text>
      <text x={PAD} y={H - 6} className="fill-slate-400 text-[11px]">{away} 100%</text>
      {["Q1", "Q2", "Q3", "Q4"].map((q, i) => (
        <text key={q} x={x(i * 720 + 360)} y={H - 6} textAnchor="middle" className="fill-slate-500 text-[11px]">{q}</text>
      ))}
      {last && (
        <>
          <path d={`${line} L${x(last.t)},${mid} L${x(points[0].t)},${mid} Z`} fill={homeColor} opacity=".35" clipPath="url(#above)" />
          <path d={`${line} L${x(last.t)},${mid} L${x(points[0].t)},${mid} Z`} fill={awayColor} opacity=".35" clipPath="url(#below)" />
          <path d={line} fill="none" stroke="white" strokeWidth="2" strokeLinejoin="round" />
          <circle cx={x(last.t)} cy={y(last.home_wp)} r="4" fill="white" />
        </>
      )}
    </svg>
  );
}
