# Reproducibility — run the portfolio pipeline

## Requirements

- Python **3.10 or later** with the standard library (SQLite is included in most builds).
- No external packages to run the pipeline or its tests.
- Optional figures require \`matplotlib\` (\`python -m pip install matplotlib\`).

## Offline smoke test

From the repository root:

~~~bash
python -m unittest discover -s tests -v

python -m portfolio.pipeline \
  --co2 examples/synthetic_co2.csv \
  --pressure examples/synthetic_pressure.csv \
  --database outputs/demo.sqlite \
  --summary outputs/demo_summary.json
~~~

Inputs under \`examples/\` are **fabricated**. Running the same command again intentionally fails if the output paths already exist; change names or explicitly delete generated files yourself.

## Use authorized historical data

Obtain local CSV/TXT sources from [Our World in Data](DATA_SOURCES.md) and DWD. The old course project used these names:

~~~bash
python -m portfolio.pipeline \
  --co2 "path/to/europe_co2_data.csv" \
  --pressure "path/to/global sea level.csv" \
  --database outputs/historical.sqlite \
  --summary outputs/historical_summary.json
~~~

The historic local filename \`global sea level.csv\` is misleading. The station values are atmospheric pressure, not sea-level height.

## Database schema

| Table | Columns |
|---|---|
| \`co2_country_year\` | \`country\`, \`year\`, \`co2_mt\`, \`population\`, \`temperature_change_from_co2_deg_c\` |
| \`jan_mayen_monthly_pressure\` | \`year\`, \`month\`, \`mslp_hpa\`, \`station_id\` |
| \`source_provenance\` | \`source_name\`, \`description\` |

Example queries:

~~~sql
SELECT year, COUNT(co2_mt) AS reporting_countries, SUM(co2_mt) AS sum_mt
FROM co2_country_year GROUP BY year ORDER BY year;

SELECT year, COUNT(mslp_hpa) AS valid_months, AVG(mslp_hpa) AS avg_hpa
FROM jan_mayen_monthly_pressure GROUP BY year ORDER BY year;
~~~

## Optional figures

~~~bash
python -m pip install matplotlib
python -m portfolio.visualize --database outputs/historical.sqlite --out outputs/charts
~~~

Charts compare **two separate time series** and cannot establish a causal relationship.

## Engineering notes

- The program rejects duplicate keys and missing mandatory schema fields.
- Missing CO₂ and station pressure observations remain \`NULL\`.
- Existing database and audit files are not overwritten.
- Tests and GitHub Actions execute entirely on synthetic local fixtures.
- To reproduce the historic snapshot exactly, store source dataset versions, timestamps, hashes and full extraction instructions. The upstream datasets may have changed since the academic project.
