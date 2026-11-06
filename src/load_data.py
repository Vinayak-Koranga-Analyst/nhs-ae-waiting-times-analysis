"""Load NHS England monthly A&E CSVs into a single DuckDB table.

Usage:
    python src/load_data.py

Reads every CSV in data/raw/, keeps the 22 published columns, renames them
to short snake_case names, adds a proper month date, and writes:
    data/processed/ae_monthly.parquet
    data/ae.duckdb  (table: ae_monthly)
"""

from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

COLUMNS = {
    "Period": "period",
    "Org Code": "org_code",
    "Parent Org": "region",
    "Org name": "org_name",
    "A&E attendances Type 1": "att_type1",
    "A&E attendances Type 2": "att_type2",
    "A&E attendances Other A&E Department": "att_other",
    "A&E attendances Booked Appointments Type 1": "att_booked_type1",
    "A&E attendances Booked Appointments Type 2": "att_booked_type2",
    "A&E attendances Booked Appointments Other Department": "att_booked_other",
    "Attendances over 4hrs Type 1": "over4h_type1",
    "Attendances over 4hrs Type 2": "over4h_type2",
    "Attendances over 4hrs Other Department": "over4h_other",
    "Attendances over 4hrs Booked Appointments Type 1": "over4h_booked_type1",
    "Attendances over 4hrs Booked Appointments Type 2": "over4h_booked_type2",
    "Attendances over 4hrs Booked Appointments Other Department": "over4h_booked_other",
    "Patients who have waited 4-12 hs from DTA to admission": "dta_wait_4_12h",
    "Patients who have waited 12+ hrs from DTA to admission": "dta_wait_12h_plus",
    "Emergency admissions via A&E - Type 1": "adm_via_ae_type1",
    "Emergency admissions via A&E - Type 2": "adm_via_ae_type2",
    "Emergency admissions via A&E - Other A&E department": "adm_via_ae_other",
    "Other emergency admissions": "adm_other",
}


def read_month(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    # One file (September 2024) has 6 extra empty columns; keep the 22 published ones.
    df = df[list(COLUMNS)].rename(columns=COLUMNS)
    df["source_file"] = path.name
    return df


def main() -> None:
    frames = [read_month(p) for p in sorted(RAW.glob("*.csv"))]
    df = pd.concat(frames, ignore_index=True)

    df = df.dropna(subset=["org_code"])
    for col in ["period", "org_code", "region", "org_name"]:
        df[col] = df[col].str.strip()

    numeric = [c for c in COLUMNS.values() if c not in ("period", "org_code", "region", "org_name")]
    df[numeric] = df[numeric].apply(pd.to_numeric, errors="coerce").fillna(0).astype("int64")

    # Every file ends with a national TOTAL row (spelt TOTAL or Total). Check the
    # organisation rows add up to it, then drop it.
    is_total = df["org_code"].str.upper().eq("TOTAL")
    totals = df[is_total].set_index("source_file")[numeric]
    orgs_sum = df[~is_total].groupby("source_file")[numeric].sum().loc[totals.index]
    diff = (orgs_sum - totals).abs().sum(axis=1)
    print(f"Reconciled {len(totals)} files against their TOTAL row; "
          f"{(diff > 0).sum()} with differences")
    for f, d in diff[diff > 0].items():
        print(f"  {f}: absolute difference {d:,}")
    df = df[~is_total].copy()

    # "MSitAE-APRIL-2025" -> 2025-04-01
    df["month"] = pd.to_datetime(
        df["period"].str.replace("MSitAE-", "", regex=False), format="%B-%Y"
    )

    dupes = df.duplicated(subset=["month", "org_code"]).sum()
    if dupes:
        raise ValueError(f"{dupes} duplicate month/org rows found")

    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED / "ae_monthly.parquet", index=False)

    con = duckdb.connect(str(ROOT / "data" / "ae.duckdb"))
    con.execute("CREATE OR REPLACE TABLE ae_monthly AS SELECT * FROM df")
    rows, months, orgs = con.execute(
        "SELECT count(*), count(DISTINCT month), count(DISTINCT org_code) FROM ae_monthly"
    ).fetchone()
    con.close()

    print(f"Loaded {rows:,} rows: {months} months, {orgs} organisations")


if __name__ == "__main__":
    main()
