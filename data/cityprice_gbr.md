# cityprice_gbr.csv: UK relative regional consumer price levels (RRCPLs)

- **Publisher:** Office for National Statistics (ONS)
- **Release:** "Relative regional consumer price levels of goods and services, UK: 2016"
- **Article:** https://www.ons.gov.uk/economy/inflationandpriceindices/articles/relativeregionalconsumerpricelevelsuk/2016
- **Release date:** 1 March 2018
- **Reference year:** 2016. CPI prices cover July 2015 to June 2016; the regional price survey ran in autumn 2016; the expenditure weights are averages of the 2014-2016 Living Costs and Food Survey.
- **Latest edition?** Yes. As of 2026-10-08 the series' `/latest` URL still resolves to the 2016 edition, and the ONS release calendar entry (`/releases/relativeregionalconsumerpricelevelsrrcpls`) shows "next release: to be confirmed". ONS has published no 2023 or later edition.
- **Base:** UK = 100. The values are spatial (not temporal), so they cannot be compared over time or with the 2010 edition.

## Raw files (data/rents_raw/gbr_rpl/)

| file | ONS table | URL |
|---|---|---|
| b1d304aa.xls | Table 1: Regional price level relative to national price level (UK=100), 2016, by COICOP division, 5 regions | https://www.ons.gov.uk/file?uri=/economy/inflationandpriceindices/articles/relativeregionalconsumerpricelevelsuk/2016/b1d304aa.xls |
| d3842817.xls | Table 3: Supplementary results, all-items price level with the English regions broken out (12 ITL1 regions) | https://www.ons.gov.uk/file?uri=/economy/inflationandpriceindices/articles/relativeregionalconsumerpricelevelsuk/2016/d3842817.xls |
| 1ce74606.xls | Table 2: Divisional expenditure weights by region (%), not used in the CSV | https://www.ons.gov.uk/file?uri=/economy/inflationandpriceindices/articles/relativeregionalconsumerpricelevelsuk/2016/1ce74606.xls |

## Housing and rents: excluded

ONS published this edition in one version only, and that version **excludes housing**. Actual rents, owner occupiers' housing costs (OOH) and Council Tax are all out of scope. The division `c04_household_housing_services_excl_rent` is the ONS "Household & housing services" division, excluding rental costs and OOH. Health (COICOP 06) and education (10) are also excluded, so those columns do not exist. Motor vehicles are assumed to have no regional price variation. Communication (08) is set to 100 for every region.

## Columns

- `c01` ... `c12`, `all_items`: from **Table 1**. ONS publishes the division breakdown for five regions only: London, England (excluding London), Scotland, Wales and Northern Ireland. The other English ITL1 regions have no division values and are left blank. For an English city outside London, use the `England (excluding London)` row, which `cityprice_gbr_citymap.csv` gives as `division_region`.
- `all_items_12region`: from **Table 3**, the all-items level for all 12 ITL1 regions. ONS computes it from 144 bilateral relativities instead of 25, so London, Scotland, Wales and NI differ slightly from Table 1 (for example, London is 107.2 here and 107.0 in Table 1). ONS advises focusing on the ranks in Table 3, not the exact values.

The values are copied as published, with no rescaling.
