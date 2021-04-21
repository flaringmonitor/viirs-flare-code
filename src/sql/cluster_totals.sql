SELECT
    {our_timestamp} AS run,
    state, flare_month_d AS month, company_key AS ticker,
    SUM(sum_rh) AS sum_rh
FROM
    {merged}
GROUP BY
    state, flare_month_d, company_key
ORDER BY
    state, flare_month_d, company_key
