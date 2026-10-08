# Room to Spend

Live: https://room-to-spend.vercel.app

Find the pay that buys you the same life in another city. A Fisher index over the 12 COICOP spending divisions:
World Bank ICP 2021 category price levels rolled to 2026, weighted by World Data Lab spending shares at your
standard of living (home and destination baskets), with each city's own rent where we have it and its own other
prices where an official source publishes them.

## City prices
Every city starts from its country's prices. On top of that:

- **Every price, official:** US metros (BEA regional price parities, 2024), Japanese prefectures (Statistics Bureau
  regional difference index), Canadian cities (StatCan inter-city price differentials, 2019, the last year published,
  seven cities, against their 15-city average) and UK regions (ONS relative regional price levels, 2016, the last
  edition: a breakdown for London, the rest of England, Scotland, Wales and Northern Ireland, with English cities
  outside London scaled by their own region's overall level against the population-weighted average of the eight). Loaded in `city_prices.py` from `data/bea_rpp_msa.csv` and
  `data/cityprice_*.csv`; each `cityprice_*.md` gives the source and its caveats. Within one country every city
  difference counts. Across borders the non-rent prices count only when both cities have them, so two cities are
  always compared on the same basis.
- **Rent, official or published:** the US, the UK and 38 more countries (`data/official_rents.csv`,
  `data/rents_*.csv`, each row with unit, period, source and notes). The page footer lists them all; it is generated
  by `build_sources.py`, so this file does not repeat the list. Cities a source leaves out take the cheapest covered
  city (Turkey: the median province the source publishes).
- **Rent, estimated:** other high-income countries, from spend a head and population (`fit_city_model2.py`), scored
  against every official table by `check_estimate.py`.
- **Everywhere else:** one urban rent premium for the whole country. City-states take national prices.
- **Left out:** 17 countries whose exchange rates or prices cannot be compared (`EXCLUDE` in `build_site_data.py`).

## How sure
Under each answer the page gives a range the true figure is likely to fall in four times out of five
(± 1.28 standard errors on the log of the answer, `logError` in `room-to-spend/core.js`). The parts are independent
and add in squares; the values ship in `data.js` as `unc` and are set in `build_site_data.py`:

| Part | Size (log) | Basis |
|---|---|---|
| Each country's price level, across borders only | 0.04 / 0.06 / 0.08 by spend a head (over $40 a day, over $15, below), + 0.15 × how far ICP 2021 was carried to 2026, + 0.03 if ICP lacks 3+ divisions | Judgement: ICP extrapolation error cannot be tested with the data here. The carry term gives Japan (yen) and Nigeria (naira) wide ranges. |
| Rent: BEA / ONS / other official or published | 0.05 / 0.08 / 0.10 | Source quality |
| Rent: our estimate | 0.15 | Out-of-sample error 0.09 to 0.16 (Canada, France, Germany, UK) |
| Rent: cheapest covered city | 0.20 | |
| Rent: one figure for the country | 0.26 | Spread of 328 official city rents around their country mean |
| Other prices at the national average | 0.027 | Spread of US metros' non-housing prices in the page's own maths |
| Official other prices: BEA 2024 / Japan 2025 / Canada 2019 / UK 2016 | 0.021 / 0.02 / 0.027 / 0.027 | BEA: year-to-year movement of metro levels. Canada and UK: as old as they are, no surer than a city with no figures |
| Official other prices dropped across a border | that city's own effect | Keeps a detour through a third city usually inside the direct range: 98.1% of the 999,900 routes between the 101 card cities from $100,000. The rest are mostly the Fisher index not being transitive where baskets differ a lot (worst: Bata to Riyadh via Moscow, 43% off against ±13%) |

Rent errors are scaled by the housing share of spending. From $100,000 in New York that gives ±4% for another US
city, ±10% for London, ±12% for Paris or Toronto, ±15% for Tokyo, ±16% for Delhi and ±29% for Lagos. The big number
itself stays exact. The page says the sizes are partly judgement.

## Build
1. `build_data.py` joins the WDL city category and city 25-demog parquets (local only, not in this repo).
2. `build_site_data.py` writes `room-to-spend/data.js` (shares, price levels, city multipliers and the error sizes; no
   spend levels).
3. `build_sources.py` regenerates the footer's country list and rent source lines from `data.js`.
4. `node check_site.mjs` must pass before every deploy. It parses every inline script (a stray apostrophe once blanked
   the live page), checks every city and country loads, runs a round trip through every card city, and compares
   eleven known answers from New York with `check_expected.json`. If an answer moves on purpose, rerun with
   `--update` and commit the new file with the change.
5. Deploy: `cd room-to-spend && NODE_TLS_REJECT_UNAUTHORIZED=0 vercel --prod --yes --scope anthony-s-projects-wdl`

The page maths live in `room-to-spend/core.js`, shared by the page and the checks. `video/` is the LinkedIn film
(Remotion); its `lib.ts` is a frozen copy of the maths from the version it shows.

WDL model inputs under `data/` are internal and gitignored.
