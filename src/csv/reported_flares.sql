CREATE TABLE IF NOT EXISTS flare_automation.reported_flares
(
    run      TEXT,
    state    TEXT,
    key_type TEXT,
    key      TEXT,
    month    DATE,
    operator TEXT,
    flared   FLOAT
);

TRUNCATE flare_automation.reported_flares;

\copy flare_automation.reported_flares FROM 'reported_flares.csv' WITH DELIMITER ',' CSV HEADER
