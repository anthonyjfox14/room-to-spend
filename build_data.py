"""Per-city essentials curve for the 'equivalent income' site.
essential share s(c,g) = nominal spend on Food+Housing+Health+Transport (COICOP 1,4,6,7) / all nominal spend,
for city c and spending group g, 2026. Mean nominal spend per person m(c,g) from the city 25-demog file.
"""
import duckdb, json, pandas as pd
YEAR = 2026
ESS = (1, 4, 6, 7)
con = duckdb.connect()
cat = con.sql(f"""
  SELECT ccode, city_id, spending_group,
         SUM(CASE WHEN coicop_1 IN {ESS} THEN exp_nominal ELSE 0 END) AS ess,
         SUM(CASE WHEN coicop_1=1 THEN exp_nominal ELSE 0 END) AS food,
         SUM(CASE WHEN coicop_1=4 THEN exp_nominal ELSE 0 END) AS housing,
         SUM(exp_nominal) AS tot_cat
  FROM 'data/cat_2026.parquet' WHERE urban='urban' AND city_id IS NOT NULL
  GROUP BY ALL""").df()
dem = con.sql(f"""
  SELECT ccode, city_id, spending_group, SUM(hc) hc, SUM(exp_nominal) tot_dem, ANY_VALUE(NAME_1) region
  FROM 'data/demogs.parquet' WHERE year={YEAR} AND urb='urban' AND city_id IS NOT NULL
  GROUP BY ALL""").df()
pop = dem.groupby(['ccode','city_id'], as_index=False).hc.sum().rename(columns={'hc':'pop'})
df = cat.merge(dem, on=['ccode','city_id','spending_group']).merge(pop, on=['ccode','city_id'])
df.to_parquet('data/city_band.parquet')
print(len(cat), len(dem), len(df), pop['pop'].gt(5e5).sum(), 'cities >500k')
# consistency: category totals vs city totals
chk = df.groupby(['ccode','city_id']).agg(a=('tot_cat','sum'), b=('tot_dem','sum'), pop=('pop','first'))
chk['r'] = chk.a/chk.b
print(chk[chk['pop']>1e6].r.describe())
