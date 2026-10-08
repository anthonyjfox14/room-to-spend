// Checks the built site before every deploy: node check_site.mjs (add --update to accept new known answers).
// 1. every inline script in index.html parses (a bad apostrophe once blanked the live page)
// 2. data.js and core.js load, and every city and country is usable
// 3. the maths holds: a city against itself is 1, a round trip comes back, every range holds its answer
// 4. known answers have not moved by more than 1% since they were last accepted (check_expected.json)
import fs from 'node:fs';
import vm from 'node:vm';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const SITE = 'room-to-spend/';
const fails = [];
const fail = (m) => fails.push(m);

// 1. scripts parse
const html = fs.readFileSync(SITE + 'index.html', 'utf8');
[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].forEach((m, i) => {
  try { new vm.Script(m[1], { filename: `inline-${i}` }); } catch (e) { fail(`inline script ${i} does not parse: ${e.message}`); }
});
for (const m of html.matchAll(/<script src="([^"]+)"/g)) if (!fs.existsSync(SITE + m[1])) fail(`missing script ${m[1]}`);

// 2. data loads
const win = {};
vm.runInNewContext(fs.readFileSync(SITE + 'data.js', 'utf8'), { window: win });
const D = win.RTS, K = D.countries, C = require('./' + SITE + 'core.js');
const cities = D.cities.map((c) => ({ n: c[0], c: c[1], card: c[2] === 2, m: c[3] || null, src: c[4] || 0, full: c[5] === 1 }));
for (const c of cities) {
  if (!K[c.c]) fail(`${c.n}: no country ${c.c}`);
  if (!c.m || c.m.length !== 12 || c.m.some((v) => !(v > 0))) fail(`${c.n}: bad city prices`);
  if (!(c.src in D.unc.rent)) fail(`${c.n}: no rent error for source ${c.src}`);
}
for (const [cc, k] of Object.entries(K)) {
  if (!fs.existsSync(`${SITE}flags/${cc}.svg`)) fail(`no flag for ${cc}`);
  if (!(D.unc.country[cc] > 0)) fail(`no country error for ${cc}`);
  if (k.p.length !== 12 || k.p.some((v) => !(v > 0))) fail(`${cc}: bad price levels`);
}

// 3. the maths
const find = (label) => cities.find((c) => `${c.n}, ${K[c.c].k}` === label) || fail(`no city ${label}`);
const ny = find('New York City, United States');
const xOf = (city, y) => (y / K[city.c].fx) / (K[city.c].r * D.rus);
const need = (a, b, y) => (y / K[a.c].fx) * C.costRatio(K, a, b, xOf(a, y)) * K[b.c].fx;   // in b's currency
const x = xOf(ny, 100000);
for (const c of cities.filter((c) => c.card)) {
  const r = C.costRatio(K, ny, c, x), e = C.logError(D, ny, c, x);
  if (!(r > 0) || !isFinite(r)) fail(`New York to ${c.n}: ratio ${r}`);
  if (!(e >= 0) || !isFinite(e) || e > 0.5) fail(`New York to ${c.n}: error ${e}`);
  const back = need(c, ny, need(ny, c, 100000));
  if (Math.abs(back / 100000 - 1) > 0.01) fail(`round trip via ${c.n} comes back at ${Math.round(back)}`);
}
if (Math.abs(C.costRatio(K, ny, ny, x) - 1) > 1e-12) fail('a city against itself is not 1');

// 4. known answers, in the destination's currency, from $100,000 in New York
const PAIRS = ['London, United Kingdom', 'Manchester, United Kingdom', 'Lisbon, Portugal', 'Tokyo, Japan',
  'Toronto, Canada', 'Paris, France', 'Berlin, Germany', 'Delhi, India', 'Lagos, Nigeria', 'Houston, United States',
  'San Francisco, United States'];
const got = Object.fromEntries(PAIRS.map((l) => [l, Math.round(need(ny, find(l), 100000))]));
const EXP = 'check_expected.json';
if (process.argv.includes('--update') || !fs.existsSync(EXP)) {
  fs.writeFileSync(EXP, JSON.stringify(got, null, 1) + '\n'); console.log('known answers written to', EXP);
} else {
  const exp = JSON.parse(fs.readFileSync(EXP, 'utf8'));
  for (const l of PAIRS) if (!(l in exp) || Math.abs(got[l] / exp[l] - 1) > 0.01) fail(`${l}: ${got[l]}, expected ${exp[l]} (run with --update if this change is meant)`);
}
for (const l of PAIRS) {
  const e = C.logError(D, ny, find(l), x);
  console.log(l.padEnd(30), String(got[l]).padStart(9), K[find(l).c].cur, ` ±${(100 * (Math.exp(1.28 * e) - 1)).toFixed(0)}%`);
}
if (fails.length) { console.error(`\n${fails.length} problem(s):\n` + fails.slice(0, 40).join('\n')); process.exit(1); }
console.log(`\nAll checks pass: ${cities.length} cities, ${Object.keys(K).length} countries.`);
