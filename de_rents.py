"""German city rents: Zensus 2022 1km grid of average net cold rent a m2 (destatis), averaged over each WDL city
polygon weighted by the number of dwellings in each cell. Writes data/de_rent_cities.csv."""
import geopandas as gpd, pandas as pd
import build_site_data as B
g = pd.read_csv('data/de_rent_1km.csv', sep=';', decimal=',')
g = g[pd.to_numeric(g.durchschnMieteQM, errors='coerce').notna()]
g['rent'] = pd.to_numeric(g.durchschnMieteQM); g['n'] = pd.to_numeric(g.AnzahlWohnungen, errors='coerce').fillna(0)
pts = gpd.GeoDataFrame(g[['rent','n']], geometry=gpd.points_from_xy(g.x_mp_1km, g.y_mp_1km), crs=3035)
polys = gpd.read_file('data/cities.gpkg', where="ccode='DEU'")
pts = pts.to_crs(polys.crs)
j = gpd.sjoin(pts, polys[['city_id','geometry']], predicate='within')
j['rw'] = j.rent * j.n
out = j.groupby('city_id').agg(rw=('rw','sum'), n=('n','sum'), cells=('rent','size')).reset_index()
out['rent'] = out.rw / out.n
out['city'] = [B.RENAME.get(('DEU', c), B.cname('DEU', c)) for c in out.city_id]
nat = (g.rent * g.n).sum() / g.n.sum()
out[['city','city_id','rent','n','cells']].to_csv('data/de_rent_cities.csv', index=False)
print('national', round(nat, 2)); print(out.sort_values('n', ascending=False)[['city','rent','n','cells']].head(25).round(2).to_string())
