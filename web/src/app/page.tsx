import { Scoreboard } from "@/components/Scoreboard";

// Server Component: the static shell renders on the server; <Scoreboard> is the live client part.
export default function Home() {
  return (
    <main className="mx-auto w-full max-w-6xl px-4 pb-12 pt-6">
      <header className="mb-6 flex items-center gap-2.5">
        <span aria-hidden className="size-6 rounded-full bg-orange-500 shadow-[0_0_18px_rgba(249,115,22,.5),inset_-4px_-4px_0_rgba(0,0,0,.25)]" />
        <h1 className="text-2xl font-extrabold tracking-tight">Courtside</h1>
      </header>
      <Scoreboard />
      <footer className="mt-10 text-center text-xs text-slate-500">
        Personal project. Not affiliated with or endorsed by the NBA.
      </footer>
    </main>
  );
}
