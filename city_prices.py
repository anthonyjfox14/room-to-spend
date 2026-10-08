"""City price multipliers for the same-life page, by COICOP division (1..12), against the country's average.
US: BEA Regional Price Parities by metro area, 2024 (data/bea_rpp_msa.csv, US = 100), split goods / housing /
utilities / other services. Each WDL US city is mapped to one metro by hand (MSA_OF), asserted unique.
Division mapping: goods 1 2 3 5; housing 4 = 0.8 housing + 0.2 utilities; services 6 8 10 11 12; half and half 7 9.
"""
import pandas as pd
MSA_OF = {
 'New York City':'New York-Newark', 'Los Angeles':'Los Angeles-Long Beach', 'Miami':'Miami-Fort Lauderdale',
 'Chicago':'Chicago-Naperville', 'San Francisco':'San Francisco-Oakland', 'Houston':'Houston-Pasadena',
 'Washington':'Washington-Arlington', 'Phoenix':'Phoenix-Mesa', 'Dallas':'Dallas-Fort Worth', 'Denver':'Denver-Aurora',
 'Las Vegas':'Las Vegas-Henderson', 'Philadelphia':'Philadelphia-Camden', 'Seattle':'Seattle-Tacoma',
 'San Diego':'San Diego-Chula Vista', 'Detroit':'Detroit-Warren', 'Portland, Oregon':'Portland-Vancouver',
 'Mesa':'Phoenix-Mesa', 'Sacramento':'Sacramento-Roseville', 'Boston':'Boston-Cambridge', 'Austin':'Austin-Round Rock',
 'San Antonio':'San Antonio-New Braunfels', 'Orlando':'Orlando-Kissimmee', 'Minneapolis':'Minneapolis-St. Paul',
 'Baltimore':'Baltimore-Columbia', 'Salt Lake City':'Salt Lake City', 'Saint Petersburg':'Tampa-St. Petersburg',
 'Columbus':'Columbus, OH', 'Milwaukee':'Milwaukee-Waukesha', 'New Orleans':'New Orleans-Metairie',
 'St. Louis':'St. Louis, MO-IL', 'Fresno':'Fresno, CA', 'Tampa':'Tampa-St. Petersburg', 'Cleveland':'Cleveland, OH',
 'Arlington':'Dallas-Fort Worth', 'Bakersfield':'Bakersfield', 'El Paso':'El Paso, TX', 'Norfolk':'Virginia Beach',
 'Atlanta':'Atlanta-Sandy Springs', 'Honolulu':'Urban Honolulu', 'Provo':'Provo-Orem',
 'North Richland Hills':'Dallas-Fort Worth', 'Louisville':'Louisville/Jefferson', 'Riverside':'Riverside-San Bernardino',
 'Oklahoma City':'Oklahoma City', 'Pittsburgh':'Pittsburgh, PA', 'Tucson':'Tucson', 'Albuquerque':'Albuquerque',
 'Escondido':'San Diego-Chula Vista', 'Colorado Springs':'Colorado Springs', 'Buffalo':'Buffalo-Cheektowaga',
 'Providence, Rhode Island':'Providence-Warwick', 'Tulsa':'Tulsa', 'Indianapolis':'Indianapolis-Carmel',
 'Cincinnati':'Cincinnati, OH', 'Stockton':'Stockton-Lodi', 'The Woodlands':'Houston-Pasadena', 'Memphis':'Memphis',
 'Kansas City':'Kansas City, MO-KS', 'Jacksonville':'Jacksonville, FL', 'Mission Viejo':'Los Angeles-Long Beach',
 'McAllen':'McAllen-Edinburg', 'Omaha':'Omaha', 'Aurora':'Denver-Aurora', 'Boise':'Boise City',
 'Modesto':'Modesto', 'Tacoma':'Seattle-Tacoma', 'Cape Coral':'Cape Coral-Fort Myers', 'Spokane':'Spokane-Spokane Valley',
}
def us_multipliers():
    b = pd.read_csv('data/bea_rpp_msa.csv', encoding='latin1')
    b = b[b.GeoName.str.contains('Metropolitan', na=False)].copy()
    b['what'] = b.Description.str.strip().map({'RPPs: Goods':'g', 'RPPs: Services: Housing':'h',
                                                'RPPs: Services: Utilities':'u', 'RPPs: Services: Other':'o'})
    t = b.dropna(subset=['what']).pivot_table(index='GeoName', columns='what', values='2024') / 100
    out = {}
    for city, pre in MSA_OF.items():
        hit = [g for g in t.index if g.startswith(pre)]
        assert len(hit) == 1, (city, pre, hit)
        r = t.loc[hit[0]]
        g, o, hs = r.g, r.o, 0.8 * r.h + 0.2 * r.u
        m = [g, g, g, hs, g, o, (g + o) / 2, o, (g + o) / 2, o, o, o]
        out[city] = [round(float(v), 4) for v in m]
    return out
if __name__ == '__main__':
    m = us_multipliers()
    for c in ['New York City','San Francisco','Houston','Cleveland','Miami']: print(c, m[c])


# Other countries with official city or regional price levels by kind of spending, against the national average.
# Each returns {city: 12 multipliers}; slot 4 (housing) carries the utilities level only, because rent comes from the
# rent sources and the build combines them as 0.8 rent + 0.2 utilities. Cities a source does not cover are left out.
def _rows(path, mpath, key):
    import os
    if not (os.path.exists(path) and os.path.exists(mpath)): return None, None
    t = pd.read_csv(path).set_index(key)
    m = pd.read_csv(mpath).dropna(subset=[key])
    return t, m

def jpn_multipliers():
    """Statistics Bureau of Japan, regional difference index of consumer prices by prefecture (data/cityprice_jpn.csv).
    Groups: food (with alcohol and eating out) 1 2 11; utilities to housing; furniture 5; clothing 3; health 6;
    transport and communications 7 8; recreation 9; education 10; miscellaneous 12. Tokyo's rent covers four
    prefectures, its other prices Tokyo-to only (Kanagawa, Saitama and Chiba are within 2.2 points of it without rent)."""
    t, m = _rows('data/cityprice_jpn.csv', 'data/cityprice_jpn_citymap.csv', 'pref_en')
    if t is None: return {}
    out = {}
    for city, pref in zip(m.city, m.pref_en):
        r = t.loc[pref].drop(["pref_ja", "year"], errors="ignore").astype(float) / 100
        v = [r.food, r.food, r.clothing, r.utilities, r.furniture, r.health, r.transport_comm, r.transport_comm,
             r.recreation, r.education, r.food, r.misc]
        out[city] = [round(float(x), 4) for x in v]
    return out

CAN_RAW = 'data/rents_raw/can_icpd/18100003.csv'
def build_cityprice_can(year=2019):
    """Rewrites data/cityprice_can.csv from the StatCan table download (CAN_RAW, local only): one row per city, every
    product group StatCan publishes for that year, snake_case columns."""
    import re
    d = pd.read_csv(CAN_RAW)
    d = d[d.REF_DATE == year]
    d['g'] = [re.sub(r'[^a-z0-9]+', '_', g.lower()).strip('_') for g in d['Products and product groups']]
    w = d.pivot_table(index='GEO', columns='g', values='VALUE', aggfunc='first')
    w.insert(0, 'year', year); w.index.name = 'city_statcan'
    w.to_csv('data/cityprice_can.csv')
    return w

def can_multipliers():
    """Statistics Canada inter-city indexes of price differentials, 2019, the last year published (table 18-10-0003),
    against the combined average of 15 cities, not the national level (data/cityprice_can.csv). The finest published
    group is used for each division: food from stores 1, alcohol and tobacco 2, clothing 3, water, fuel and
    electricity to housing (utilities), household furnishings 5, health care 6, transportation 7, household
    operations 8 (communications sit there in Canada's basket), recreation 9, education and reading 10, food from
    restaurants 11, personal care 12. Shelter is left out: CMHC rents carry housing."""
    t, m = _rows('data/cityprice_can.csv', 'data/cityprice_can_citymap.csv', 'city_statcan')
    if t is None: return {}
    out = {}
    for city, sc in zip(m.city, m.city_statcan):
        r = t.loc[sc].drop('year').astype(float) / 100
        v = [r.food_purchased_from_stores, r.alcoholic_beverages_tobacco_products_and_recreational_cannabis,
             r.clothing_and_footwear, r.water_fuel_and_electricity, r.household_furnishings_and_equipment,
             r.health_care, r.transportation, r.household_operations, r.recreation, r.education_and_reading,
             r.food_purchased_from_restaurants, r.personal_care]
        out[city] = [round(float(x), 4) for x in v]
    return out

# mid-2016 population (millions) of the eight English regions outside London, to average their Table 3 levels:
# the English cities are scaled against that average, not against Table 1's 98.7, which is measured differently
ENG_POP = {'South East': 9.03, 'East': 6.13, 'South West': 5.52, 'West Midlands': 5.80, 'East Midlands': 4.72,
           'North West': 7.22, 'North East': 2.64, 'Yorkshire and the Humber': 5.43}
def _eng_t3():
    t = pd.read_csv('data/cityprice_gbr.csv').set_index('region')
    return sum(t.loc[r].all_items_12region * w for r, w in ENG_POP.items()) / sum(ENG_POP.values())

def gbr_multipliers():
    """ONS relative regional consumer price levels, 2016, the last edition published (data/cityprice_gbr.csv), UK = 100,
    without rent. The breakdown by kind of spending exists only for London, England outside London, Scotland, Wales
    and Northern Ireland, so English cities outside London share that row, scaled by their own region's all-items level. Health and education are not published
    and take the region's all-items level; household services (no rent) stand in for utilities."""
    global ENG_T3
    import os
    if os.path.exists('data/cityprice_gbr.csv'): ENG_T3 = _eng_t3()
    t, m = _rows('data/cityprice_gbr.csv', 'data/cityprice_gbr_citymap.csv', 'region')
    if t is None: return {}
    out = {}
    for city, reg, own in zip(m.city, m.division_region, m.region):
        r = t.loc[reg].drop('year').astype(float) / 100
        # English cities outside London share one breakdown; their own region's all-items level (ONS Table 3) moves
        # every division by the same factor, so Brighton (South East 101.5) and Hull (Yorkshire 97.7) differ
        if reg != own:
            r = r * (t.loc[own].all_items_12region / ENG_T3)
            r['c08_communication'] = 1.0          # ONS sets communication to 100 everywhere
        v = [r.c01_food, r.c02_alcohol_tobacco, r.c03_clothing_footwear, r.c04_household_housing_services_excl_rent,
             r.c05_furnishings_household, r.all_items, r.c07_transport, r.c08_communication, r.c09_recreation_culture,
             r.all_items, r.c11_restaurants_hotels, r.c12_misc]
        out[city] = [round(float(x), 4) for x in v]
    return out
