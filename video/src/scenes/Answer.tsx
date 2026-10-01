import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { C, EASE, clamp, city, display, flag, money, needed, sans } from "../lib";
import { Ground } from "./Ground";

const R = needed(city("New York City", "USA"), 100000, city("London", "GBR"));

// the answer counts up to the page's exact figure, then the comparison lands
export const Answer: React.FC = () => {
  const f = useCurrentFrame();
  const v = interpolate(f, [12, 58], [0, R.local], { ...clamp, easing: EASE });
  return (
    <Ground>
      <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", height: "100%", gap: 22 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20, fontFamily: display, fontSize: 52, color: C.ink2, opacity: interpolate(f, [0, 12], [0, 1], clamp) }}>
          <Img src={staticFile(flag("GBR"))} style={{ width: 62, borderRadius: 6, boxShadow: "0 0 0 1px rgba(11,17,56,.08)" }} />
          In London you would need
        </div>
        <div style={{ fontFamily: sans, fontWeight: 500, fontSize: 200, lineHeight: 1, letterSpacing: "-0.035em", color: C.accent, fontVariantNumeric: "tabular-nums" }}>
          {money(v, R.cur)}
        </div>
        <div style={{ fontFamily: sans, fontSize: 52, color: C.ink2, marginTop: -4, opacity: interpolate(f, [12, 26], [0, 1], clamp) }}>a year</div>
        <div
          style={{
            marginTop: 50, fontFamily: sans, fontSize: 50, lineHeight: 1.35, color: C.body, maxWidth: 880,
            opacity: interpolate(f, [62, 78], [0, 1], clamp),
            translate: interpolate(f, [62, 82], ["0px 22px", "0px 0px"], { ...clamp, easing: EASE }),
          }}
        >
          That is <b style={{ color: C.ink, fontWeight: 500 }}>{Math.abs(R.pct)}% {R.pct < 0 ? "less" : "more"}</b> than $100,000 in New York, for the same life.
        </div>
      </div>
    </Ground>
  );
};
