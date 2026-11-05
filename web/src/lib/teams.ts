// Team display info: nickname + primary color, keyed by the code the feed sends.
export const TEAMS: Record<string, { name: string; color: string }> = {
  ATL: { name: "Hawks", color: "#C8102E" },        BOS: { name: "Celtics", color: "#007A33" },
  BKN: { name: "Nets", color: "#2a2a2a" },         CHA: { name: "Hornets", color: "#1D1160" },
  CHI: { name: "Bulls", color: "#CE1141" },        CLE: { name: "Cavaliers", color: "#860038" },
  DAL: { name: "Mavericks", color: "#00538C" },    DEN: { name: "Nuggets", color: "#0E2240" },
  DET: { name: "Pistons", color: "#C8102E" },      GS: { name: "Warriors", color: "#1D428A" },
  HOU: { name: "Rockets", color: "#CE1141" },      IND: { name: "Pacers", color: "#002D62" },
  LAC: { name: "Clippers", color: "#C8102E" },     LAL: { name: "Lakers", color: "#552583" },
  MEM: { name: "Grizzlies", color: "#5D76A9" },    MIA: { name: "Heat", color: "#98002E" },
  MIL: { name: "Bucks", color: "#00471B" },        MIN: { name: "Timberwolves", color: "#0C2340" },
  NO: { name: "Pelicans", color: "#0C2340" },      NY: { name: "Knicks", color: "#F58426" },
  OKC: { name: "Thunder", color: "#007AC1" },      ORL: { name: "Magic", color: "#0077C0" },
  PHI: { name: "76ers", color: "#006BB6" },        PHX: { name: "Suns", color: "#1D1160" },
  POR: { name: "Trail Blazers", color: "#E03A3E" },SAC: { name: "Kings", color: "#5A2D81" },
  SA: { name: "Spurs", color: "#2a2a2a" },         TOR: { name: "Raptors", color: "#CE1141" },
  UTAH: { name: "Jazz", color: "#002B5C" },        WSH: { name: "Wizards", color: "#002B5C" },
};

export const team = (code: string) => TEAMS[code] ?? { name: code, color: "#3a4260" };
