import { Suspense } from "react";
import { GameView } from "@/components/GameView";

// The game id is runtime data (unknown at build time), so it's read inside <Suspense>:
// the page shell renders instantly, then this small server component resolves the id.
async function GameLoader({ params }: { params: PageProps<"/games/[id]">["params"] }) {
  const { id } = await params;
  return <GameView id={id} />;
}

export default function GamePage({ params }: PageProps<"/games/[id]">) {
  return (
    <main className="mx-auto w-full max-w-3xl px-4 pb-12 pt-6">
      <Suspense fallback={<p className="py-16 text-center text-slate-400">Opening game…</p>}>
        <GameLoader params={params} />
      </Suspense>
    </main>
  );
}
