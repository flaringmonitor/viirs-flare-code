CREATE TABLE IF NOT EXISTS flare_automation.states
(
    id          INT,
    geom        GEOMETRY,
    state_abbr  TEXT,
    name        TEXT
);

TRUNCATE flare_automation.states;

\copy flare_automation.states FROM 'states.csv' WITH DELIMITER ',' CSV HEADER

-- UPDATE flare_automation.states SET geom = ST_setsrid(geom, 4326);

CREATE INDEX IF NOT EXISTS states_geom ON flare_automation.states USING gist(geom);
