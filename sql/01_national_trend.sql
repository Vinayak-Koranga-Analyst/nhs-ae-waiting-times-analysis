-- Q1. National monthly trend: attendances, 4-hour performance and 12-hour trolley waits.
SELECT
    strftime(month, '%Y-%m')                                  AS month,
    sum(att_total)                                            AS attendances,
    round(100 * (1 - sum(over4h_total) / sum(att_total)), 1)  AS pct_4h_all_types,
    round(100 * (1 - sum(over4h_t1) / sum(att_t1)), 1)        AS pct_4h_type1,
    sum(dta_wait_12h_plus)                                    AS trolley_waits_12h,
    round(100.0 * sum(dta_wait_12h_plus) / sum(adm_via_ae_type1), 1) AS trolley_12h_per_100_adm
FROM ae_measures
GROUP BY month
ORDER BY month;
