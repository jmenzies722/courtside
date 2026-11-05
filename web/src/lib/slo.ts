// Freshness SLO: live scores must be no more than 10 seconds behind.
export const FRESHNESS_SLO_SECONDS = 10;

export type Health = "ok" | "warn" | "bad";

export const ageSeconds = (fetchedAt: string, now: number) =>
  Math.max(0, (now - Date.parse(fetchedAt)) / 1000);

// ok = within SLO, warn = up to 3x over, bad = worse than that
export const health = (seconds: number): Health =>
  seconds <= FRESHNESS_SLO_SECONDS ? "ok" : seconds <= FRESHNESS_SLO_SECONDS * 3 ? "warn" : "bad";

export const periodLabel = (p: number) => (p <= 4 ? `Q${p}` : p === 5 ? "OT" : `${p - 4}OT`);
