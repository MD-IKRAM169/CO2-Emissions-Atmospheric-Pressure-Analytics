# Project brief for technical interviews

## Elevator pitch

I created a **standalone Python ETL pipeline** that ingests annual CO₂ emissions and monthly meteorological pressure files, validates schemas and unique keys, normalizes wide monthly observations, and persists the results in **SQLite** with a source-provenance table. It produces a JSON quality audit, runs without external dependencies, and includes automated unit tests and GitHub CI. This is a **portfolio reimplementation** inspired by earlier university coursework.

## Demonstrated competencies

| Skill | Implementation |
|---|---|
| Extract | Ingest local CSV and semicolon-delimited CLIMAT TXT |
| Transform | Filter 50 defined country labels, normalize year/month observations |
| Validate | Check schema, reject duplicate keys, keep missing data explicit |
| Load | Use SQLite with primary keys and a source-provenance table |
| Quality reporting | Count missing CO₂ values, incomplete monthly series and missing years |
| Testing | Isolated temporary-file tests plus CLI smoke test in GitHub Actions |
| Data communication | Physically correct units, explicit attribution, limitation-aware charts |

## Technical discussion topics

- Why preserve missing values rather than replacing them with zero or backward-filling.
- How changing country coverage distorts a summed annual time series.
- Why a stable primary key matters when loading repeated observations.
- Why normalizing \`Jahr;Jan;...;Dez\` into year/month rows improves SQL analysis.
- How to extend the work with data fingerprints, monitoring, schema versioning, incremental loads and cloud orchestration.
- Why single-station pressure cannot be treated as global atmospheric pressure and descriptive correlations do not prove climate causality.

## Scope and honesty

This is not a cloud-hosted production system, real-time monitoring service or independently validated climate model. Tests establish reproducible ETL behavior on synthetic inputs. University documents remain linked for provenance, not copied into this repository.
