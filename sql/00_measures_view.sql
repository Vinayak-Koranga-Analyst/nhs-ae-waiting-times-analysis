-- Reusable view with the derived measures defined in docs/data-dictionary.md.
CREATE OR REPLACE VIEW ae_measures AS
SELECT
    month,
    org_code,
    org_name,
    region,
    att_type1 + att_type2 + att_other
        + att_booked_type1 + att_booked_type2 + att_booked_other          AS att_total,
    over4h_type1 + over4h_type2 + over4h_other
        + over4h_booked_type1 + over4h_booked_type2 + over4h_booked_other AS over4h_total,
    att_type1 + att_booked_type1                                          AS att_t1,
    over4h_type1 + over4h_booked_type1                                    AS over4h_t1,
    adm_via_ae_type1,
    dta_wait_4_12h,
    dta_wait_12h_plus
FROM ae_monthly;
