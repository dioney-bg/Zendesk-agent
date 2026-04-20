-- FY27 ES Open Pipeline by Quarter
-- For coverage calculations: CQ, CQ+1, CQ+2

WITH es_open_pipeline AS (
    SELECT
        OPPORTUNITY_TYPE,
        PRODUCT_ARR_USD as arr,
        CLOSEDATE,
        -- Calculate fiscal quarter
        CASE
            WHEN MONTH(CLOSEDATE) IN (2, 3, 4) THEN 'Q1'
            WHEN MONTH(CLOSEDATE) IN (5, 6, 7) THEN 'Q2'
            WHEN MONTH(CLOSEDATE) IN (8, 9, 10) THEN 'Q3'
            WHEN MONTH(CLOSEDATE) IN (11, 12, 1) THEN 'Q4'
        END as close_quarter,
        -- Calculate fiscal year
        CASE
            WHEN MONTH(CLOSEDATE) = 1 THEN YEAR(CLOSEDATE)
            ELSE YEAR(CLOSEDATE) + 1
        END as fiscal_year
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    WHERE DATE_LABEL = 'today'
        AND PRODUCT = 'ES'
        AND OPPORTUNITY_STATUS = 'Open'
        AND opportunity_is_commissionable = TRUE
        AND OPPORTUNITY_TYPE IN ('Expansion', 'New Business')
        AND stage_2_plus_date_c IS NOT NULL
        AND PRODUCT_ARR_USD > 0
        AND CLOSEDATE >= '2026-02-01'
        AND CLOSEDATE <= '2027-01-31'
)
SELECT
    close_quarter,
    'Total' as metric,
    ROUND(SUM(arr), 0) as open_pipeline_arr
FROM es_open_pipeline
WHERE fiscal_year = 2027
GROUP BY close_quarter

UNION ALL

SELECT
    close_quarter,
    'New Business' as metric,
    ROUND(SUM(arr), 0) as open_pipeline_arr
FROM es_open_pipeline
WHERE fiscal_year = 2027
    AND OPPORTUNITY_TYPE = 'New Business'
GROUP BY close_quarter

UNION ALL

SELECT
    close_quarter,
    'X-Sell / Up-Sell' as metric,
    ROUND(SUM(arr), 0) as open_pipeline_arr
FROM es_open_pipeline
WHERE fiscal_year = 2027
    AND OPPORTUNITY_TYPE = 'Expansion'
GROUP BY close_quarter

ORDER BY
    CASE close_quarter
        WHEN 'Q1' THEN 1
        WHEN 'Q2' THEN 2
        WHEN 'Q3' THEN 3
        WHEN 'Q4' THEN 4
    END,
    CASE metric
        WHEN 'Total' THEN 1
        WHEN 'New Business' THEN 2
        WHEN 'X-Sell / Up-Sell' THEN 3
    END;
