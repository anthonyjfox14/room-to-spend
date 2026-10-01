// Shared look and maths for the Room to Spend film. Every figure on screen is computed here from the same
// data file and the same Fisher index the live page uses (room-to-spend/index.html), so the film cannot drift
// from the site. Refresh src/rts.json with `node sync-data.mjs` after the site data changes.
import { Easing } from "remotion";
import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";
import { loadFont as loadInterTight } from "@remotion/google-fonts/InterTight";
import RTS from "./rts.json";

export const display = loadMontserrat("normal", { weights: ["400", "500"], subsets: ["latin"] }).fontFamily;
export const sans = loadInterTight("normal", { weights: ["400", "500", "600"], subsets: ["latin"] }).fontFamily;

// the WDL paper system
export const C = {
  paper: "#FFFFFF",
  band: "#F2F3F8",
  ink: "#0B1138",
  ink2: "#454B70",
  mut: "#5C6382",
  body: "#6B7290",
  hair: "#E4E6EF",
  accent: "#4C5BE4",
  accentDeep: "#3243CE",
};

// motion: one house curve for moves, back-out for arrivals (welcome-screen grammar)
export const EASE = Easing.bezier(0.32, 0.72, 0, 1);
export const BACK = Easing.bezier(0.34, 1.56, 0.64, 1);
export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

type Country = { k: string; cur: string; fx: number; r: number; p: number[]; w: (number[] | null)[] };
type Data = { rus: number; countries: Record<string, Country>; cities: [string, string, number, number[]?, number?][] };
const D = RTS as unknown as Data;
const K = D.countries;

export type City = { n: string; c: string; card: boolean; m: number[] | null; src: number };
const cities: City[] = D.cities.map((c) => ({ n: c[0], c: c[1], card: c[2] === 2, m: c[3] ?? null, src: c[4] ?? 0 }));
export const city = (name: string, cc?: string): City => {
  const hit = cities.find((c) => c.n === name && (!cc || c.c === cc));
  if (!hit) throw new Error("city not in data: " + name);
  return hit;
};
export const country = (cc: string) => K[cc];

const PTS = [7, 24, 64, 108, 200].map((v) => v * 365);
function weights(k: Country, x: number): number[] {
  const b: [number, number[]][] = [];
  k.w.forEach((v, i) => { if (v) b.push([PTS[i], v]); });
  const n = b.length;
  if (x <= b[0][0]) return b[0][1];
  if (x >= b[n - 1][0]) return b[n - 1][1];
  for (let i = 0; i < n - 1; i++) {
    if (x <= b[i + 1][0]) {
      const t = (Math.log(x) - Math.log(b[i][0])) / (Math.log(b[i + 1][0]) - Math.log(b[i][0]));
      return b[i][1].map((v, j) => v + (b[i + 1][1][j] - v) * t);
    }
  }
  return b[n - 1][1];
}
function prices(c: City, cross: boolean): number[] {
  const k = K[c.c];
  if (!c.m) return k.p;
  return k.p.map((v, j) => v * (cross && j !== 3 ? 1 : c.m![j]));
}
function costRatio(a: City, b: City, x: number): number {
  const cross = a.c !== b.c, A = K[a.c], B = K[b.c], pa = prices(a, cross), pb = prices(b, cross);
  const wa = weights(A, x), wb = weights(B, x);
  let L = 0, la = 0, P = 0, sb = 0;
  for (let j = 0; j < 12; j++) {
    const rel = pb[j] / pa[j];
    L += wa[j] * rel; la += wa[j]; P += wb[j] / rel; sb += wb[j];
  }
  return Math.sqrt((L / la) * (sb / P));
}

// the pay, in the destination's currency and in US dollars, that buys the life `pay` buys at home
export function needed(home: City, pay: number, dest: City) {
  const hk = K[home.c], dk = K[dest.c];
  const yu = pay / hk.fx, x = yu / (hk.r * D.rus);
  const usd = yu * costRatio(home, dest, x);
  return { local: usd * dk.fx, usd, cur: dk.cur, pct: Math.round(100 * (usd / yu - 1)) };
}

// the page's five suggestions: closest in cost, one per country, never home's or the destination's
export function fiveLike(home: City, pay: number, dest: City) {
  const target = needed(home, pay, dest).usd;
  return cities
    .filter((c) => c.card && c.c !== home.c && c.c !== dest.c)
    .map((c) => ({ c, ...needed(home, pay, c) }))
    .sort((a, b) => Math.abs(Math.log(a.usd / target)) - Math.abs(Math.log(b.usd / target)))
    .slice(0, 5)
    .sort((a, b) => a.usd - b.usd);
}

// countries whose city rents come from official or published figures (src 1, 2, 4 on the page)
export function officialCountries(): string[] {
  const s = new Set<string>();
  cities.forEach((c) => { if (c.src === 1 || c.src === 2 || c.src === 4) s.add(c.c); });
  return [...s];
}

export function money(v: number, cur: string) {
  try {
    return new Intl.NumberFormat("en", { style: "currency", currency: cur, maximumFractionDigits: 0 }).format(Math.round(v));
  } catch {
    return cur + " " + Math.round(v).toLocaleString("en");
  }
}
export const flag = (cc: string) => `flags/${cc}.svg`;
