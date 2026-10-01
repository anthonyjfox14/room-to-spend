"""Fit how much more rent and services cost in a city than in its country, from how rich and how big the city is.
Train: 68 US metros, BEA RPP 2024 (housing+utilities, other services) against WDL city spend per head and population.
Test: UK cities, ONS private rents Aug 2026 (city rent / UK rent), never seen in the fit.
"""
import duckdb, json, numpy as np, pandas as pd
from city_prices import us_multipliers
con = duckdb.connect()
city = con.sql("""SELECT ccode, city_id, SUM(exp_nominal)/SUM(hc) spc, SUM(hc) pop FROM 'data/demogs.parquet'
                  WHERE year=2026 AND urb='urban' AND city_id IS NOT NULL GROUP BY ALL""").df()
nat = con.sql("SELECT ccode, SUM(exp_nominal)/SUM(hc) spc_nat, SUM(hc) pop_nat FROM 'data/demogs.parquet' WHERE year=2026 GROUP BY 1").df()
city = city.merge(nat, on='ccode')
city['ls'] = np.log(city.spc / city.spc_nat)          # how much richer than the country
city['lp'] = np.log(city['pop'])                        # how big
D = json.loads(open('room-to-spend/data.js', encoding='utf-8').read()[len('window.RTS='):-2])
name_to_id = {}
names = pd.read_csv('data/cities_names_english.csv')
# the page's display names back to city_id, via the same cleaning the builder uses
import build_site_data as B
for t in city.itertuples():
    name_to_id[(t.ccode, B.RENAME.get((t.ccode, t.city_id), B.cname(t.ccode, t.city_id)))] = t.city_id
us = us_multipliers()
rows = []
for n, m in us.items():
    cid = name_to_id.get(('USA', n))
    r = city[(city.ccode=='USA') & (city.city_id==cid)].iloc[0]
    rows.append(dict(n=n, ls=r.ls, lp=r.lp, h=np.log(m[3]), o=np.log(m[5])))
us = pd.DataFrame(rows)
X = np.c_[np.ones(len(us)), us.ls, us.lp]
coef = {}
for y in ['h','o']:
    b, *_ = np.linalg.lstsq(X, us[y], rcond=None)
    pred = X @ b; r2 = 1 - ((us[y]-pred)**2).sum() / ((us[y]-us[y].mean())**2).sum()
    coef[y] = b; print(y, 'coef', b.round(3), 'R2', round(r2, 3))
# test on the UK: predicted housing multiplier against ONS rent ratio (rent part = 0.8 of division 4)
uk = pd.read_csv('data/uk_rent_ratio.csv')
out = []
for t in uk.itertuples():
    cid = name_to_id.get(('GBR', t.city)); r = city[(city.ccode=='GBR') & (city.city_id==cid)].iloc[0]
    ph = np.exp(coef['h'] @ [1, r.ls, r.lp]); out.append((t.city, round(t.ratio,2), round(ph,2)))
o = pd.DataFrame(out, columns=['city','ons','model'])
print(o.to_string()); print('corr', round(np.corrcoef(np.log(o.ons), np.log(o.model))[0,1],3),
      'mean abs log err', round(np.abs(np.log(o.ons/o.model)).mean(),3), 'vs flat (=1):', round(np.abs(np.log(o.ons)).mean(),3))
json.dump({k: list(map(float, v)) for k, v in coef.items()}, open('data/city_model_coef.json','w'))
