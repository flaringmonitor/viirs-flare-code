SELECT
    {our_timestamp} AS run,
    'dec' AS type,
    'NM' AS state,
    -- max date from already processed data
    (
        SELECT 
            MAX(disp_dte)
        FROM
            {our_table}
        WHERE
            state = 'NM'
    ) AS disp_dte,
    sq.cid,
    ST_Collect(sq.surface_hole) AS cluster_geom,
    ARRAY_AGG(sq.api ORDER BY sq.api) AS apis_in_cluster,
    company_key
FROM 
(
    SELECT 
        ST_ClusterDBSCAN(wells.surface_hole,.00270,1) OVER (PARTITION BY wells.company_key) AS cid,
        surface_hole,
        wells.api,
        wells.company_key
    FROM
    (
        SELECT
            pt.api,
            pt.surface_hole,
            pt.company_key
        FROM 
        (
            SELECT 
                DISTINCT 
                    w.api,
                    surface_hole,
                    company_key
            FROM
                tmp_geo w
            JOIN
                tmp_prod p
            ON
                w.api = p.api
            WHERE
                w.state = 'NM' AND
                p.state = 'NM' AND 
                p.date >= '2020-06-01'
        ) pt
        JOIN 
        (
            SELECT 
                *
            FROM
                flare_automation.states
            WHERE 
                state_abbr = 'NM'
        ) py 
        ON
            St_intersects(py.geom, pt.surface_hole)
    ) wells
) sq
GROUP BY 
    cid,
    company_key;
