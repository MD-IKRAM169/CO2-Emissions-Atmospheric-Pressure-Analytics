"""Reproducible CO2 / Jan Mayen monthly-pressure ETL (descriptive, not causal).

Inputs are explicit local source files. Run with python -m portfolio.pipeline.
No user-provided source data is modified, downloaded or silently overwritten.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sqlite3
from collections import Counter
from pathlib import Path

# Historical coursework's 50 selected country/territorial labels.
# This is not a political or statistical definition of Europe or the EU.
PROJECT_COUNTRIES = frozenset('''
Albania|Andorra|Armenia|Austria|Azerbaijan|Belarus|Belgium|Bosnia and Herzegovina|Bulgaria|
Croatia|Cyprus|Denmark|Estonia|Finland|France|Georgia|Germany|Greece|Hungary|Iceland|Ireland|
Italy|Kazakhstan|Kosovo|Latvia|Liechtenstein|Lithuania|Luxembourg|Malta|Moldova|Monaco|
Montenegro|Netherlands|North Macedonia|Norway|Poland|Portugal|Romania|Russia|San Marino|
Serbia|Slovakia|Slovenia|Spain|Sweden|Switzerland|Turkey|Ukraine|United Kingdom|Vatican
'''.replace('\n', '').split('|'))

MONTHS = ('Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun',
          'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez')


def _float_or_none(value: str | None) -> float | None:
    """Convert blank, NA and non-finite numbers to missing (not zero)."""
    if value is None or str(value).strip() in ('', 'NA', 'nan', 'NaN'):
        return None
    try:
        number = float(value)
    except (ValueError, TypeError):
        return None
    return number if math.isfinite(number) else None


def read_co2_csv(path: Path):
    """Validate annual country observations; preserve missing CO2 as NULL."""
    with Path(path).open('r', encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not {'country', 'year', 'co2'}.issubset(reader.fieldnames or []):
            raise ValueError('CO2 file must include country, year, co2 columns')
        rows, seen = [], set()
        for record in reader:
            country = (record.get('country') or '').strip()
            if country not in PROJECT_COUNTRIES:
                continue
            try:
                year = int(record['year'])
            except (ValueError, TypeError):
                raise ValueError(f'Invalid CO2 year for {country}: {record.get("year")!r}') from None
            key = (country, year)
            if key in seen:
                raise ValueError(f'Duplicate country/year record: {key}')
            seen.add(key)
            rows.append((country, year, _float_or_none(record.get('co2')),
                         _float_or_none(record.get('population')),
                         _float_or_none(record.get('temperature_change_from_co2'))))
    if not rows:
        raise ValueError('No project countries found in CO2 dataset')
    return rows


def read_pressure_csv(path: Path):
    """Read monthly sea-level-reduced air pressure (hPa), Jan Mayen station 01001."""
    with Path(path).open('r', encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream, delimiter=';')
        if not {'Jahr', *MONTHS}.issubset(reader.fieldnames or []):
            raise ValueError('Expected DWD columns Jahr;Jan;Feb;...;Dez')
        rows, seen = [], set()
        for record in reader:
            try:
                year = int(record['Jahr'])
            except (ValueError, TypeError):
                raise ValueError(f'Invalid pressure year: {record.get("Jahr")!r}') from None
            if year in seen:
                raise ValueError(f'Duplicate pressure year: {year}')
            seen.add(year)
            for month, column in enumerate(MONTHS, 1):
                value = _float_or_none(record[column])
                # Quality-screen absurd/missing marker values without imputing them.
                if value is not None and not (850 <= value <= 1100):
                    value = None
                rows.append((year, month, value))
    if not rows:
        raise ValueError('Pressure file has no observations')
    return rows


def produce_database(co2_rows, pressure_rows, path: Path):
    """Create new SQLite tables with primary keys; never overwrite existing DB."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(f'Refusing to overwrite existing database: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sqlite3.connect(path) as conn:
            conn.executescript("""
                CREATE TABLE co2_country_year (
                    country TEXT NOT NULL, year INTEGER NOT NULL,
                    co2_mt REAL, population REAL, temperature_change_from_co2_deg_c REAL,
                    PRIMARY KEY (country, year)
                );
                CREATE TABLE jan_mayen_monthly_pressure (
                    year INTEGER NOT NULL, month INTEGER NOT NULL,
                    mslp_hpa REAL, station_id TEXT NOT NULL DEFAULT '01001',
                    PRIMARY KEY (year, month), CHECK (month BETWEEN 1 AND 12)
                );
                CREATE TABLE source_provenance (
                    source_name TEXT PRIMARY KEY, description TEXT
                );
            """)
            conn.executemany('INSERT INTO co2_country_year VALUES (?,?,?,?,?)', co2_rows)
            conn.executemany(
                'INSERT INTO jan_mayen_monthly_pressure (year,month,mslp_hpa) VALUES (?,?,?)',
                pressure_rows,
            )
            conn.executemany('INSERT INTO source_provenance VALUES (?,?)', [
                ('OWID CO2', 'Our World in Data annual country CO2. Selected project countries, not EU aggregate.'),
                ('DWD CLIMAT 01001',
                 'Monthly sea-level-reduced atmospheric pressure in hPa at Jan Mayen, not global mean.'),
            ])
    except Exception:
        path.unlink(missing_ok=True)
        raise


def summarize(co2_rows, pressure_rows):
    station_years = sorted({row[0] for row in pressure_rows})
    co2_years = [row[1] for row in co2_rows]
    observed_country_counts = Counter(row[1] for row in co2_rows if row[2] is not None)
    valid_months = sum(row[2] is not None for row in pressure_rows)
    return {
        'co2': {
            'project_country_count': len({row[0] for row in co2_rows}),
            'records': len(co2_rows),
            'records_with_co2': sum(row[2] is not None for row in co2_rows),
            'year_min': min(co2_years),
            'year_max': max(co2_years),
            'country_coverage_changes_by_year': len(set(observed_country_counts.values())) > 1,
            'caution': 'Selected European / partly transcontinental country labels, not an EU aggregate.',
        },
        'pressure': {
            'station': 'Jan Mayen (DWD CLIMAT 01001)',
            'unit': 'hPa (air pressure, not ocean sea-level height)',
            'year_min': station_years[0],
            'year_max': station_years[-1],
            'years_with_rows': len(station_years),
            'missing_years_in_range': sorted(
                set(range(station_years[0], station_years[-1] + 1)) - set(station_years)
            ),
            'months_with_valid_pressure': valid_months,
            'months_missing_or_out_of_range': len(pressure_rows) - valid_months,
        },
        'warning': 'The datasets have different geographic scopes; no causal relationship is inferred.',
    }


def run(co2_file: Path, pressure_file: Path, database: Path, summary: Path) -> dict:
    if Path(summary).exists():
        raise FileExistsError(f'Refusing to overwrite existing summary: {summary}')
    co2 = read_co2_csv(co2_file)
    pressure = read_pressure_csv(pressure_file)
    report = summarize(co2, pressure)
    produce_database(co2, pressure, database)
    path = Path(summary)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--co2', type=Path, required=True, help='OWID country-year CSV')
    parser.add_argument('--pressure', type=Path, required=True, help='DWD station 01001 CSV/TXT')
    parser.add_argument('--database', type=Path, default=Path('outputs/climate.sqlite'))
    parser.add_argument('--summary', type=Path, default=Path('outputs/summary.json'))
    args = parser.parse_args(argv)
    report = run(args.co2, args.pressure, args.database, args.summary)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f'Wrote database: {args.database}\nWrote summary: {args.summary}')


if __name__ == '__main__':
    main()
