CREATE TABLE IF NOT EXISTS flare_automation.mapping_combined
(
 ticker2             TEXT,
 ticker              TEXT,
 company_name        TEXT,
 full_company_name   TEXT,
 dataset_filter_flag TEXT
);

TRUNCATE flare_automation.mapping_combined;

\copy flare_automation.mapping_combined FROM 'mapping_combined.csv' WITH DELIMITER ',' CSV HEADER
