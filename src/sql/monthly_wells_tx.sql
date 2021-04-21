SELECT
    {our_timestamp} AS run,
   'monthly' AS type,
   'TX' AS state,
    disp_dte,
    sq.cid,
    ST_Collect(sq.surface_hole) AS cluster_geom,
    ARRAY_AGG(sq.api ORDER BY sq.api) AS apis_in_cluster,
    company_key
FROM 
(
    SELECT 
        ST_ClusterDBSCAN(wells.surface_hole,.00270,1) OVER (PARTITION BY wells.disp_dte,wells.company_key) AS cid,
        wells.surface_hole,
        wells.api,
        wells.company_key,
        wells.disp_dte
    FROM 
    (
        SELECT 
            pt.api,
            pt.surface_hole,
            pt.company_key,
            pt.disp_dte
        FROM 
        (
            SELECT 
                DISTINCT 
                    w.api,
                    surface_hole,
                    company_key,
                    p.date AS disp_dte
            FROM
                tmp_geo w
            JOIN
                tmp_prod p
            ON 
                 w.api = p.api
            WHERE
                 p.state = 'TX' AND
                 w.state = 'TX' AND
                 -- p.date = '2020-08-01'
                 (
                    p.date BETWEEN 
                        {first} AND 
                        {last}
                 )

        ) pt
        
        JOIN 
        (
            SELECT 
                *
            FROM
                flare_automation.states
            WHERE 
                state_abbr = 'TX'
        ) py 
        
        ON 
            St_intersects(py.geom, pt.surface_hole)

    ) wells
) sq

GROUP BY 
    disp_dte,
    cid,
    company_key;
