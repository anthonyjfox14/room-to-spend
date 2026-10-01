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
