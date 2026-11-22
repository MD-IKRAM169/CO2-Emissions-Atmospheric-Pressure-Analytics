"""Offline isolated tests for the portfolio ETL. No downloads or secrets."""
import csv
import sqlite3
import tempfile
import unittest
from pathlib import Path

from portfolio.pipeline import (MONTHS, read_co2_csv, read_pressure_csv,
                                run, summarize)


class ClimatePipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.co2 = self.root / 'co2.csv'
        self.co2.write_text('country,year,co2,population,temperature_change_from_co2\n'
                            'Germany,2020,100,80000000,0.4\n'
                            'Germany,2021,,81000000,0.41\n'
                            'France,2020,80,67000000,0.3\n'
                            'World,2020,50000,7000000000,1.5\n',
                            encoding='utf-8')
        self.mslp = self.root / 'mslp.txt'
        with self.mslp.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream, delimiter=';')
            writer.writerow(['Jahr', *MONTHS])
            writer.writerow([2020, 1000, *([1001] * 11)])
            writer.writerow([2022, -999, *([1010] * 11)])

    def test_preserves_missing_co2_and_filters_world_aggregate(self):
        rows = read_co2_csv(self.co2)
        self.assertEqual(len(rows), 3)
        self.assertIsNone(next(r[2] for r in rows if r[1] == 2021))
        self.assertNotIn('World', {r[0] for r in rows})

    def test_pressure_missing_months_and_years(self):
        rows = read_pressure_csv(self.mslp)
        self.assertEqual(len(rows), 24)
        self.assertIsNone(rows[12][2])
        info = summarize(read_co2_csv(self.co2), rows)
        self.assertEqual(info['pressure']['missing_years_in_range'], [2021])
        self.assertEqual(info['pressure']['months_missing_or_out_of_range'], 1)

    def test_database_tables_and_no_overwrite(self):
        db = self.root / 'out' / 'climate.sqlite'
        summary = self.root / 'out' / 'summary.json'
        report = run(self.co2, self.mslp, db, summary)
        self.assertTrue(db.exists())
        self.assertTrue(summary.exists())
        self.assertEqual(report['co2']['project_country_count'], 2)
        with sqlite3.connect(db) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM co2_country_year').fetchone()[0], 3)
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM jan_mayen_monthly_pressure').fetchone()[0], 24)
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM source_provenance').fetchone()[0], 2)
        with self.assertRaises(FileExistsError):
            run(self.co2, self.mslp, db, self.root / 'different.json')

    def test_rejects_bad_headers_and_duplicate_co2_keys(self):
        self.co2.write_text('foo,bar\n1,2\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'country, year, co2'):
            read_co2_csv(self.co2)
        self.co2.write_text('country,year,co2\nGermany,2020,20\nGermany,2020,30\n',
                            encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            read_co2_csv(self.co2)

    def test_rejects_duplicate_pressure_year(self):
        with self.mslp.open('a', encoding='utf-8') as stream:
            stream.write('2020;' + ';'.join(['1000'] * 12) + '\n')
        with self.assertRaisesRegex(ValueError, 'Duplicate pressure year'):
            read_pressure_csv(self.mslp)


if __name__ == '__main__':
    unittest.main()
