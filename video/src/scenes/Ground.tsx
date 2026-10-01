import { AbsoluteFill } from "remotion";
import { C } from "../lib";

// the site's ground: white paper with a faint ink dot lattice, fading out towards the bottom
export const Ground: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ backgroundColor: C.paper }}>
    <AbsoluteFill
      style={{
        backgroundImage: "radial-gradient(rgba(11,17,56,0.10) 1.3px, transparent 1.3px)",
        backgroundSize: "26px 26px",
        backgroundPosition: "13px 13px",
        WebkitMaskImage: "linear-gradient(180deg,#000 0%,#000 40%,rgba(0,0,0,.4) 70%,transparent 100%)",
        maskImage: "linear-gradient(180deg,#000 0%,#000 40%,rgba(0,0,0,.4) 70%,transparent 100%)",
      }}
    />
    <AbsoluteFill style={{ padding: "110px 90px" }}>{children}</AbsoluteFill>
  </AbsoluteFill>
);
