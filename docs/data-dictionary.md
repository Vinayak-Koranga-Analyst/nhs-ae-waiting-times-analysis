# Data Dictionary

**Dataset:** NHS England, A&E Attendances and Emergency Admissions (monthly, provider level)
**Grain:** one row per organisation per month
**Table:** `ae_monthly` in `data/ae.duckdb`, built by [`src/load_data.py`](../src/load_data.py)
**Coverage:** April 2024 – September 2026 (30 months), 207 organisations, 5,905 rows
**Official definitions:** [A&E Attendances and Emergency Admissions definitions (NHS England)](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2025/11/AE-Attendances-Emergency-Definitions-v5.0-final-August-2020.pdf)

## Key terms

| Term | Meaning |
|---|---|
| **Type 1** | Major emergency department: consultant-led, open 24 hours, with full resuscitation facilities. What most people think of as "A&E". |
| **Type 2** | Consultant-led single-specialty A&E, e.g. eye hospitals or dental A&E. |
| **Other A&E department** | Types 3 and 4: urgent treatment centres, minor injury units and walk-in centres. |
| **Booked appointment** | An attendance booked in advance, e.g. through NHS 111. Counted separately but included in the headline 4-hour figure. |
| **4-hour standard** | The share of attendances where the patient is admitted, transferred or discharged within 4 hours of arrival. Constitutional standard: 95%. Interim target for March 2026: 78%. |
| **DTA (decision to admit)** | The point when a clinician decides the patient needs a hospital bed. |
| **Trolley wait** | Time from DTA to the patient actually being admitted. Long trolley waits mean A&E is full of patients waiting for beds elsewhere in the hospital. |

## Columns

| Column | Source column (as published) | Type | Description |
|---|---|---|---|
| `period` | Period | text | Published period code, e.g. `MSitAE-APRIL-2025` |
| `month` | (derived from `period`) | date | First day of the month, e.g. 2025-04-01 |
| `org_code` | Org Code | text | ODS code of the trust or provider, e.g. `RTD` |
| `org_name` | Org name | text | Organisation name |
| `region` | Parent Org | text | NHS England region (7 regions) |
| `att_type1` | A&E attendances Type 1 | integer | Unplanned attendances at Type 1 departments |
| `att_type2` | A&E attendances Type 2 | integer | Unplanned attendances at Type 2 departments |
| `att_other` | A&E attendances Other A&E Department | integer | Unplanned attendances at Type 3/4 departments |
| `att_booked_type1` | A&E attendances Booked Appointments Type 1 | integer | Booked attendances, Type 1 |
| `att_booked_type2` | A&E attendances Booked Appointments Type 2 | integer | Booked attendances, Type 2 |
| `att_booked_other` | A&E attendances Booked Appointments Other Department | integer | Booked attendances, Type 3/4 |
| `over4h_type1` | Attendances over 4hrs Type 1 | integer | Type 1 attendances over 4 hours |
| `over4h_type2` | Attendances over 4hrs Type 2 | integer | Type 2 attendances over 4 hours |
| `over4h_other` | Attendances over 4hrs Other Department | integer | Type 3/4 attendances over 4 hours |
| `over4h_booked_type1` | Attendances over 4hrs Booked Appointments Type 1 | integer | Booked Type 1 attendances over 4 hours |
| `over4h_booked_type2` | Attendances over 4hrs Booked Appointments Type 2 | integer | Booked Type 2 attendances over 4 hours |
| `over4h_booked_other` | Attendances over 4hrs Booked Appointments Other Department | integer | Booked Type 3/4 attendances over 4 hours |
| `dta_wait_4_12h` | Patients who have waited 4-12 hs from DTA to admission | integer | Trolley waits of 4 to 12 hours |
| `dta_wait_12h_plus` | Patients who have waited 12+ hrs from DTA to admission | integer | Trolley waits of over 12 hours |
| `adm_via_ae_type1` | Emergency admissions via A&E - Type 1 | integer | Emergency admissions through Type 1 A&E |
| `adm_via_ae_type2` | Emergency admissions via A&E - Type 2 | integer | Emergency admissions through Type 2 A&E |
| `adm_via_ae_other` | Emergency admissions via A&E - Other A&E department | integer | Emergency admissions through Type 3/4 A&E |
| `adm_other` | Other emergency admissions | integer | Emergency admissions not through A&E (e.g. direct from GP) |
| `source_file` | (added) | text | Name of the CSV the row came from, for audit |

## Derived measures

These are calculated in the SQL queries rather than stored.

| Measure | Formula | Notes |
|---|---|---|
| Total attendances | all six `att_*` columns | Matches NHS England's headline attendance count |
| 4-hour performance (all types) | 1 − (all six `over4h_*` columns ÷ total attendances) | Headline measure. Reproduces NHS England's published figure (e.g. 75.0% for March 2025) |
| 4-hour performance (Type 1) | 1 − ((`over4h_type1` + `over4h_booked_type1`) ÷ (`att_type1` + `att_booked_type1`)) | Major EDs only. Fairer for comparing acute trusts, because Type 3 activity flatters the all-types figure |
| 12-hour trolley wait rate | `dta_wait_12h_plus` ÷ `adm_via_ae_type1` × 100 | 12-hour trolley waits per 100 emergency admissions through Type 1 A&E |

## Data quality checks

| Check | Result | How it's handled |
|---|---|---|
| Each file's organisation rows add up to its national total row | 30 of 30 files reconcile exactly | Total rows are dropped after the check |
| Total row labelled consistently | No: `TOTAL` in 25 files, `Total` in 5, some with trailing spaces | Matched case-insensitively after trimming spaces |
| Same columns in every file | No: September 2024 has 6 extra empty columns | Only the 22 published columns are kept |
| Duplicate organisation-month rows | None | Loader stops if any are found |
| Revised files | Some months were republished as "revised" | The latest published version of each month is used (see `data/sources.txt`) |
| Organisations change over time | 190–201 organisations a month, due to mergers, new providers and closures | Trust comparisons use only organisations that report Type 1 activity in every month of the comparison period |
| Small providers | Many independent-sector UTCs report only Type 3 activity | Excluded from Type 1 trust comparisons |

## Limitations

- **Monthly totals only.** The data shows how many patients waited over 4 hours, not how long they waited or why.
- **Trolley waits are counted from the decision to admit, not from arrival.** The time from arrival to the decision isn't in this dataset.
- **No case mix.** Trusts with older or sicker patients aren't adjusted for.
- **12-hour waits from arrival** (a different measure, from the Emergency Care Data Set) are published separately and are not used here.
