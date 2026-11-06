-- Q3. Regional performance, latest 12 months (Oct 2025 - Sep 2026) vs the 12 months before.
WITH periods AS (
    SELECT
        region,
        CASE WHEN month >= DATE '2025-10-01' THEN 'latest_12m' ELSE 'prior_12m' END AS period,
        sum(att_total)    AS att,
        sum(over4h_total) AS over4h,
        sum(att_t1)       AS att_t1,
        sum(over4h_t1)    AS over4h_t1,
        sum(dta_wait_12h_plus) AS trolley_12h,
        sum(adm_via_ae_type1)  AS adm_t1
    FROM ae_measures
    WHERE month >= DATE '2024-10-01'
    GROUP BY ALL
)
SELECT
    replace(region, 'NHS ENGLAND ', '')                                                    AS region,
    round(100 * (1 - max(over4h) FILTER (period = 'prior_12m')  / max(att) FILTER (period = 'prior_12m')), 1)  AS pct_4h_prior,
    round(100 * (1 - max(over4h) FILTER (period = 'latest_12m') / max(att) FILTER (period = 'latest_12m')), 1) AS pct_4h_latest,
    round(100 * (1 - max(over4h_t1) FILTER (period = 'latest_12m') / max(att_t1) FILTER (period = 'latest_12m')), 1) AS pct_4h_type1_latest,
    round(100.0 * max(trolley_12h) FILTER (period = 'latest_12m') / max(adm_t1) FILTER (period = 'latest_12m'), 1) AS trolley_12h_per_100_adm_latest
FROM periods
GROUP BY region
ORDER BY pct_4h_latest DESC;
