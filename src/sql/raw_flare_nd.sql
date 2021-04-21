SELECT
    {our_timestamp} AS run,
    'ND' AS state,
    pt.point,
    pt.rh,
    pt.temp_bb,
    pt.date_ltz
FROM
(
    SELECT 
        point,
        rh,
        temp_bb,
        date_ltz
    FROM
        tmp_viirs
    WHERE
        (lat_gmtco BETWEEN 45.9 AND 49.2) AND 
        (lon_gmtco BETWEEN -104.2 AND -96.4) AND 
         temp_bb > 1399 AND
        (
            date_ltz BETWEEN 
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
        state_abbr = 'ND'
) py 

ON
    St_intersects(py.geom, pt.point)
