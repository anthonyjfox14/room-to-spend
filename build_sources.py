"""Writes the footer's country list and the per-country city-rent source lines in room-to-spend/index.html from
the data, so the page cannot claim a country it does not use. Run after build_site_data.py.
Hand-written lines (CURATED) win; any other country gets a line from the first row of its rents_*.csv file."""
import glob, html, json, re, pandas as pd

P = 'room-to-spend/index.html'
D = json.loads(open('room-to-spend/data.js', encoding='utf-8').read()[len('window.RTS='):-2])
K = D['countries']
src4 = sorted({c[1] for c in D['cities'] if c[4] == 4}, key=lambda cc: K[cc]['k'])

def a(url, text): return f'<a href="{html.escape(url, quote=True)}" rel="noopener" target="_blank">{text}</a>'
CURATED = {
 'CAN': 'Canada Mortgage and Housing Corporation via Statistics Canada, ' + a('https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3410013301', 'average rents by metropolitan area, 2025') + '.',
 'FRA': 'Ministry for Ecological Transition, ' + a('https://www.data.gouv.fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2025', 'Carte des loyers 2025') + '.',
 'DEU': 'Federal Statistical Office, ' + a('https://www.destatis.de/zensus2022', 'Census 2022 average rent on a 1 km grid') + ', averaged over each city.',
 'AUS': 'Australian Bureau of Statistics, ' + a('https://www.abs.gov.au/census/find-census-data/quickstats/2021', '2021 Census median weekly rent by capital city') + '.',
 'ESP': 'Ministry of Housing, ' + a('https://www.mivau.gob.es/vivienda/alquila-bien-es-tu-derecho/serpavi', 'SERPAVI rent reference system, 2024') + '.',
 'ITA': 'Revenue Agency, ' + a('https://www.agenziaentrate.gov.it/portale/web/guest/schede/fabbricatiterreni/omi', 'Property Market Observatory (OMI), new leases 2025') + '.',
 'PRT': 'Statistics Portugal, ' + a('https://www.ine.pt', 'house rental statistics, new leases to June 2026') + '.',
 'NLD': 'Statistics Netherlands (CBS), ' + a('https://datasets.cbs.nl/odata/v1/CBS/85950NED', 'housing costs of renters by municipality, 2024') + ', net of housing allowance.',
 'CHE': 'Federal Statistical Office, ' + a('https://www.bfs.admin.ch/bfs/en/home/statistics/construction-housing/dwellings/rented-dwellings.html', 'structural survey rent per m&sup2; by canton, 2024') + '.',
 'SWE': 'Statistics Sweden, ' + a('https://www.scb.se/en/finding-statistics/statistics-by-subject-area/housing-construction-and-building/housing-construction-and-conversion/rents-for-dwellings/', 'rents for dwellings, 2025') + '.',
 'BRA': 'FIPE, ' + a('https://downloads.fipe.org.br/indices/fipezap/fipezap-202608-residencial-locacao.pdf', 'FipeZAP residential rent index, August 2026') + '.',
 'MEX': 'INEGI, ' + a('https://www.inegi.org.mx/programas/enigh/nc/2024/', 'household income and expenditure survey (ENIGH) 2024') + ', rent paid by metro area, our calculation.',
 'JPN': 'Statistics Bureau of Japan, ' + a('https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040210062&fileKind=0', '2023 Housing and Land Survey, private rent per m&sup2; by city') + '; Tokyo uses Tokyo, Kanagawa, Saitama and Chiba, and Osaka and Nagoya their prefectures.',
 'KOR': 'Korea Real Estate Board, ' + a('https://www.reb.or.kr/r-one/portal/bbs/statdata/searchBulletinPage.do', 'housing price trend survey, August 2026') + ': average monthly apartment rent plus the deposit at 5% a year; Seoul uses the capital region.',
 'CHN': 'China Index Academy, ' + a('https://m.cih-index.com/news/2025-04-23/52652700.html', '50-city residential rental price index, March 2025') + '.',
 'IDN': 'Statistics Indonesia (BPS), ' + a('https://www.bps.go.id/id/publication/2024/04/23/10bea00c1fed6819872fa32f/harga-konsumen-beberapa-barang-dan-jasa-kelompok-perumahan-air-listrik-dan-bahan-bakar-rumah-tangga-90-kota-di-indonesia-2023.html', 'consumer prices of housing, 90 cities, 2023') + ', rental house fee; price quotes, not matched for quality between cities.',
 'IND': 'ANAROCK Research, ' + a('https://websitemedia.anarock.com/media/Residential_Market_Viewpoints_Bengaluru_Q1_2025_0dbe000f64.pdf', 'Residential Market Viewpoints city reports, Q1 2025 (Bengaluru shown)') + ', monthly asking rent for a two-bedroom flat averaged over tracked micro-markets; Mumbai and Delhi cover their wider regions, and Mumbai’s satellite towns use their own micro-market figures.',
 'EGY': 'Built Environment Observatory (Marsad Omran), ' + a('https://marsadomran.info/en/2026/07/4430/', 'Cairo') + ' and ' + a('https://marsadomran.info/en/2026/08/4473/', 'Alexandria') + ' rent price indices, 2026 Q2, median asking rent.',
 'BEL': 'CIB Vlaanderen rent barometer ' + a('https://community.cib.be/actua/news/0071c6aa-c6a8-46b1-af1c-060d4cb55a43', 'for Brussels and Antwerp') + ' and the Federia ' + a('https://www.federia.immo/images/blog/2026-02-11-cp-barometre-des-locations-25_file.pdf', 'Wallonia barometer for Liège') + ', apartments on new leases, 2025.',
 'KHM': 'Realestate.com.kh published median asking rents for ' + a('https://www.realestate.com.kh/phnom-penh/', 'Phnom Penh') + ' and ' + a('https://www.realestate.com.kh/siem-reap/', 'Siem Reap') + ', October 2026.',
 'POL': 'Bankier.pl report on Otodom Analytics data, ' + a('https://www.bankier.pl/wiadomosc/Ceny-ofertowe-wynajmu-mieszkan-lipiec-2026-Raport-Bankier-pl-9167757.html', 'asking rents for 40 to 59 m&sup2; flats, June 2026 data (July 2026 report)') + '.',
 'ARE': 'Our average of the rent ranges Asteco quotes for one-bedroom flats in its ' + a('https://cdn.aldar.com/-/media/project/asteco/asteco/pdf/20241001_astrep960_2024q3_uae_v20.pdf', 'UAE property review, Q3 2024') + '.',
 'SAU': 'Real Estate General Authority, Ejar rental indicators on the ' + a('https://open.data.gov.sa', 'Saudi open data platform') + ', 2026 Q1: contract-weighted average apartment rent from four regional district files.',
 'PER': 'INEI, ' + a('https://proyectos.inei.gob.pe/microdatos/', 'ENAHO household survey microdata 2023 and 2024') + ', rent paid by renting households, our calculation.',
 'ISR': 'Central Bureau of Statistics, ' + a('https://www.cbs.gov.il/he/publications/Madad/DocLib/2026/price08a/a4_9_e.xlsx', 'average monthly rent by big city and district, 2026 Q2') + '; Modiin uses the Center District.',
 'RUS': 'Rosstat, ' + a('https://rosstat.gov.ru/storage/mediabank/sred_potreb_cen_08-2026.xlsx', 'average consumer prices in surveyed cities, August 2026') + ', one-room flat rented from a private owner.',
 'BLR': 'Kufar rental data as reported by npr.by, ' + a('https://npr.by/roditeli-vs-obshhezhitie-skolko-stoit-snyat-zhile-dlya-studenta-v-raznyh-gorodah-belarusi/', 'August 2026') + ', median one-room flat.',
 'TUR': 'Betam, Bahçeşehir University, ' + a('https://betam.bahcesehir.edu.tr/wp-content/uploads/2026/09/Kiralik-Konut-Piyasasi-Gorunumu-Eylul-2026.docx', 'rental housing market outlook, August 2026') + ', asking rent per m&sup2; by province.',
}

rows = pd.concat([pd.read_csv(f) for f in sorted(glob.glob('data/rents_*.csv'))])
items = []
for cc in src4:
    if cc in CURATED:
        body = CURATED[cc]
    else:
        r = rows[rows.ccode == cc].iloc[0]
        body = f"{html.escape(str(r.source_name))}, {a(str(r.source_url), html.escape(str(r.period)))}."
    items.append(f'      <li><b>{html.escape(K[cc]["k"])}:</b> {body}</li>')
block = '\n'.join(['      <li><b>City rents, by country</b> (official statistics where published, otherwise published market figures):</li>'] + items)

p = open(P, encoding='utf-8').read()
# replace everything between the UK line and the estimate line with the generated block
i = p.index('<li><b>UK city rents:</b>'); i = p.index('</li>', i) + len('</li>\n')
j = p.index('      <li><b>City rents in other high-income countries:</b>')
assert i < j
p = p[:i] + block + '\n' + p[j:]

names = [K[cc]['k'] for cc in src4]
lst = ', '.join(names[:-1]) + ' and ' + names[-1]
m = re.search(r"In [^.]*?, official or published figures tell us", p)
assert m, 'footer sentence not found'
p = p[:m.start()] + f"In {lst}, official or published figures tell us" + p[m.end():]
open(P, 'w', encoding='utf-8').write(p)
print(len(src4), 'countries listed')
