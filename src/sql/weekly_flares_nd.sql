-- Weekly Flares
SELECT
    {our_timestamp} AS run,
    'ND' AS state,
    DATE_TRUNC('month', sq.date_ltz)::date AS flare_month_d,
    lpad(EXTRACT(YEAR FROM (sq.date_ltz))::text,4,'0') AS flare_year,
    lpad(EXTRACT(MONTH FROM (sq.date_ltz))::text,2,'0') AS flare_month,
    lpad(EXTRACT(week FROM (sq.date_ltz))::text,2,'0') AS flare_week,
    sq.cid,
    ST_Collect(sq.point) AS cluster_geom,
    SUM(sq.rh) as sum_rh,
    ARRAY_AGG(sq.rh ORDER BY sq.rh) AS array_rh

FROM 
(
   SELECT 
       ST_ClusterDBSCAN(flares.point,.00135,1) OVER (PARTITION BY EXTRACT(YEAR FROM (flares.date_ltz)),
       EXTRACT(WEEK FROM (flares.date_ltz))) AS cid,
       flares.point,
       flares.rh,
       flares.temp_bb,
       flares.date_ltz
    FROM 
       {raw_flare} flares
    WHERE
       state = 'ND'
) sq

GROUP BY
    EXTRACT(YEAR FROM (sq.date_ltz)),
    EXTRACT(MONTH FROM (sq.date_ltz)),
    EXTRACT(WEEK FROM (sq.date_ltz)),
    DATE_TRUNC('month', sq.date_ltz)::date,
    cid;
