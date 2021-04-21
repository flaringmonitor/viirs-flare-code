CREATE TABLE IF NOT EXISTS flare_automation.flare_wells
(
    api                    TEXT,
    state                  TEXT,
    parent_ticker          TEXT,
    operator_name          TEXT,
    longitude_surface_hole FLOAT,
    latitude_surface_hole  FLOAT
);

TRUNCATE flare_automation.flare_wells;

\copy flare_automation.flare_wells FROM 'flare_wells.csv' WITH DELIMITER ',' CSV HEADER
