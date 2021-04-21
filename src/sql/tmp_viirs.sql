DROP TABLE IF EXISTS tmp_viirs;

CREATE TEMPORARY TABLE tmp_viirs AS
SELECT
    date_ltz, rh, temp_bb, lat_gmtco, lon_gmtco,  
    ST_SetSRID(ST_MakePoint(lon_gmtco, lat_gmtco), 4326) AS point
FROM
    flare_automation.viirs;
 
CREATE INDEX ON tmp_viirs USING gist(point);
CREATE INDEX ON tmp_viirs (date_ltz ASC);
