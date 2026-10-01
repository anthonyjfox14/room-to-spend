import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { BACK, C, EASE, clamp, city, display, flag, money, needed, sans } from "../lib";
import { Ground } from "./Ground";

// The same $100,000 New York life, priced in five other cities, cheapest first. One row lands at a time and its
// figure counts up; earlier rows step back so only the newest one is lit.
const HOME = city("New York City", "USA");
const PICKS: [string, string][] = [["Delhi", "IND"], ["Mexico City", "MEX"], ["Lisbon", "PRT"], ["Tokyo", "JPN"], ["Zurich", "CHE"]];
const ROWS = PICKS.map(([n, cc]) => ({ c: city(n, cc), ...needed(HOME, 100000, city(n, cc)) })).sort((a, b) => a.usd - b.usd);
const START = 22, GAP = 24;

export const Montage: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Ground>
      <div style={{ display: "flex", flexDirection: "column", height: "100%", justifyContent: "center" }}>
        <div
          style={{
            fontFamily: display, fontSize: 70, lineHeight: 1.1, letterSpacing: "-0.02em", color: C.ink, marginBottom: 56,
            opacity: interpolate(f, [0, 14], [0, 1], clamp),
            translate: interpolate(f, [0, 20], ["0px 24px", "0px 0px"], { ...clamp, easing: EASE }),
          }}
        >
          The same life, priced <span style={{ color: C.accent }}>city by city</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          {ROWS.map((r, i) => {
            const a = START + i * GAP;
            const lit = f < a + GAP || i === ROWS.length - 1;
            const v = interpolate(f, [a + 4, a + 22], [0, r.local], { ...clamp, easing: EASE });
            return (
              <div
                key={r.c.n}
                style={{
                  display: "grid", gridTemplateColumns: "78px 1fr auto", alignItems: "center", gap: 26, padding: "26px 0",
                  borderTop: `2px solid ${C.hair}`,
                  opacity: interpolate(f, [a, a + 10], [0, 1], clamp) * (lit ? 1 : 0.42),
                  translate: interpolate(f, [a, a + 16], ["0px 40px", "0px 0px"], { ...clamp, easing: BACK }),
                }}
              >
                <Img src={staticFile(flag(r.c.c))} style={{ width: 78, borderRadius: 7, boxShadow: "0 0 0 1px rgba(11,17,56,.08)" }} />
                <div style={{ fontFamily: display, fontSize: 54, color: C.ink }}>{r.c.n}</div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontFamily: sans, fontWeight: 500, fontSize: 54, color: lit ? C.accent : C.ink, fontVariantNumeric: "tabular-nums" }}>{money(v, r.cur)}</div>
                  <div style={{ fontFamily: sans, fontSize: 34, color: C.mut, fontVariantNumeric: "tabular-nums" }}>{r.cur === "USD" ? " " : money(r.usd, "USD")}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Ground>
  );
};
