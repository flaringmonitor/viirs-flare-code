CREATE TABLE IF NOT EXISTS flare_automation.lower_48_basins
(
    id          INT,
    geom        GEOMETRY,
    basin       TEXT,
    lithology   TEXT,
    shale_play  TEXT,
    source      TEXT,
    area_sq_mi  FLOAT,
    area_sq_km  FLOAT,
    age_shale   TEXT
);

TRUNCATE flare_automation.lower_48_basins;

\copy flare_automation.lower_48_basins FROM 'lower_48_basins.csv' WITH DELIMITER ',' CSV HEADER;

--UPDATE flare_automation.lower_48_basins SET geom = ST_setsrid(geom, 4326);

CREATE INDEX IF NOT EXISTS l48_geom ON flare_automation.lower_48_basins USING gist(geom);
