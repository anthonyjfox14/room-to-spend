"""Score the shipped rent-spread estimate against every official city rent table (no refit)."""
import json, glob, numpy as np, pandas as pd, duckdb, sys
sys.stdout.reconfigure(encoding='utf-8')
import build_site_data as B
S = json.load(open('data/city_model_coef.json'))['slopes']
c = duckdb.sql("""SELECT ccode, city_id, SUM(exp_nominal)/SUM(hc) spc, SUM(hc) pop FROM 'data/demogs.parquet'
                  WHERE year=2026 AND urb='urban' AND city_id IS NOT NULL GROUP BY ALL""").df()
c['n'] = [B.RENAME.get((a, i), B.cname(a, i)) for a, i in zip(c.ccode, c.city_id)]
c = c.drop_duplicates(['ccode','n']).set_index(['ccode','n'])
o = pd.concat([pd.read_csv('data/official_rents.csv')[['ccode','city','rent']]] + [pd.read_csv(f)[['ccode','city','rent']] for f in glob.glob('data/rents_*.csv')])
for cc, g in o.groupby('ccode'):
    g = g[[(cc, n) in c.index for n in g.city]].drop_duplicates('city')
    if len(g) < 3: print(cc, 'too few cities', len(g)); continue
    st = c.loc[[(cc, n) for n in g.city]]; w = st['pop'].values / st['pop'].sum()
    z = S[0]*np.log(st.spc.values) + S[1]*np.log(st['pop'].values); z -= (z*w).sum()
    y = np.log(g.rent.values.astype(float)); y -= (y*w).sum()
    print(cc, len(g), 'corr', round(np.corrcoef(z, y)[0,1], 2), 'err', round(np.abs(z-y).mean(), 3), 'flat', round(np.abs(y).mean(), 3))
