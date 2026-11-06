-- Q5. Is 4-hour performance linked to trolley waits (flow out of A&E)?
-- Group Type 1 trusts into quartiles by 12-hour trolley wait rate, latest 12 months,
-- and compare their Type 1 4-hour performance.
WITH trust AS (
    SELECT
        org_code,
        sum(att_t1)            AS att_t1,
        sum(over4h_t1)         AS over4h_t1,
        sum(dta_wait_12h_plus) AS trolley_12h,
        sum(adm_via_ae_type1)  AS adm_t1
    FROM ae_measures
    WHERE month >= DATE '2025-10-01'
    GROUP BY org_code
    HAVING count(*) FILTER (att_t1 > 0) = 12 AND sum(adm_via_ae_type1) > 0
),
ranked AS (
    SELECT *,
        100.0 * trolley_12h / adm_t1 AS trolley_rate,
        ntile(4) OVER (ORDER BY 100.0 * trolley_12h / adm_t1) AS quartile
    FROM trust
)
SELECT
    quartile                                                        AS trolley_wait_quartile,
    count(*)                                                        AS trusts,
    round(min(trolley_rate), 1) || ' - ' || round(max(trolley_rate), 1) AS trolley_12h_per_100_adm_range,
    round(100 * (1 - sum(over4h_t1) / sum(att_t1)), 1)              AS pct_4h_type1,
    round(median(100 * (1 - over4h_t1 / att_t1)), 1)                AS median_trust_pct_4h_type1
FROM ranked
GROUP BY quartile
ORDER BY quartile;
