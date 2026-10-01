import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { BACK, C, EASE, clamp, city, country, display, fiveLike, flag, money, sans } from "../lib";
import { Ground } from "./Ground";

// the page's five suggestions for London, arriving as objects: back-out, a small tilt, 3 frames apart
const FIVE = fiveLike(city("New York City", "USA"), 100000, city("London", "GBR"));

export const Cards: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Ground>
      <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", height: "100%" }}>
        <div
          style={{
            fontFamily: display, fontSize: 68, lineHeight: 1.12, letterSpacing: "-0.02em", color: C.ink, marginBottom: 54, maxWidth: 880,
            opacity: interpolate(f, [0, 14], [0, 1], clamp),
            translate: interpolate(f, [0, 20], ["0px 24px", "0px 0px"], { ...clamp, easing: EASE }),
          }}
        >
          Five cities that cost about the same as London
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 24 }}>
          {FIVE.map((o, i) => {
            const a = 18 + i * 4;
            const tilt = i % 2 ? 3 : -3;
            return (
              <div
                key={o.c.n}
                style={{
                  background: C.paper, border: `2px solid ${C.hair}`, borderRadius: 26, padding: "28px 28px",
                  boxShadow: "0 2px 4px rgba(11,17,56,.04), 0 18px 40px -26px rgba(11,17,56,.35)",
                  display: "grid", gridTemplateColumns: "auto 1fr", gridTemplateRows: "auto auto", columnGap: 24, rowGap: 18,
                  gridColumn: i === 4 ? "1 / span 2" : undefined,
                  opacity: interpolate(f, [a, a + 8], [0, 1], clamp),
                  translate: interpolate(f, [a, a + 16], ["0px 46px", "0px 0px"], { ...clamp, easing: BACK }),
                  rotate: interpolate(f, [a, a + 16], [`${tilt}deg`, "0deg"], { ...clamp, easing: BACK }),
                  scale: interpolate(f, [a, a + 16], [0.94, 1], { ...clamp, easing: BACK }),
                }}
              >
                <Img src={staticFile(flag(o.c.c))} style={{ width: 70, borderRadius: 7, boxShadow: "0 0 0 1px rgba(11,17,56,.08)", alignSelf: "center" }} />
                <div>
                  <div style={{ fontFamily: display, fontSize: 44, color: C.ink, lineHeight: 1.15 }}>{o.c.n}</div>
                  <div style={{ fontFamily: sans, fontSize: 30, color: C.mut }}>{country(o.c.c).k}</div>
                </div>
                <div style={{ gridColumn: "1 / span 2", borderTop: `2px solid ${C.hair}`, paddingTop: 16, display: "flex", alignItems: "baseline", gap: 14, flexWrap: "wrap" }}>
                  <span style={{ fontFamily: sans, fontWeight: 500, fontSize: 40, color: C.ink, fontVariantNumeric: "tabular-nums" }}>{money(o.local, o.cur)}</span>
                  {o.cur !== "USD" && <span style={{ fontFamily: sans, fontSize: 27, color: C.mut, fontVariantNumeric: "tabular-nums" }}>{money(o.usd, "USD")}</span>}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Ground>
  );
};
