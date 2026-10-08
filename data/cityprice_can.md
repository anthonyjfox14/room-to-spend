# cityprice_can.csv

Statistics Canada, Table 18-10-0003-01, "Inter-city indexes of price differentials of consumer goods and services, annual".
Index, combined city average = 100. Prices as of October of the reference year. Values copied as published (integers).

- Table page: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000301
- File downloaded (full table): https://www150.statcan.gc.ca/n1/tbl/csv/18100003-eng.zip (fetched 2026-10-08; raw copy in data/rents_raw/can_icpd/)
- Reference year used: **2019**, the latest in the table. The cube ends at 2019 (last released 2020-12-18); StatCan notes the program is under review, so no later year exists.
- 15 cities. Iqaluit has only the food index published, so its other columns are empty. Ottawa-Gatineau covers the Ontario part only.
- Columns are the nine major components (the table's top-level groups). The ninth is published as "Alcoholic beverages, tobacco products and recreational cannabis".

## StatCan's caveat

StatCan says the figures "should not be interpreted as a measure of differences in the cost of living between cities." They compare prices for a selected basket of goods and services only, not everything households buy. Weights come from the 2017 Survey of Household Spending. The timing of price collection and local sales taxes can move city-to-city relationships. Shelter is hard to match across cities, so owned accommodation uses a rental-equivalence approach (market rents standing in for homeowners' shelter costs), which StatCan says should not be used to compare homeowners' purchasing power; housing indexes for Whitehorse and Yellowknife should be used with caution. City coverage grew in 2016-2018, so comparisons with earlier years need care.

## City map

data/cityprice_can_citymap.csv maps the WDL cities to the StatCan city that covers them; uncovered cities are left blank with a note.
