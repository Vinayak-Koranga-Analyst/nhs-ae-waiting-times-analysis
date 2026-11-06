-- Q6. Correlation between trust 12-hour trolley wait rate and Type 1 4-hour performance
-- (latest 12 months, same trusts as Q5).
WITH trust AS (
    SELECT
        org_code,
        100 * (1 - sum(over4h_t1) / sum(att_t1))           AS pct_4h_type1,
        100.0 * sum(dta_wait_12h_plus) / sum(adm_via_ae_type1) AS trolley_rate
    FROM ae_measures
    WHERE month >= DATE '2025-10-01'
    GROUP BY org_code
    HAVING count(*) FILTER (att_t1 > 0) = 12 AND sum(adm_via_ae_type1) > 0
)
SELECT
    count(*)                                         AS trusts,
    round(corr(trolley_rate, pct_4h_type1), 2)       AS correlation,
    round(regr_slope(pct_4h_type1, trolley_rate), 2) AS pct_points_per_extra_trolley_wait_per_100
FROM trust;
