import type { Health } from "@/lib/slo";

const COLORS: Record<Health | "idle", string> = {
  ok: "bg-emerald-400", warn: "bg-amber-400", bad: "bg-red-500", idle: "bg-slate-500",
};

export function HealthDot({ health, pulse = false }: { health: Health | "idle"; pulse?: boolean }) {
  return <span className={`inline-block size-2 rounded-full ${COLORS[health]} ${pulse ? "animate-pulse" : ""}`} />;
}
