# Room to Spend

Live: https://room-to-spend.vercel.app

Find the pay that buys you the same life in another city. A Fisher index over the 12 COICOP spending divisions:
World Bank ICP 2021 category price levels rolled to 2026, weighted by World Data Lab spending shares at your
standard of living (home and destination baskets), with each city's own rent where we have it.

## City rents
- Official, every city: US (BEA regional price parities by metro, all divisions), UK (ONS private rents).
- Official or published spread between covered cities: Canada, France, Germany, Australia, Spain, Italy, Portugal,
  Netherlands, Switzerland, Sweden, Japan, South Korea, Brazil, Mexico, China (`data/official_rents.csv`,
  `data/rents_*.csv`, each row with unit, period, source and notes). Cities a source leaves out take the cheapest
  covered city.
- Other high-income countries: estimated from spend a head and population (`fit_city_model2.py`), scored against
  every official table by `check_estimate.py`.
- Everywhere else: one urban premium per country. City-states take national prices.

## Build
1. `build_data.py` joins the WDL city category and city 25-demog parquets (local only, not in this repo).
2. `build_site_data.py` writes `room-to-spend/data.js` (shares, price levels, rent multipliers only; no spend levels).
   Importing it rebuilds `data.js`.
3. Before deploying, extract the inline script from `room-to-spend/index.html` and run `node --check` on it.
4. Deploy: `cd room-to-spend && NODE_TLS_REJECT_UNAUTHORIZED=0 vercel --prod --yes --scope anthony-s-projects-wdl`

WDL model inputs under `data/` are internal and gitignored.
