// Copies the live site's data into the film: room-to-spend/data.js -> src/rts.json, and the flags.
import { readFileSync, writeFileSync, cpSync } from "node:fs";
const js = readFileSync("../room-to-spend/data.js", "utf8");
const json = js.slice(js.indexOf("{"), js.lastIndexOf("}") + 1);
JSON.parse(json);
writeFileSync("src/rts.json", json);
cpSync("../room-to-spend/flags", "public/flags", { recursive: true });
console.log("synced", json.length, "bytes");
