-- FY26 Q1 ES Bookings - Last Year
-- Closed won ES opportunities as of same date last year

WITH es_bookings AS (
    SELECT
        OPPORTUNITY_TYPE,
        PRODUCT_BOOKING_ARR_USD as arr,
        CLOSEDATE
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    WHERE DATE_LABEL = '-4 quarter'
        AND PRODUCT = 'ES'
        AND OPPORTUNITY_STATUS = 'Closed'
        AND opportunity_is_commissionable = TRUE
        AND OPPORTUNITY_TYPE IN ('Expansion', 'New Business')
        AND stage_2_plus_date_c IS NOT NULL
        AND CLOSEDATE >= '2025-02-01'
        AND CLOSEDATE <= DATEADD(year, -1, CURRENT_DATE())
        AND PRODUCT_BOOKING_ARR_USD > 0
)
SELECT
    'Total' as metric,
    ROUND(SUM(arr), 0) as ly_bookings_arr
FROM es_bookings

UNION ALL

SELECT
    'New Business' as metric,
    ROUND(SUM(arr), 0) as ly_bookings_arr
FROM es_bookings
WHERE OPPORTUNITY_TYPE = 'New Business'

UNION ALL

SELECT
    'X-Sell / Up-Sell' as metric,
    ROUND(SUM(arr), 0) as ly_bookings_arr
FROM es_bookings
WHERE OPPORTUNITY_TYPE = 'Expansion'

ORDER BY
    CASE metric
        WHEN 'Total' THEN 1
        WHEN 'New Business' THEN 2
        WHEN 'X-Sell / Up-Sell' THEN 3
    END;
