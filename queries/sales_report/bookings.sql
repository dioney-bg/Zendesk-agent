-- FY27 Q1 Closed Bookings by Region and Segment (with WoW deltas)
-- Returns: region, segment, feb_arr, mar_arr, total_fy27_q1_arr, wow_delta

WITH closed_bookings_current AS (
  SELECT
    CASE WHEN p.REGION = 'NA' THEN 'AMER' ELSE COALESCE(p.REGION, 'Unknown') END as region,
    COALESCE(p.PRO_FORMA_MARKET_SEGMENT, 'Unknown') as segment,
    SUM(CASE WHEN MONTH(p.CLOSEDATE) = 2 AND YEAR(p.CLOSEDATE) = 2026 THEN p.PRODUCT_BOOKING_ARR_USD ELSE 0 END) as feb_arr,
    SUM(CASE WHEN MONTH(p.CLOSEDATE) = 3 AND YEAR(p.CLOSEDATE) = 2026 THEN p.PRODUCT_BOOKING_ARR_USD ELSE 0 END) as mar_arr,
    SUM(CASE WHEN p.CLOSEDATE BETWEEN '2026-02-01' AND '2026-04-30' THEN p.PRODUCT_BOOKING_ARR_USD ELSE 0 END) as total_fy27_q1_arr
  FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p
  WHERE p.OPPORTUNITY_STATUS = 'Closed'
    AND p.DATE_LABEL = 'today'
    AND p.opportunity_is_commissionable = TRUE
    AND p.stage_2_plus_date_c IS NOT NULL
    AND p.OPPORTUNITY_TYPE IN ('Expansion', 'New Business')
    AND p.PRODUCT = 'Total Booking'
    AND p.CLOSEDATE BETWEEN '2026-02-01' AND '2026-04-30'
    AND p.PRODUCT_BOOKING_ARR_USD > 0
  GROUP BY region, segment
),
closed_bookings_last_week AS (
  SELECT
    CASE WHEN p.REGION = 'NA' THEN 'AMER' ELSE COALESCE(p.REGION, 'Unknown') END as region,
    COALESCE(p.PRO_FORMA_MARKET_SEGMENT, 'Unknown') as segment,
    SUM(CASE WHEN p.CLOSEDATE BETWEEN '2026-02-01' AND '2026-04-30' THEN p.PRODUCT_BOOKING_ARR_USD ELSE 0 END) as total_fy27_q1_arr
  FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p
  WHERE p.OPPORTUNITY_STATUS = 'Closed'
    AND p.DATE_LABEL = '-1 week'
    AND p.opportunity_is_commissionable = TRUE
    AND p.stage_2_plus_date_c IS NOT NULL
    AND p.OPPORTUNITY_TYPE IN ('Expansion', 'New Business')
    AND p.PRODUCT = 'Total Booking'
    AND p.CLOSEDATE BETWEEN '2026-02-01' AND '2026-04-30'
    AND p.PRODUCT_BOOKING_ARR_USD > 0
  GROUP BY region, segment
)
SELECT
  c.region,
  c.segment,
  c.feb_arr,
  c.mar_arr,
  c.total_fy27_q1_arr,
  c.total_fy27_q1_arr - COALESCE(lw.total_fy27_q1_arr, 0) as wow_delta
FROM closed_bookings_current c
LEFT JOIN closed_bookings_last_week lw ON c.region = lw.region AND c.segment = lw.segment
ORDER BY
  CASE c.region WHEN 'AMER' THEN 1 WHEN 'EMEA' THEN 2 WHEN 'APAC' THEN 3 WHEN 'LATAM' THEN 4 ELSE 99 END,
  CASE c.segment WHEN 'Enterprise' THEN 1 WHEN 'Strategic' THEN 2 WHEN 'Public Sector' THEN 3 WHEN 'Commercial' THEN 4 WHEN 'SMB' THEN 5 WHEN 'Digital' THEN 6 ELSE 99 END;
