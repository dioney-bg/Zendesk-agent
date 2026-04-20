-- FY26 Q1 ES Pipeline Created - Last Year
-- Opportunities that became S2+ during Q1 FY26 (Feb 1 - Apr 30, 2025)

WITH es_pipeline_created AS (
    SELECT
        OPPORTUNITY_TYPE,
        PRODUCT_ARR_USD as arr,
        STAGE_2_PLUS_DATE_C
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    WHERE DATE_LABEL = '-4 quarter'
        AND PRODUCT = 'ES'
        AND opportunity_is_commissionable = TRUE
        AND OPPORTUNITY_TYPE IN ('Expansion', 'New Business')
        AND STAGE_2_PLUS_DATE_C >= '2025-02-01'
        AND STAGE_2_PLUS_DATE_C <= DATEADD(year, -1, CURRENT_DATE())
        AND PRODUCT_ARR_USD > 0
)
SELECT
    'Total' as metric,
    ROUND(SUM(arr), 0) as ly_created_arr
FROM es_pipeline_created

UNION ALL

SELECT
    'New Business' as metric,
    ROUND(SUM(arr), 0) as ly_created_arr
FROM es_pipeline_created
WHERE OPPORTUNITY_TYPE = 'New Business'

UNION ALL

SELECT
    'X-Sell / Up-Sell' as metric,
    ROUND(SUM(arr), 0) as ly_created_arr
FROM es_pipeline_created
WHERE OPPORTUNITY_TYPE = 'Expansion'

ORDER BY
    CASE metric
        WHEN 'Total' THEN 1
        WHEN 'New Business' THEN 2
        WHEN 'X-Sell / Up-Sell' THEN 3
    END;
