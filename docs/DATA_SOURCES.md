# Source inventory and terminology

This repository is a later portfolio reimplementation. It does **not** redistribute raw historical datasets; the source links below are external.

| Source | Data used | Expected file format | Units | Important qualification |
|---|---|---|---|---|
| [Our World in Data CO₂](https://github.com/owid/co2-data) | Annual country-level CO₂ emissions and related fields | Comma-separated CSV | \`co2\`: million tonnes (MtCO₂) | A 50-label country selection; **not** EU membership |
| [DWD CLIMAT atmospheric pressure](https://opendata.dwd.de/climate_environment/CDC/observations_global/CLIMAT/monthly/qc/mean_sea_level_pressure/historical/) | Quality-controlled monthly mean sea-level-reduced air pressure for **station 01001, Jan Mayen** | Semicolon-separated TXT | **hPa** | Single weather station; **not** global mean air pressure or ocean height |

The course project used legacy filenames \`europe_co2_data.csv\` and \`global sea level.csv\`. Despite the latter name, its physical variable is **atmospheric pressure** in hPa. The DWD \`observations_global\` directory collects stations globally; it does **not** make a station file a global spatial average.

The local historical snapshots used to prepare example charts may differ from current source releases. For research replication, record download date, checksum, original license, variable definitions, station identity and preprocessing choices. Check the official sites' current reuse terms before redistributing any raw records.

The representative DWD file in the university project plan was \`01001_195101_202112.txt\`. It is a Jan Mayen pressure series rather than a sea-level-rise record.
