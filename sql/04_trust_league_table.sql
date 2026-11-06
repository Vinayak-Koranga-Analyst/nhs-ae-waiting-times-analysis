-- Q4. Type 1 trusts, latest 12 months: 4-hour performance and 12-hour trolley wait rate.
-- Only trusts reporting Type 1 activity in all 12 months, to keep the comparison fair.
WITH latest AS (
    SELECT *
    FROM ae_measures
    WHERE month >= DATE '2025-10-01'
),
full_year AS (
    SELECT org_code
    FROM latest
    WHERE att_t1 > 0
    GROUP BY org_code
    HAVING count(*) = 12
)
SELECT
    org_code,
    any_value(org_name)                                         AS trust,
    replace(any_value(region), 'NHS ENGLAND ', '')              AS region,
    sum(att_t1)                                                 AS type1_attendances,
    round(100 * (1 - sum(over4h_t1) / sum(att_t1)), 1)          AS pct_4h_type1,
    round(100.0 * sum(dta_wait_12h_plus) / nullif(sum(adm_via_ae_type1), 0), 1) AS trolley_12h_per_100_adm
FROM latest
WHERE org_code IN (SELECT org_code FROM full_year)
GROUP BY org_code
ORDER BY pct_4h_type1;
