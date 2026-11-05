"use client";
import { useEffect, useState } from "react";
import type { GameDetail, GameWithOdds } from "@/lib/types";

export type Connection = "connecting" | "live" | "reconnecting";

// One open connection (Server-Sent Events). The server pushes fresh data on every change.
export function useSSE<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [connection, setConnection] = useState<Connection>("connecting");

  useEffect(() => {
    const es = new EventSource(url);
    es.onopen = () => setConnection("live");
    es.onmessage = (e) => setData(JSON.parse(e.data));
    es.onerror = () => setConnection("reconnecting"); // EventSource retries on its own
    return () => es.close(); // cleanup on unmount: no leaked connections
  }, [url]);

  return { data, connection };
}

export function useGameStream() {
  const { data, connection } = useSSE<GameWithOdds[]>("/api/stream");
  return { games: data ?? [], connection };
}

export function useGameDetail(id: string) {
  return useSSE<GameDetail>(`/api/games/${encodeURIComponent(id)}/stream`);
}

// Re-render every second so "data age" counters move.
// Starts at 0 and reads the clock only in the browser (inside the interval): reading
// Date.now() during render would freeze the server's prerender time into the page.
export function useNow(intervalMs = 1000) {
  const [now, setNow] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
  return now;
}
