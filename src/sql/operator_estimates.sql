-- try to build "pretty" company name out of company and ticker
WITH oper AS
(
    SELECT
        -- find the most popular operator name per state/ticker
        DISTINCT ON (state, parent_ticker)
            state,
            COALESCE(parent_ticker, operator_name) AS key,
            CASE
                WHEN COALESCE(parent_ticker, '') = '' THEN
                    INITCAP(operator_name)
                ELSE
                    INITCAP(operator_name) || ' (' || parent_ticker || ')'
            END AS company_name

    FROM
    (
        SELECT
            state, parent_ticker, operator_name, COUNT(1) AS count
        FROM
            tmp_geo
        WHERE
            COALESCE(parent_ticker, '') != '' AND
            COALESCE(operator_name, '') != ''
        GROUP BY
            state, parent_ticker, operator_name
        ORDER BY 4 DESC
    ) a
)

SELECT
    f.state,
    t.month AS date,
    COALESCE(m.full_company_name, o.company_name,
        INITCAP(t.ticker)||' (Private)') AS company_name,
    t.sum_rh * f.avg_coef AS estimated_flare_volume_mcf,
    r.flared AS reported_mcf

FROM
    ({cluster_totals}) t
INNER JOIN
    {operator_factors} f
ON
    f.state = t.state AND
    f.operator = t.ticker
    
-- pull in reported
LEFT JOIN
(
    SELECT
        state, month, operator,
        SUM(flared) AS flared
    FROM
        {reported_flares}
    GROUP BY
        state, month, operator
) r
ON
    t.state = r.state AND
    t.ticker = r.operator AND
    t.month = r.month

-- try our mapping table
LEFT JOIN
    flare_automation.mapping_combined m
ON
    f.operator = m.ticker2

-- that may fail, try our formatted operator list
LEFT JOIN
    oper o
ON
    f.state = o.state AND
    f.operator = o.key

ORDER BY
    1, 2, 3

