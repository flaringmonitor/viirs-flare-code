CREATE TABLE IF NOT EXISTS flare_automation.viirs
(
    date_ltz   TIMESTAMP,
    rh         FLOAT,
    temp_bb    INT,
    lat_gmtco  FLOAT,
    lon_gmtco  FLOAT
);

TRUNCATE flare_automation.viirs;

\copy flare_automation.viirs FROM 'viirs.csv' WITH DELIMITER ',' CSV HEADER
