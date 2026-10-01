import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { C, EASE, clamp, display, flag, sans } from "../lib";
import { Ground } from "./Ground";

// The page's question, written as a sentence. The destination is typed in, letter by letter, as a visitor would.
const DEST = "London, United Kingdom";
const TYPE_FROM = 46, PER_CHAR = 1.6;

const Slot: React.FC<{ cc?: string; showFlag?: boolean; children: React.ReactNode; caret?: boolean }> = ({ cc, showFlag, children, caret }) => {
  const f = useCurrentFrame();
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 14, borderBottom: `4px solid ${caret ? C.accent : C.ink}`, padding: "0 4px 2px", whiteSpace: "nowrap" }}>
      {cc && <Img src={staticFile(flag(cc))} style={{ width: 52, borderRadius: 5, boxShadow: "0 0 0 1px rgba(11,17,56,.08)", opacity: showFlag ? 1 : 0 }} />}
      <span style={{ fontFamily: sans, fontWeight: 500, color: C.accent }}>{children}</span>
      {caret && <span style={{ width: 4, height: "1.05em", background: C.accent, opacity: Math.floor(f / 8) % 2 ? 0 : 1 }} />}
    </span>
  );
};

export const Sentence: React.FC = () => {
  const f = useCurrentFrame();
  const typed = Math.max(0, Math.min(DEST.length, Math.floor((f - TYPE_FROM) / PER_CHAR)));
  const done = typed === DEST.length;
  const line = (a: number) => ({
    opacity: interpolate(f, [a, a + 14], [0, 1], clamp),
    translate: interpolate(f, [a, a + 20], ["0px 26px", "0px 0px"], { ...clamp, easing: EASE }),
  });
  return (
    <Ground>
      <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", height: "100%", gap: 26, fontFamily: display, fontSize: 66, lineHeight: 1.55, letterSpacing: "-0.01em", color: C.ink }}>
        <div style={line(0)}>I live in <Slot cc="USA" showFlag>New York City</Slot></div>
        <div style={line(10)}>on <Slot>$100,000</Slot> a year.</div>
        <div style={line(26)}>I am thinking of moving to</div>
        <div style={line(32)}>
          <Slot cc="GBR" showFlag={done} caret={!done && f >= TYPE_FROM - 6}>{DEST.slice(0, typed) || " "}</Slot>
        </div>
      </div>
    </Ground>
  );
};
