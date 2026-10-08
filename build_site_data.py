"""Writes room-to-spend/data.js for the same-life page. Reads only local copies in data/ (see build_data.py).

Same life = the pay that buys the same standard of living in the destination, priced category by category.
 - w: per country and spending band, the share of spending on each of the 12 COICOP divisions (WDL 2026.2.1 city
   category file, all urban cities pooled). Only shares ship, read on the page at fixed points inside the public
   band edges (7, 24, 64, 108 and 200 dollars a day, adjusted to buy the same everywhere).
 - p: per country, the price level of each division against the US (ICP 2021, WDL's icp_category_conversion_factors),
   rolled to 2026 with WDL's 2021-PPP-to-USD factor relative to the US. A missing division takes the country's
   overall price level.
 - r: the country's overall price level against the US (nominal USD per 2021 PPP dollar, over the US's), used to
   place you on the destination's bands at your standard of living.
The page takes a Fisher index of the price relatives: the geometric mean of the home-basket and destination-basket
indices, so neither place's habits decide the answer.
Countries whose exchange rate or price level is unusable (war, collapse, fixed official rates) are left out: EXCLUDE.
"""
import json, re, duckdb, numpy as np, pandas as pd, pycountry
from city_prices import us_multipliers, jpn_multipliers, can_multipliers, gbr_multipliers
CITY_M = {'USA': us_multipliers()}   # city price multipliers by division, against the country's average

EXCLUDE = {'SDN','SSD','HTI','TKM','SYR','YEM','VEN','LBN','IRN','MMR','AFG','PSE','PRK','CUB','ZWE','LBY','ERI'}
FIX_CUR = {'LBR': ('USD', 1.0)}            # the conversion file carries LRD with a rate of 1, which is really US dollars
FLAGSHIP = {'IND': 'New Delhi', 'COM': 'Moroni', 'CYP': 'Nicosia', 'NLD': 'Amsterdam'}   # largest-by-polygon is not the city a reader knows
RENAME = {('CZE','Praga'): 'Prague', ('IND','New Delhi'): 'Delhi', ('MAC','Taipa'): 'Macau'}
DROP = {('ISR','Ramallah, ISR')}
ORDER = {'Vulnerable and Poor':0,'Lower Middle':1,'Core Middle':2,'Upper Middle':3,'Rich':4}

con = duckdb.connect()
cat = con.sql("""SELECT ccode, spending_group, CAST(coicop_1 AS INT) k, SUM(exp_nominal) e
                 FROM 'data/cat_2026.parquet' WHERE urban='urban' AND city_id IS NOT NULL AND coicop_1 BETWEEN 1 AND 12
                 GROUP BY ALL""").df()
hc = con.sql("""SELECT ccode, spending_group, SUM(hc) hc FROM 'data/demogs.parquet'
                WHERE year=2026 AND urb='urban' AND city_id IS NOT NULL GROUP BY ALL""").df()
rr = con.sql("SELECT ccode, SUM(exp_nominal)/SUM(exp_ppp) r FROM 'data/demogs.parquet' WHERE year=2026 GROUP BY 1").df().set_index('ccode').r
RUS = float(rr['USA'])                    # nominal USD per 2021 PPP dollar in the US, to read the band points
rr = rr / rr['USA']

cf = pd.read_csv('data/Conversion_Factors.csv')
cf26 = cf[cf.year==2026].set_index('ccode'); cf21 = cf[cf.year==2021].set_index('ccode')
drift = cf26.hhe_2021ppp_to_current_USD / cf21.hhe_2021ppp_to_current_USD
drift = drift / drift['USA']
icp = pd.read_csv('data/icp_category_conversion_factors.csv').pivot_table(index='ccode', columns='coicop_1', values='pli_us100') / 100
icp = icp.mul(drift, axis=0)

names = pd.read_csv('data/cities_names_english.csv').set_index(['ccode','city_id']).english_city_name.to_dict()
OVER = {'KOR':'South Korea','PRK':'North Korea','RUS':'Russia','IRN':'Iran','VNM':'Vietnam','TWN':'Taiwan','BOL':'Bolivia',
        'VEN':'Venezuela','TZA':'Tanzania','SYR':'Syria','LAO':'Laos','MDA':'Moldova','COD':'DR Congo','COG':'Congo','CZE':'Czechia',
        'TUR':'Turkey','KSV':'Kosovo','GBR':'United Kingdom','USA':'United States','HKG':'Hong Kong','MAC':'Macau',
        'PSE':'Palestine','CIV':"Côte d'Ivoire"}
def country(cc):
    if cc in OVER: return OVER[cc]
    c = pycountry.countries.get(alpha_3=cc); return getattr(c,'common_name',None) or (c.name if c else cc)
def cname(cc, cid):
    n = str(names.get((cc, cid), cid))
    n = n.rsplit(', ',1)[0] if n.endswith(', '+cc) else n
    return re.sub(r'\s*\[.*?\]', '', n).strip()

tot = cat.groupby(['ccode','spending_group']).e.transform('sum')
cat['s'] = cat.e / tot
countries, nfill = {}, 0
for cc, g in cat.groupby('ccode'):
    if cc in EXCLUDE or cc not in rr.index or cc not in cf26.index: continue
    h = hc[hc.ccode==cc].set_index('spending_group').hc
    w = [None]*5
    for sg, x in g.groupby('spending_group'):
        if h.get(sg, 0) < 20000: continue
        v = x.set_index('k').s.reindex(range(1,13)).fillna(0)
        w[ORDER[sg]] = [round(float(t), 4) for t in v]
    if sum(b is not None for b in w) < 2: continue
    p = []
    for k in range(1,13):
        v = icp.at[cc, k] if (cc in icp.index and k in icp.columns) else float('nan')
        if not v == v: v = rr[cc]; nfill += 1          # missing division: the country's overall level
        p.append(round(float(v), 4))
    row = cf26.loc[cc]
    cur, fx = FIX_CUR.get(cc, (row.lcu_code, row.hhe_2021ppp_to_current_LCU/row.hhe_2021ppp_to_current_USD))
    assert cur != 'USD' or abs(fx - 1) < 1e-9, cc
    countries[cc] = dict(k=country(cc), cur=cur, fx=round(fx,6), r=round(float(rr[cc]),5), p=p, w=w)

d = pd.read_parquet('data/city_band.parquet')
pop = d.groupby(['ccode','city_id'], as_index=False)['pop'].first()
pop = pop[pop.ccode.isin(countries) & ~pop.apply(lambda t: (t.ccode, t.city_id) in DROP, axis=1)]
pop['f'] = pop.apply(lambda t: FLAGSHIP.get(t.ccode) == t.city_id, axis=1)
pop = pop[(pop['pop'] >= 3e5) | pop.f].sort_values(['f','pop'], ascending=False)
cities, seen = [], set()
for t in pop.itertuples():
    big = t.ccode not in seen; seen.add(t.ccode)
    n = RENAME.get((t.ccode, t.city_id), cname(t.ccode, t.city_id))
    # a city can stand in the five suggestions only if its country has people in the top bands to read from
    card = big and t.pop >= 3e5 and sum(b is not None for b in countries[t.ccode]['w']) >= 4
    cities.append([n, t.ccode, 2 if card else (1 if big else 0)])
for cc in countries:
    if cc not in seen:
        t = d[d.ccode==cc].sort_values('pop', ascending=False).iloc[0]
        cities.append([RENAME.get((cc, t.city_id), cname(cc, t.city_id)), cc, 1]); seen.add(cc)

# city prices: official where published (US metros: BEA, every division; UK: ONS rents, housing), estimated elsewhere.
# The estimate models only how a country's cities differ from each other in rent, from how rich (spend a head) and how
# big (population) each is, with slopes fitted on US metros and UK cities with each country's mean removed
# (fit_city_model2.py; on the UK, unseen in the US-only fit, error 0.16 against 0.29 for no city difference).
# The level is anchored so the population-weighted mean of a country's listed cities sits at the urban premium U,
# the geometric mean of the US (1.26) and UK (1.08) values. Housing division = 0.8 rent + 0.2 utilities.
SLOPES = json.load(open('data/city_model_coef.json'))['slopes']
U = (1.264 * 1.075) ** 0.5
# high-income countries, where WDL spend a head ranks cities the way rents do (tested on the UK, Canada, France, Germany).
# Elsewhere it does not (public review: Hyderabad above Mumbai, Suzhou above Shenzhen, Ibadan above Abuja).
# NLD, BEL and ITA came out with the main city below a second city (Rotterdam > Amsterdam), so they share U.
ESTIMATE_OK = {'CHE','ISR','AUS','SWE','AUT','CZE','ESP','PRT','GRC','JPN','KOR','POL','NZL','IRL','DNK',
               'NOR','FIN','HUN','SVK','SVN','EST','LVA','LTU','HRV'}
uk_ratio = pd.read_csv('data/uk_rent_ratio.csv').set_index('city').ratio.to_dict()
# official city rents elsewhere (data/official_rents.csv): Canada CMHC 2025 two-bedroom average rent by metro (StatCan
# table 34-10-0133); France Carte des loyers 2025, apartment rent a m2, listing-weighted over the core city's EPCI;
# Germany Zensus 2022 1km grid rent a m2 averaged over each city polygon (de_rents.py); Australia 2021 Census median
# weekly rent by Greater Capital City (ABS QuickStats; Point Cook takes Greater Melbourne)
_o = pd.read_csv('data/official_rents.csv')[['ccode','city','rent']]
# plus the per-region files the source hunt writes (data/rents_*.csv: ccode, city, rent, unit, period, source_name, ...)
import glob
for f in sorted(glob.glob('data/rents_*.csv')):
    r = pd.read_csv(f)
    r = r[pd.to_numeric(r.rent, errors='coerce') > 0][['ccode','city','rent']]
    _o = pd.concat([_o[~_o.ccode.isin(set(r.ccode))], r])
# sources whose city order fails a plain sanity read, kept in the files but not used (2026-10-01):
# UKR mixes Kyiv city with oblast averages (Lviv above Kyiv); ECU puts Cuenca above Quito; ARG's report leaves out
# Buenos Aires, which would then take the cheapest covered level; PAK small division samples put Peshawar above Lahore
OFFICIAL_DROP = {'UKR', 'ECU', 'ARG', 'PAK'}
# Turkey: uncovered provinces take the median of Betam's published non-metro provinces (median of the nine Betam publishes, Ordu and Tekirdag, about 225 a m2), not the
# cheapest province (too low for Antalya or Bursa) and not the national average (Istanbul-heavy, too high for the east)
FILL_RENT = {'TUR': 225.0}
_o = _o[~_o.ccode.isin(OFFICIAL_DROP)]
OFFICIAL = {cc: g.drop_duplicates('city').set_index('city').rent.astype(float).to_dict() for cc, g in _o.groupby('ccode')}
cstat = con.sql("""SELECT ccode, city_id, SUM(exp_nominal)/SUM(hc) spc, SUM(hc) pop FROM 'data/demogs.parquet'
                   WHERE year=2026 AND urb='urban' AND city_id IS NOT NULL GROUP BY ALL""").df()
cstat['n'] = [RENAME.get((c, i), cname(c, i)) for c, i in zip(cstat.ccode, cstat.city_id)]
cstat = cstat.drop_duplicates(['ccode','n']).set_index(['ccode','n'])
import math
from collections import defaultdict
byc = defaultdict(list)
for row in cities: byc[row[1]].append(row)
for cc, rows in byc.items():
    if cc == 'USA':
        for row in rows: row += [CITY_M['USA'][row[0]], 1]
        continue
    if cc == 'GBR':
        for row in rows:
            r = uk_ratio[row[0]]; row += [[1,1,1,round(0.8*r+0.2,4),1,1,1,1,1,1,1,1], 2]
        continue
    if cc in {'SGP','HKG','MAC'}:
        # city-states: the city is the country, so national prices with no urban premium
        for row in rows: row += [[1]*12, 5]
        continue
    if len(rows) == 1:
        rows[0] += [[1,1,1,round(0.8*U+0.2,4),1,1,1,1,1,1,1,1], 5]; continue
    st = [cstat.loc[(cc, row[0])] for row in rows]
    off = OFFICIAL.get(cc, {})
    hit = [i for i, row in enumerate(rows) if row[0] in off]
    if len(hit) >= 2:
        # official rents: their spread across the covered cities, anchored at U like the estimate.
        w = [st[i]['pop'] for i in hit]; W = sum(w)
        lr = [math.log(off[rows[i][0]]) for i in hit]; lbar = sum(a*b for a, b in zip(lr, w)) / W
        hs = []
        for i, li in zip(hit, lr):
            h = min(2.5, max(0.4, U * math.exp(li - lbar))); hs.append(h); rows[i] += [[1,1,1,round(0.8*h+0.2,4),1,1,1,1,1,1,1,1], 4]
        # cities the source does not cover take the cheapest covered city: sources cover the biggest, dearest cities,
        # so U and then the lower quartile still put uncovered cities above covered ones (Hegang above Harbin)
        hm = min(hs)
        if cc in FILL_RENT:   # a source that publishes a national figure: uncovered cities take it, on the same scale
            hm = min(2.5, max(0.4, U * math.exp(math.log(FILL_RENT[cc]) - lbar)))
        for i, row in enumerate(rows):
            if i not in hit: row += [[1,1,1,round(0.8*hm+0.2,4),1,1,1,1,1,1,1,1], 6]
        continue
    if cc not in ESTIMATE_OK:
        # the spread estimate was only tested in high-income countries; elsewhere every city takes the urban premium
        for row in rows: row += [[1,1,1,round(0.8*U+0.2,4),1,1,1,1,1,1,1,1], 5]
        continue
    w = [x['pop'] for x in st]; W = sum(w)
    z = [SLOPES[0]*math.log(x.spc) + SLOPES[1]*math.log(x['pop']) for x in st]
    zbar = sum(a*b for a, b in zip(z, w)) / W
    for row, zi in zip(rows, z):
        h = min(2.5, max(0.4, U * math.exp(zi - zbar)))
        row += [[1,1,1,round(0.8*h+0.2,4),1,1,1,1,1,1,1,1], 3]
# official city prices for the other kinds of spending (city_prices.py): US metros already carry theirs. Elsewhere the
# city's own levels replace the national average for everything but rent, and utilities take a fifth of housing.
# The last field of a city row says whether it has its own prices for everything (1) or only its rent (0).
OTHER = {'JPN': jpn_multipliers(), 'CAN': can_multipliers(), 'GBR': gbr_multipliers()}
for row in cities:
    o = OTHER.get(row[1], {}).get(row[0])
    if o:
        h = (row[3][3] - 0.2) / 0.8
        row[3] = o[:3] + [round(0.8 * h + 0.2 * o[3], 4)] + o[4:]
    row.append(1 if (row[1] == 'USA' or o) else 0)

# how sure (README, "How sure"): standard errors on the log of the answer, added in squares on the page (core.js).
#  country: the national price level, from ICP 2021 carried to 2026. We cannot test this here, so it is set by how
#    well measured a country's prices are likely to be: 0.05 where people spend over $40 a day (2021 PPP), 0.07 over
#    $15, 0.10 below, plus 0.03 where ICP lacks three or more divisions and they take the overall level.
#  rent: each city's rent against its country's, by source: BEA metro rents 0.05, ONS 0.08, other official or
#    published city figures 0.10, our estimate 0.15 (out-of-sample error 0.09 to 0.16 in Canada, France, Germany
#    and the UK), the cheapest covered city 0.20, one figure for the country 0.26 (the spread of official city
#    rents around their country's mean, 328 cities).
#  other: a city's other prices, when it takes the national average: 0.027, the spread of US metros' non-housing
#    price levels in the page's own maths.
spd = con.sql("SELECT ccode, SUM(exp_ppp)/SUM(hc)/365 d FROM 'data/demogs.parquet' WHERE year=2026 GROUP BY 1").df().set_index('ccode').d
cunc = {}
for cc, k in countries.items():
    d = float(spd.get(cc, 0)); e = 0.05 if d > 40 else 0.07 if d > 15 else 0.10
    miss = sum(1 for j in range(1, 13) if not (cc in icp.index and j in icp.columns and icp.at[cc, j] == icp.at[cc, j]))
    cunc[cc] = round(e + (0.03 if miss >= 3 else 0), 3)
unc = dict(country=cunc, rent={'1': 0.05, '2': 0.08, '3': 0.15, '4': 0.10, '5': 0.26, '6': 0.20}, other=0.027)

out = dict(year=2026, rus=round(RUS,5), countries=countries, cities=cities, unc=unc)
open('room-to-spend/data.js','w',encoding='utf-8').write('window.RTS=' + json.dumps(out, ensure_ascii=False, separators=(',',':')) + ';\n')
print(sum(c[5] for c in cities), 'cities with every price their own,', sum(len(c) == 6 for c in cities), 'cities with their own prices,', len(countries), 'countries', len(cities), 'cities', sum(c[2]==2 for c in cities), 'card cities', nfill, 'divisions filled from overall level')
