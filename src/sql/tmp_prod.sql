DROP TABLE IF EXISTS tmp_prod;

CREATE TEMPORARY TABLE tmp_prod AS

SELECT
    api,
    date,
    state
FROM
    flare_automation.flare_prod
WHERE
    state IN ('ND', 'NM', 'TX') AND
    date >= '2019-01-01'
ORDER BY
    api, date;

CREATE INDEX ON tmp_prod (api ASC, date ASC);
