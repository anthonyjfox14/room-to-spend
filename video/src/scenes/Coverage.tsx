import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { BACK, C, EASE, clamp, display, flag, officialCountries, sans } from "../lib";
import { Ground } from "./Ground";

// every country whose city rents come from official or published figures, one flag a frame
const CCS = officialCountries().sort();

export const Coverage: React.FC = () => {
  const f = useCurrentFrame();
  const n = Math.round(interpolate(f, [8, 8 + CCS.length], [0, CCS.length], clamp));
  return (
    <Ground>
      <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", height: "100%" }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 28, opacity: interpolate(f, [0, 10], [0, 1], clamp) }}>
          <span style={{ fontFamily: sans, fontWeight: 500, fontSize: 200, lineHeight: 1, letterSpacing: "-0.035em", color: C.accent, fontVariantNumeric: "tabular-nums" }}>{n}</span>
          <span style={{ fontFamily: display, fontSize: 64, color: C.ink, lineHeight: 1.1 }}>countries</span>
        </div>
        <div
          style={{
            fontFamily: sans, fontSize: 46, lineHeight: 1.35, color: C.body, marginTop: 18, marginBottom: 54, maxWidth: 880,
            opacity: interpolate(f, [10, 24], [0, 1], clamp),
            translate: interpolate(f, [10, 28], ["0px 20px", "0px 0px"], { ...clamp, easing: EASE }),
          }}
        >
          price each city's own rent from official statistics or published market figures.
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(8, 1fr)", gap: 18 }}>
          {CCS.map((cc, i) => {
            const a = 8 + i;
            return (
              <Img
                key={cc}
                src={staticFile(flag(cc))}
                style={{
                  width: "100%", aspectRatio: "4 / 3", objectFit: "cover", borderRadius: 8, boxShadow: "0 0 0 1px rgba(11,17,56,.08)",
                  opacity: interpolate(f, [a, a + 6], [0, 1], clamp),
                  scale: interpolate(f, [a, a + 12], [0.6, 1], { ...clamp, easing: BACK }),
                }}
              />
            );
          })}
        </div>
      </div>
    </Ground>
  );
};
