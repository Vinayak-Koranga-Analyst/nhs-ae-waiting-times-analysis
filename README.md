# NHS A&E Waiting Times: Where Does the Pressure Build Up?

An analysis of NHS England's published A&E data (April 2024 – September 2026), written from a business analyst's point of view: frame the problem, check the data, find where performance breaks down, and recommend what to look at first.

> **Real public data.** All figures come from NHS England's monthly A&E Attendances and Emergency Admissions statistics. The analysis and recommendations are my own and are not NHS guidance.

## The business question

The NHS constitutional standard is for 95% of A&E patients to be admitted, transferred or discharged within 4 hours. The interim target for March 2026 was 78%. Nationally, performance has stayed in the low-to-mid 70s.

This project asks:

1. How has 4-hour performance changed month by month, and how seasonal is it?
2. Which regions and trusts are furthest from the target, and is the gap getting smaller?
3. Is poor 4-hour performance linked to long waits for a bed after the decision to admit ("trolley waits")? In other words, is the bottleneck inside A&E or in flow out of A&E into the hospital?

## Status

| Stage | Status |
|---|---|
| Data sourced, loaded and reconciled | Done |
| [Data dictionary](docs/data-dictionary.md) | Done |
| SQL analysis queries | In progress |
| Python analysis and charts | Next |
| Dashboard | Next |
| Findings and recommendation paper | Next |

## Data

- **Source:** [NHS England, A&E Attendances and Emergency Admissions](https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/), monthly provider-level CSVs. The URLs used are in [`data/sources.txt`](data/sources.txt).
- **Coverage:** 30 months (April 2024 – September 2026), 207 organisations, 5,905 organisation-month rows.
- **Licence:** contains public sector information licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## How to run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/load_data.py
```

The loader reads the 30 CSVs in `data/raw/`, standardises the column names, checks that each file's organisation rows add up to its published national total, and writes a DuckDB database (`data/ae.duckdb`) for the SQL queries.

## Repository layout

```text
data/raw/            Monthly CSVs as published by NHS England
data/sources.txt     Download URLs
docs/                Data dictionary and (later) findings paper
sql/                 Analysis queries (DuckDB SQL)
src/load_data.py     Load, clean and reconcile the data
```

## Tools

SQL (DuckDB), Python (pandas, Plotly), Markdown.
