SELECT
    DISTINCT ON (state, flare_month_d, flare_week, fcid)
       {our_timestamp} AS run,
        ROW_NUMBER() OVER () AS fid,
        state,
        flare_month_d,
        flare_week,
        fcid,
        wcid,
        apis_in_cluster,
        company_key,
        sum_rh,
        array_rh,
        distance,
        wcluster_geom,
        fcluster_geom
FROM
(
    SELECT
        ST_Distance(w.cluster_geom, f.cluster_geom) AS distance,
        w.state, w.disp_dte, w.cid AS wcid,
        f.cid AS fcid, sum_rh, w.apis_in_cluster,
        w.company_key, f.array_rh,
        f.flare_month_d, f.flare_week,
        w.cluster_geom AS wcluster_geom,
        f.cluster_geom AS fcluster_geom


    FROM
        {monthly} w,
        {weekly} f

    WHERE
        w.state = f.state AND
        w.disp_dte = f.flare_month_d AND
        ST_DWithin(w.cluster_geom, f.cluster_geom, .00375)
) a

ORDER BY
    state, flare_month_d, flare_week, fcid, distance;
