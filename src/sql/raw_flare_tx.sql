SELECT 
    {our_timestamp} AS run,
    'TX' AS state,
    pt.point,
    pt.rh,
    pt.temp_bb,
    pt.date_ltz
FROM 
(
    SELECT 
        POINT,
        rh,
        temp_bb,
        date_ltz
    FROM 
        tmp_viirs
    WHERE 
        (lat_gmtco BETWEEN 25.7 AND 36.7) AND (lon_gmtco BETWEEN -106.8 AND -93) AND 
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
        state_abbr = 'TX' 
) py

ON 
   St_intersects (py.geom,pt.point)
