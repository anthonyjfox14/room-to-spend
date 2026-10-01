"""Within-country version: only the spread between a country's cities is modelled; the level is anchored so the
population-weighted mean of the country's listed cities equals an urban premium U, measured where we know it.
Fit the slopes on US metros with the country mean removed; test on the UK, which the fit never sees.
"""
import json, numpy as np, pandas as pd, duckdb
import build_site_data as B
from city_prices import us_multipliers
con = duckdb.connect()
city = con.sql("""SELECT ccode, city_id, SUM(exp_nominal)/SUM(hc) spc, SUM(hc) pop FROM 'data/demogs.parquet'
                  WHERE year=2026 AND urb='urban' AND city_id IS NOT NULL GROUP BY ALL""").df()
city['n'] = [B.RENAME.get((c, i), B.cname(c, i)) for c, i in zip(city.ccode, city.city_id)]
def frame(cc, target):
    x = city[city.ccode == cc].set_index('n').loc[list(target)]
    return pd.DataFrame(dict(ls=np.log(x.spc), lp=np.log(x['pop']), w=x['pop'], y=np.log(list(target.values()))), index=x.index)
us = frame('USA', {n: m[3] for n, m in us_multipliers().items()})
uk = frame('GBR', pd.read_csv('data/uk_rent_ratio.csv').set_index('city').ratio.mul(0.8).add(0.2).to_dict())   # housing division = 0.8 rent + 0.2 utilities
def demean(f, cols):
    w = f.w / f.w.sum(); return f[cols] - (f[cols].mul(w, axis=0)).sum()
Xu, yu = demean(us, ['ls','lp']), demean(us, ['y']).y
b, *_ = np.linalg.lstsq(Xu.values, yu.values, rcond=None)
print('slopes (ls, lp):', b.round(3))
for name, f in [('US (fit)', us), ('UK (test)', uk)]:
    X, y = demean(f, ['ls','lp']), demean(f, ['y']).y
    p = X.values @ b
    print(name, 'corr', round(np.corrcoef(p, y)[0,1], 3), 'mean abs err', round(np.abs(p - y).mean(), 3), 'flat', round(np.abs(y).mean(), 3))
    U = float(np.exp((f.y * f.w).sum() / f.w.sum())); print('   urban premium (pop-weighted mean of listed cities):', round(U, 3))
# refit on both, with each country's mean removed, for the slopes we ship
X = pd.concat([demean(us, ['ls','lp']), demean(uk, ['ls','lp'])]); y = pd.concat([demean(us, ['y']).y, demean(uk, ['y']).y])
b2, *_ = np.linalg.lstsq(X.values, y.values, rcond=None); print('pooled slopes:', b2.round(3))
json.dump(dict(slopes=list(map(float, b2))), open('data/city_model_coef.json', 'w'))
