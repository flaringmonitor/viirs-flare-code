SELECT 
    {our_timestamp} AS run,
    'NM' AS state,
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
        (lat_gmtco BETWEEN 31 AND 38) AND 
        (lon_gmtco BETWEEN -109.2 AND -102.8) AND 
        temp_bb > 1399 AND
        -- (date_ltz BETWEEN '2020-08-01' AND '2021-01-01')
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
        state_abbr = 'NM' 
) py 

ON 
    St_intersects (py.geom,pt.point)
