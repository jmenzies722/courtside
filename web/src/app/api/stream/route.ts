import { proxyStream } from "@/lib/proxy";

// Scoreboard stream: every game, pushed on every change.
export async function GET(request: Request) {
  return proxyStream(request, "/api/stream");
}
