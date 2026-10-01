import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { C, EASE, clamp, display, sans } from "../lib";

// the close on the site's grey title band: name, address, logo
export const End: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: C.band, padding: "110px 90px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
      <AbsoluteFill style={{ backgroundImage: "radial-gradient(rgba(11,17,56,.06) 1px, transparent 1px)", backgroundSize: "18px 18px" }} />
      <div style={{ position: "relative", display: "flex", flexDirection: "column", gap: 30 }}>
        <div
          style={{
            fontFamily: display, fontSize: 104, lineHeight: 1.02, letterSpacing: "-0.02em", color: C.ink,
            opacity: interpolate(f, [0, 14], [0, 1], clamp),
            translate: interpolate(f, [0, 22], ["0px 30px", "0px 0px"], { ...clamp, easing: EASE }),
          }}
        >
          Room to <span style={{ color: C.accent }}>Spend</span>
        </div>
        <div style={{ fontFamily: sans, fontSize: 48, color: C.ink2, opacity: interpolate(f, [10, 24], [0, 1], clamp) }}>
          Try your own city at
        </div>
        <div style={{ fontFamily: sans, fontWeight: 500, fontSize: 56, color: C.accentDeep, opacity: interpolate(f, [16, 30], [0, 1], clamp) }}>
          room-to-spend.vercel.app
        </div>
        <Img
          src={staticFile("wdl-logo.png")}
          style={{ width: 380, marginTop: 90, opacity: interpolate(f, [26, 40], [0, 1], clamp) }}
        />
      </div>
    </AbsoluteFill>
  );
};
