-- FY27 Open Pipeline by Region, Segment, and Quarter (with WoW deltas for Q1 and Total)
-- Returns: region, segment, close_quarter, pipeline_arr, q1_wow_delta, total_wow_delta

WITH pipeline_current AS (
  SELECT
    CASE WHEN p.REGION = 'NA' THEN 'AMER' ELSE COALESCE(p.REGION, 'Unknown') END as region,
    COALESCE(p.PRO_FORMA_MARKET_SEGMENT, 'Unknown') as segment,
    CASE
      WHEN p.CLOSEDATE BETWEEN '2026-02-01' AND '2026-04-30' THEN 'Q1'
      WHEN p.CLOSEDATE BETWEEN '2026-05-01' AND '2026-07-31' THEN 'Q2'
      WHEN p.CLOSEDATE BETWEEN '2026-08-01' AND '2026-10-31' THEN 'Q3'
      WHEN p.CLOSEDATE BETWEEN '2026-11-01' AND '2027-01-31' THEN 'Q4'
    END as close_quarter,
    SUM(p.PRODUCT_ARR_USD) as pipeline_arr
  FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p
  WHERE p.OPPORTUNITY_STATUS = 'Open'
    AND p.DATE_LABEL = 'today'
    AND p.opportunity_is_commissionable = TRUE
    AND p.stage_2_plus_date_c IS NOT NULL
    AND p.OPPORTUNITY_TYPE IN ('Expansion', 'New Business')
    AND p.PRODUCT = 'Total Booking'
    AND p.PRODUCT_ARR_USD > 0
    AND p.CLOSEDATE BETWEEN '2026-02-01' AND '2027-01-31'
  GROUP BY region, segment, close_quarter
),
pipeline_last_week AS (
  SELECT
    CASE WHEN p.REGION = 'NA' THEN 'AMER' ELSE COALESCE(p.REGION, 'Unknown') END as region,
    COALESCE(p.PRO_FORMA_MARKET_SEGMENT, 'Unknown') as segment,
    CASE
      WHEN p.CLOSEDATE BETWEEN '2026-02-01' AND '2026-04-30' THEN 'Q1'
      WHEN p.CLOSEDATE BETWEEN '2026-05-01' AND '2026-07-31' THEN 'Q2'
      WHEN p.CLOSEDATE BETWEEN '2026-08-01' AND '2026-10-31' THEN 'Q3'
      WHEN p.CLOSEDATE BETWEEN '2026-11-01' AND '2027-01-31' THEN 'Q4'
    END as close_quarter,
    SUM(p.PRODUCT_ARR_USD) as pipeline_arr
  FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p
  WHERE p.OPPORTUNITY_STATUS = 'Open'
    AND p.DATE_LABEL = '-1 week'
    AND p.opportunity_is_commissionable = TRUE
    AND p.stage_2_plus_date_c IS NOT NULL
    AND p.OPPORTUNITY_TYPE IN ('Expansion', 'New Business')
    AND p.PRODUCT = 'Total Booking'
    AND p.PRODUCT_ARR_USD > 0
    AND p.CLOSEDATE BETWEEN '2026-02-01' AND '2027-01-31'
  GROUP BY region, segment, close_quarter
),
-- Calculate Q1 and Total WoW deltas per region/segment
wow_deltas AS (
  SELECT
    c.region,
    c.segment,
    SUM(CASE WHEN c.close_quarter = 'Q1' THEN c.pipeline_arr ELSE 0 END) -
      COALESCE(SUM(CASE WHEN lw.close_quarter = 'Q1' THEN lw.pipeline_arr ELSE 0 END), 0) as q1_wow_delta,
    SUM(c.pipeline_arr) - COALESCE(SUM(lw.pipeline_arr), 0) as total_wow_delta
  FROM pipeline_current c
  LEFT JOIN pipeline_last_week lw ON c.region = lw.region AND c.segment = lw.segment AND c.close_quarter = lw.close_quarter
  GROUP BY c.region, c.segment
)
SELECT
  c.region,
  c.segment,
  c.close_quarter,
  c.pipeline_arr,
  w.q1_wow_delta,
  w.total_wow_delta
FROM pipeline_current c
LEFT JOIN wow_deltas w ON c.region = w.region AND c.segment = w.segment
ORDER BY
  CASE c.region WHEN 'AMER' THEN 1 WHEN 'EMEA' THEN 2 WHEN 'APAC' THEN 3 WHEN 'LATAM' THEN 4 ELSE 99 END,
  CASE c.segment WHEN 'Enterprise' THEN 1 WHEN 'Strategic' THEN 2 WHEN 'Public Sector' THEN 3 WHEN 'Commercial' THEN 4 WHEN 'SMB' THEN 5 WHEN 'Digital' THEN 6 ELSE 99 END,
  CASE c.close_quarter WHEN 'Q1' THEN 1 WHEN 'Q2' THEN 2 WHEN 'Q3' THEN 3 WHEN 'Q4' THEN 4 END;
