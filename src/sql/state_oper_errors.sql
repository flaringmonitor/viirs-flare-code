WITH latest AS
(
    SELECT
        MAX(date) AS max_date
    FROM
        {operator_estimates}
)

SELECT
    o.state,
    o.company_name AS full_company_name,
    -- percent difference
    ABS(SUM(o.estimated_flare_volume_mcf) - SUM(o.reported_mcf))/
        ((SUM(o.estimated_flare_volume_mcf) + SUM(o.reported_mcf))/2.0) AS error
FROM
    {operator_estimates} o,
    latest l
WHERE
    o.date >= DATE_TRUNC('month', l.max_date - INTERVAL '20 months') AND
    o.date < DATE_TRUNC('month', l.max_date - INTERVAL '2 months') AND
    -- disregard > 100% error points
    ABS(o.estimated_flare_volume_mcf - o.reported_mcf) < (o.estimated_flare_volume_mcf + o.reported_mcf) / 2
GROUP BY
    1, 2
ORDER BY
    1,2
