DROP TABLE IF EXISTS tmp_geo;
        
CREATE TEMPORARY TABLE tmp_geo AS

SELECT
    state,
    api,
    parent_ticker, 
    operator_name,
    -- key that uses parent_ticker or operator_name as available
    COALESCE(parent_ticker, operator_name) AS company_key,
    ST_SetSRID(ST_MakePoint(longitude_surface_hole, latitude_surface_hole), 4326) AS surface_hole
FROM
    flare_automation.flare_wells
WHERE
    longitude_surface_hole IS NOT NULL AND
    latitude_surface_hole IS NOT NULL AND 
    state IN ('ND', 'NM', 'TX');

CREATE INDEX ON tmp_geo USING gist(surface_hole);
CREATE INDEX ON tmp_geo (api ASC);
