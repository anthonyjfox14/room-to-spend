# cityprice_jpn.csv: Japan regional price levels by prefecture, 2025

**Source:** Statistics Bureau of Japan (総務省統計局), Retail Price Survey (Structural Survey) 小売物価統計調査（構造編）, table group 地域別価格差 (regional price differences). Statistics code 00200571.

**Table:** 10大費目別消費者物価地域差指数（全国平均＝100）－ 全国，地方，都道府県，都道府県庁所在市及び政令指定都市
(Regional difference index of consumer prices by the 10 major expenditure groups, national average = 100: Japan, regions, prefectures, prefectural capitals and designated cities.)

**Year:** 2025 (survey year). Published on e-Stat 2026-09-18 14:00. This is the latest year available as of 2026-10-08.

**URLs:**
- Dataset page: https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00200571&stat_infid=000040506879
- Excel file (saved as `data/rents_raw/jpn_rdi/rdi_2025_10groups_pref.xlsx`; server filename b001.xlsx): https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040506879&fileKind=0
- Survey home: https://www.stat.go.jp/data/kouri/index.htm

**Rows:** the 47 prefecture rows (region codes 01000 to 47000). The regional (地方) rows and the city rows in the same sheet are dropped.

**Column mapping:**

| column | source header |
|---|---|
| all | 総合 |
| food | 食料 |
| housing | 住居 |
| utilities | 光熱・水道 |
| furniture | 家具・家事用品 |
| clothing | 被服及び履物 |
| health | 保健医療 |
| transport_comm | 交通・通信 |
| education | 教育 |
| recreation | 教養娯楽 |
| misc | 諸雑費 |
| all_ex_rent | 家賃を除く総合 |

Values are copied unchanged (one decimal place) and none are imputed. The table has no missing (…) cells for prefectures.

**Caveats:**
- `housing` (住居) and `all` (総合) include actual rents paid by renters but **exclude owner-occupiers' imputed rent**. Since 2018 the Bureau has used the names 総合 and 住居 for what used to be called 持家の帰属家賃を除く総合 and 持家の帰属家賃を除く住居. `all_ex_rent` (家賃を除く総合) excludes rent altogether.
- The indices are relative within Japan only (national average = 100, 2025). They are not comparable across years as a time series, and they are not international price levels.
- A prefecture's index covers the whole prefecture, so it understates the price level of the main city in some prefectures. For city-level detail, the same sheet has prefectural-capital and designated-city rows. Example: Tokyo-to `housing` is 129.8 and covers all of Tokyo-to, not only the 23 wards.
- `education` swings widely (Osaka 124.7, Kyoto 118.6) because it is driven by tuition-fee policy. Hokkaido's `utilities` (117.8) reflects heating fuel.

**City map:** `cityprice_jpn_citymap.csv` assigns each WDL city to the prefecture that contains it. Nagoya and Toyohashi are in Aichi, Sapporo in Hokkaido, Sendai in Miyagi, Kitakyushu in Fukuoka, Naha in Okinawa, Otsu in Shiga, Kanazawa in Ishikawa, Himeji in Hyogo, Takasaki in Gunma, Matsuyama in Ehime, Numazu in Shizuoka, Kofu in Yamanashi, Fukuyama in Hiroshima, Utsunomiya in Tochigi and Takamatsu in Kagawa. Every other city is in the prefecture of the same name.
