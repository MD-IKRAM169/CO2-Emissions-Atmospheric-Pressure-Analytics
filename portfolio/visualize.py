"""Optional descriptive plots from generated SQLite (requires matplotlib)."""
import argparse
import sqlite3
from pathlib import Path


def plot(database: Path, out: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as conn:
        co2 = conn.execute("""
            SELECT year, SUM(co2_mt), COUNT(co2_mt)
            FROM co2_country_year WHERE co2_mt IS NOT NULL
            GROUP BY year ORDER BY year
        """).fetchall()
        station = conn.execute("""
            SELECT year, AVG(mslp_hpa), COUNT(mslp_hpa)
            FROM jan_mayen_monthly_pressure GROUP BY year ORDER BY year
        """).fetchall()

    fig, ax = plt.subplots(figsize=(10, 4.8), layout='constrained')
    ax.plot([r[0] for r in co2], [r[1] for r in co2])
    ax.set(title='Selected-country annual CO₂ observations',
           xlabel='Year', ylabel='CO₂ (million tonnes)')
    ax.grid(alpha=.25)
    fig.savefig(out / 'co2_selected_countries.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

    available = {year: value for year, value, count in station if count > 0}
    years = range(min(available), max(available) + 1)
    means = [available.get(year, float('nan')) for year in years]
    fig, ax = plt.subplots(figsize=(10, 4.8), layout='constrained')
    ax.plot(list(years), means)
    ax.set(title='Jan Mayen atmospheric pressure (not global)', xlabel='Year',
           ylabel='Annual mean MSLP (hPa)')
    ax.grid(alpha=.25)
    fig.savefig(out / 'jan_mayen_pressure.png', dpi=150, bbox_inches='tight')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, default=Path('outputs/climate.sqlite'))
    parser.add_argument('--out', type=Path, default=Path('outputs/charts'))
    args = parser.parse_args()
    plot(args.database, args.out)
    print(f'Saved descriptive charts to {args.out}')


if __name__ == '__main__':
    main()
