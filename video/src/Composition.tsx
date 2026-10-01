import { Composition, Folder } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { Hook } from "./scenes/Hook";
import { Sentence } from "./scenes/Sentence";
import { Answer } from "./scenes/Answer";
import { Montage } from "./scenes/Montage";
import { Cards } from "./scenes/Cards";
import { Coverage } from "./scenes/Coverage";
import { End } from "./scenes/End";

const FPS = 30, W = 1080, H = 1350;
// [name, component, frames]; the cut between scenes is a short fade, the hand-off into the answer a slide up
const SCENES: [string, React.FC, number][] = [
  ["Hook", Hook, 96],
  ["Sentence", Sentence, 132],
  ["Answer", Answer, 120],
  ["Montage", Montage, 168],
  ["Cards", Cards, 120],
  ["Coverage", Coverage, 120],
  ["End", End, 105],
];
const T = 10;
const total = SCENES.reduce((s, x) => s + x[2], 0) - T * (SCENES.length - 1);

export const RoomToSpend: React.FC = () => (
  <TransitionSeries>
    {SCENES.flatMap(([name, C, d], i) => [
      <TransitionSeries.Sequence key={name} durationInFrames={d} name={name}>
        <C />
      </TransitionSeries.Sequence>,
      ...(i < SCENES.length - 1
        ? [
            <TransitionSeries.Transition
              key={name + "-t"}
              presentation={name === "Sentence" ? slide({ direction: "from-bottom" }) : fade()}
              timing={linearTiming({ durationInFrames: T })}
            />,
          ]
        : []),
    ])}
  </TransitionSeries>
);

export const MyComposition = () => (
  <>
    <Composition id="RoomToSpend" component={RoomToSpend} durationInFrames={total} fps={FPS} width={W} height={H} />
    <Folder name="Scenes">
      {SCENES.map(([name, C, d]) => (
        <Composition key={name} id={name} component={C} durationInFrames={d} fps={FPS} width={W} height={H} />
      ))}
    </Folder>
  </>
);
