WITH well_clusters AS
(
     -- group flares together per well cluster
     SELECT
         state,
         flare_month_d AS month,
         wcluster_geom,
         company_key,
         wcid AS cid,
         -- gather points in cluster
         ST_COLLECT(fcluster_geom) AS fcluster_geom,
         ARRAY_LENGTH(apis_in_cluster, 1) AS wells,
         -- sum flares
         SUM(sum_rh) AS sum_rh
     FROM
         ({cluster_ftw}) c
     GROUP BY
         -- Note: wcluster_geom, company_key, wcid and apis_in_cluster
         -- should always be the same for a well cluster
         state, flare_month_d, wcluster_geom, company_key, wcid,
         apis_in_cluster
),

-- try to build "pretty" company name out of company and ticker
oper AS
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
    i.*,
    COALESCE(m.full_company_name, o.company_name,
        INITCAP(i.ticker_operator)||' (Private)') AS company_name,
    i.sum_rh * f.avg_coef AS estimated_flare_volume_mcf,
    -- Create a bounding circle in kilometers, this will likely overstate
    -- the circle some. Degrees of longitude are smaller in ground length 
    -- than degrees of latitude.
    c.radius * 110.574 AS radius,
    c.center,
    ST_X(c.center) AS longitude,
    ST_Y(c.center) AS latitude
FROM
     (
         -- raw unclustered flares
         SELECT
             'rucf' AS type,
             state,
             DATE_TRUNC('month', date_ltz)::date AS month,
             lpad(EXTRACT(week FROM (date_ltz))::text, 2 ,'0') AS flare_week,
             NULL AS cid,
             point AS cluster_geom,
             rh AS sum_rh,
             NULL::INTEGER AS wells,
             NULL AS ticker_operator

         FROM
             {raw_flare}
         
         UNION ALL
         
         -- weekly flare clusters
         SELECT
             'wfc' AS type,
             state,
             flare_month_d AS month, 
             flare_week,
             cid,
             cluster_geom,
             sum_rh,
             NULL::INTEGER AS wells,
             NULL AS ticker_operator
        FROM
             {weekly}
             
        UNION ALL 
        
        -- monthly well clusters + flare clusters
        SELECT
            'mwc' AS type,
            state,
            month,
            NULL AS flare_week,
            cid,
            ST_COLLECT(wcluster_geom, fcluster_geom) cluster_geom,
            sum_rh,
            wells,
            company_key AS ticker_operator
       FROM
            well_clusters
     ) i
JOIN
     ST_MinimumBoundingRadius(i.cluster_geom) c
ON
     (1=1)

LEFT JOIN
    {operator_factors} f
ON
    f.state = i.state AND
    f.operator = i.ticker_operator

-- try our mapping table
LEFT JOIN
    flare_automation.mapping_combined m
ON
    i.ticker_operator = m.ticker2

-- that may fail, try our formatted operator list
LEFT JOIN
    oper o
ON
    i.state = o.state AND
    i.ticker_operator = o.key

