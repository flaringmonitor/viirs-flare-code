CREATE TABLE IF NOT EXISTS flare_automation.flare_prod
(
    api   TEXT,
    date  DATE,
    state TEXT
);

TRUNCATE flare_automation.flare_prod;

\copy flare_automation.flare_prod FROM 'flare_prod.csv' WITH DELIMITER ',' CSV HEADER
