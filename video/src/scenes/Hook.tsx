import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { BACK, C, EASE, clamp, display, flag, sans } from "../lib";
import { Ground } from "./Ground";

// one huge number, one quiet line, then the question
export const Hook: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Ground>
      <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", height: "100%", gap: 34 }}>
        <div
          style={{
            fontFamily: sans, fontWeight: 500, fontSize: 210, lineHeight: 1, letterSpacing: "-0.035em", color: C.ink,
            fontVariantNumeric: "tabular-nums",
            opacity: interpolate(f, [0, 14], [0, 1], clamp),
            translate: interpolate(f, [0, 22], ["0px 60px", "0px 0px"], { ...clamp, easing: BACK }),
          }}
        >
          $100,000
        </div>
        <div
          style={{
            display: "flex", alignItems: "center", gap: 20, fontFamily: sans, fontSize: 50, color: C.body,
            opacity: interpolate(f, [12, 28], [0, 1], clamp),
            translate: interpolate(f, [12, 30], ["0px 24px", "0px 0px"], { ...clamp, easing: EASE }),
          }}
        >
          <Img src={staticFile(flag("USA"))} style={{ width: 58, borderRadius: 6, boxShadow: "0 0 0 1px rgba(11,17,56,.08)" }} />
          a year in New York City
        </div>
        <div
          style={{
            marginTop: 70, fontFamily: display, fontWeight: 400, fontSize: 76, lineHeight: 1.12, letterSpacing: "-0.02em", color: C.ink,
            opacity: interpolate(f, [42, 60], [0, 1], clamp),
            translate: interpolate(f, [42, 64], ["0px 34px", "0px 0px"], { ...clamp, easing: EASE }),
          }}
        >
          What does the same life cost in <span style={{ color: C.accent }}>another city</span>?
        </div>
      </div>
    </Ground>
  );
};
