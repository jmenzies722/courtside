import { proxyStream } from "@/lib/proxy";

// One game's stream: plays + win probability, pushed on every change.
export async function GET(request: Request, ctx: RouteContext<"/api/games/[id]/stream">) {
  const { id } = await ctx.params;
  return proxyStream(request, `/api/games/${encodeURIComponent(id)}/stream`);
}
