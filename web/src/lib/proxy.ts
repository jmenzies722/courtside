import { connection } from "next/server";

// Server-side SSE proxy: browser -> Next.js -> Python API.
// API_URL is read at REQUEST time, so one Docker image works in every environment.
export async function proxyStream(request: Request, path: string) {
  await connection(); // always run per request, never prerender
  const apiUrl = process.env.API_URL ?? "http://localhost:8000";
  const upstream = await fetch(`${apiUrl}${path}`, { signal: request.signal }).catch(() => null);
  if (!upstream?.ok || !upstream.body) {
    return new Response("API unavailable", { status: upstream?.status === 404 ? 404 : 503 });
  }
  return new Response(upstream.body, {
    headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache, no-transform" },
  });
}
