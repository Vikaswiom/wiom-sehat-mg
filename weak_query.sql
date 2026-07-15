-- Per Track-A CSP: the worst-first weak connections (out-of-range ONTs) for "आज ये ठीक करें".
-- Source: DBT.HOURLY_DEVICE_PING_INFLUX (per-device optical, the doc's whom-to-treat basis).
-- Weak = 15-day avg device optical below -25 dBm (calibrated: reproduces a0b6t9's ~49% in-range).
-- Identifier = DEVICE_ID (ONT serial on the router). No customer name/address → no PII in the public file.
WITH cohort AS (   -- Track-A CSPs (OP<75 at month start) mapped to their partner_id
  SELECT s.csp_id, a.partner_id
  FROM (
    SELECT csp_id, t1_oor_rate AS op0,
           ROW_NUMBER() OVER (PARTITION BY csp_id ORDER BY snapshot_date ASC) AS rn
    FROM PROD_DB.CSP_QUALITY_SERVICE_CSP_QUALITY_SERVICE.DAILY_METRIC_SNAPSHOTS
    WHERE _fivetran_active = TRUE AND snapshot_date >= DATE_TRUNC('month', CURRENT_DATE)
  ) s
  JOIN PROD_DB.CSP_GATEWAY_SERVICE_CSP_GATEWAY_SERVICE.CSP_ACCOUNT a
    ON a.csp_id = s.csp_id AND a._fivetran_active = TRUE
  WHERE s.rn = 1 AND s.op0 < 75
),
dev AS (   -- 15-day avg optical per device, only for cohort partners
  SELECT c.csp_id, p.device_id,
         AVG(p.optical_avg)        AS opt,
         SUM(p.total_pings_missed) AS missed
  FROM cohort c
  JOIN PROD_DB.DBT.HOURLY_DEVICE_PING_INFLUX p
    ON p.partner_id = c.partner_id
   AND p.date_ist >= DATEADD(day, -15, CURRENT_DATE)
   AND p.optical_avg IS NOT NULL
  GROUP BY c.csp_id, p.device_id
),
ranked AS (
  SELECT csp_id, device_id, ROUND(opt, 0) AS dbm,
         ROW_NUMBER() OVER (PARTITION BY csp_id ORDER BY opt ASC) AS rnk,
         COUNT_IF(opt < -25) OVER (PARTITION BY csp_id)           AS weak_n
  FROM dev
)
SELECT csp_id,
       weak_n,
       ARRAY_AGG(OBJECT_CONSTRUCT('d', device_id, 'v', dbm))
         WITHIN GROUP (ORDER BY rnk) AS worst
FROM ranked
WHERE rnk <= 3 AND dbm < -25
GROUP BY csp_id, weak_n
ORDER BY csp_id
