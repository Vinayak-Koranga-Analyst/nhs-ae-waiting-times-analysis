-- Q2. Seasonality: winter (Dec-Feb) vs summer (Jun-Aug).
-- December is counted with the following January and February (e.g. Dec 2024 -> winter 2025).
WITH seasonal AS (
    SELECT
        CASE WHEN month(month) IN (12, 1, 2) THEN 'Winter (Dec-Feb)' ELSE 'Summer (Jun-Aug)' END AS season,
        CASE WHEN month(month) = 12 THEN year(month) + 1 ELSE year(month) END              AS season_year,
        *
    FROM ae_measures
    WHERE month(month) IN (12, 1, 2, 6, 7, 8)
)
SELECT
    season,
    season_year,
    count(DISTINCT month)                                     AS months,
    round(sum(att_total) / count(DISTINCT month), 0)          AS avg_monthly_attendances,
    round(100 * (1 - sum(over4h_total) / sum(att_total)), 1)  AS pct_4h_all_types,
    round(sum(dta_wait_12h_plus) / count(DISTINCT month), 0)  AS avg_monthly_trolley_waits_12h
FROM seasonal
GROUP BY ALL
HAVING count(DISTINCT month) = 3
ORDER BY season_year, season;
