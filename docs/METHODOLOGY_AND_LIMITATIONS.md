# Methodology, data quality and scientific boundaries

## Original academic context

The 2024/2025 Methods of Advanced Data Engineering (MADE) project at FAU explored a comparison of CO₂ emissions and mean sea-level pressure. This repository is **new portable ETL code**, inspired by that academic work, not a copy of the graded exercises or a reproduced causal result.

## Inputs and experimental snapshot

The observed historical source snapshots contain **9,171 selected country-year rows** with **7,373 available CO₂ estimates**, from **50 selected country/territorial labels**, and years spanning **1750–2022**. The original project emphasized **1850–2022**.

The pressure file contains 65 observed years in **1951–2021**, with **1971–1976 missing entirely**, and **766 nonmissing monthly values out of 780**. This is DWD CLIMAT weather station **01001 (Jan Mayen)**, where the quantity is **mean sea-level pressure in hPa**. It is not measured ocean surface height.

These descriptive counts are derived from the supplied historical local data, **not** a claim about the latest upstream datasets.

## ETL stages

1. Load the two files using explicit local CLI paths; no automatic downloads or data overwrites.
2. Validate expected field names, typed years and unique country/year or station/year keys.
3. Keep the 50 historical project country labels; omit a \`World\` aggregate to avoid double-counting.
4. Preserve empty CO₂ measurements as null instead of treating missing as zero.
5. Normalize the DWD 12 monthly fields into one \`(year,month,value)\` row per observed year/month.
6. Treat missing or implausible pressure values (outside 850–1100 hPa) as null; do not interpolate data.
7. Write separate SQLite tables for emissions, pressure observations and source-provenance descriptions.
8. Return a JSON audit of coverage, missing station years/months and dataset scope.

## What the results do and do not establish

- The time-series plots are **descriptive** and intentionally presented separately.
- Selected-country CO₂ totals vary in coverage by year, so they are not harmonized comparisons across a constant population or territory set.
- Country-level emissions have a different geographic scale from pressure measured at a single northern weather station.
- **Correlation does not establish causation.** Time trends, changing reporting coverage, missing values, autocorrelation and confounders would all require separate analysis.
- The portfolio code **does not** assert that CO₂ emissions caused measured Jan Mayen pressure changes, or that the DWD file measures rising ocean level.
- The source archive has no established reproducible release manifest or independently validated statistical model.
- Synthetic sample files are deliberately fictional, not genuine CO₂ or meteorological measurements.

## Reproducibility improvements not yet implemented

Pinned source downloads/hashes, station metadata validation, independent reference-data tests, uncertainty estimates, trend harmonization and formal statistical modeling are possible next steps. The existing CI verifies ETL behavior on fabricated fixtures, not scientific hypotheses.
