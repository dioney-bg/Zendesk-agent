-- Industry x Region Summary - New Business Opportunities (Last 12 Months)
-- Summarizes key metrics for planning: pipeline, bookings, win rates, deal cycles, inbound %

WITH all_opps AS (
    -- CLOSED OPPORTUNITIES
    SELECT
        p.CRM_OPPORTUNITY_ID,
        CASE
            WHEN p.REGION = 'NA' THEN 'AMER'
            ELSE COALESCE(p.REGION, 'Unknown')
        END AS region,
        COALESCE(s.SALES_STRATEGY_INDUSTRY_C, 'Unknown') AS industry,
        'Closed' AS opportunity_status,
        p.PRODUCT_BOOKING_ARR_USD AS arr_usd,
        p.stage_2_plus_date_c,
        p.CLOSEDATE,
        p.sales_play_lead
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p
    LEFT JOIN CLEANSED.SALESFORCE.SALESFORCE_ACCOUNT_BCV s
        ON p.CRM_ACCOUNT_ID = s.ID
    WHERE p.DATE_LABEL = 'today'
        AND p.opportunity_is_commissionable = TRUE
        AND p.stage_2_plus_date_c IS NOT NULL
        AND p.OPPORTUNITY_TYPE = 'New Business'
        AND p.PRODUCT = 'Total Booking'
        AND p.OPPORTUNITY_STATUS = 'Closed'
        AND p.PRODUCT_BOOKING_ARR_USD > 0
        AND p.stage_2_plus_date_c >= DATEADD(month, -12, CURRENT_DATE())

    UNION ALL

    -- LOST OPPORTUNITIES
    SELECT
        p.CRM_OPPORTUNITY_ID,
        CASE
            WHEN p.REGION = 'NA' THEN 'AMER'
            ELSE COALESCE(p.REGION, 'Unknown')
        END AS region,
        COALESCE(s.SALES_STRATEGY_INDUSTRY_C, 'Unknown') AS industry,
        'Lost' AS opportunity_status,
        p.PRODUCT_ARR_USD AS arr_usd,
        p.stage_2_plus_date_c,
        p.CLOSEDATE,
        p.sales_play_lead
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p
    LEFT JOIN CLEANSED.SALESFORCE.SALESFORCE_ACCOUNT_BCV s
        ON p.CRM_ACCOUNT_ID = s.ID
    WHERE p.DATE_LABEL = 'today'
        AND p.opportunity_is_commissionable = TRUE
        AND p.stage_2_plus_date_c IS NOT NULL
        AND p.OPPORTUNITY_TYPE = 'New Business'
        AND p.PRODUCT = 'Total Booking'
        AND p.OPPORTUNITY_STATUS = 'Lost'
        AND p.PRODUCT_ARR_USD > 0
        AND p.stage_2_plus_date_c >= DATEADD(month, -12, CURRENT_DATE())
        -- Exclude duplicates in lost
        AND COALESCE(p.DEAL_LOST_REASONMULTI__C, '') != 'Duplicate'

    UNION ALL

    -- OPEN OPPORTUNITIES
    SELECT
        p.CRM_OPPORTUNITY_ID,
        CASE
            WHEN p.REGION = 'NA' THEN 'AMER'
            ELSE COALESCE(p.REGION, 'Unknown')
        END AS region,
        COALESCE(s.SALES_STRATEGY_INDUSTRY_C, 'Unknown') AS industry,
        'Open' AS opportunity_status,
        p.PRODUCT_ARR_USD AS arr_usd,
        p.stage_2_plus_date_c,
        p.CLOSEDATE,
        p.sales_play_lead
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p
    LEFT JOIN CLEANSED.SALESFORCE.SALESFORCE_ACCOUNT_BCV s
        ON p.CRM_ACCOUNT_ID = s.ID
    WHERE p.DATE_LABEL = 'today'
        AND p.opportunity_is_commissionable = TRUE
        AND p.stage_2_plus_date_c IS NOT NULL
        AND p.OPPORTUNITY_TYPE = 'New Business'
        AND p.PRODUCT = 'Total Booking'
        AND p.OPPORTUNITY_STATUS = 'Open'
        AND p.PRODUCT_ARR_USD > 0
        AND p.stage_2_plus_date_c >= DATEADD(month, -12, CURRENT_DATE())
),

summary_metrics AS (
    SELECT
        region,
        industry,

        -- Total pipeline created (all ARR)
        SUM(arr_usd) AS total_pipeline_created,

        -- Total bookings (closed ARR only)
        SUM(CASE WHEN opportunity_status = 'Closed' THEN arr_usd ELSE 0 END) AS total_bookings,

        -- Won deal count
        COUNT(DISTINCT CASE WHEN opportunity_status = 'Closed' THEN CRM_OPPORTUNITY_ID END) AS won_deal_count,

        -- Lost deal count (for win rate calculation)
        COUNT(DISTINCT CASE WHEN opportunity_status = 'Lost' THEN CRM_OPPORTUNITY_ID END) AS lost_deal_count,

        -- Win rate: closed / (closed + lost)
        ROUND(
            100.0 * COUNT(DISTINCT CASE WHEN opportunity_status = 'Closed' THEN CRM_OPPORTUNITY_ID END) /
            NULLIF(
                COUNT(DISTINCT CASE WHEN opportunity_status = 'Closed' THEN CRM_OPPORTUNITY_ID END) +
                COUNT(DISTINCT CASE WHEN opportunity_status = 'Lost' THEN CRM_OPPORTUNITY_ID END),
                0
            ),
            1
        ) AS win_rate_pct,

        -- Average deal cycle (days from stage 2+ to close, minimum 1 day)
        ROUND(
            AVG(
                CASE
                    WHEN opportunity_status IN ('Closed', 'Lost') AND CLOSEDATE IS NOT NULL
                    THEN GREATEST(DATEDIFF(day, stage_2_plus_date_c, CLOSEDATE), 1)
                    ELSE NULL
                END
            ),
            0
        ) AS avg_deal_cycle_days,

        -- % of inbound leads
        ROUND(
            100.0 * COUNT(DISTINCT CASE WHEN LOWER(COALESCE(sales_play_lead, '')) LIKE '%inbound%' THEN CRM_OPPORTUNITY_ID END) /
            NULLIF(COUNT(DISTINCT CRM_OPPORTUNITY_ID), 0),
            1
        ) AS inbound_pct

    FROM all_opps
    GROUP BY region, industry
)

SELECT
    region,
    industry,
    total_pipeline_created,
    total_bookings,
    won_deal_count,
    win_rate_pct,
    avg_deal_cycle_days,
    inbound_pct
FROM summary_metrics
ORDER BY
    -- Region ordering
    CASE region
        WHEN 'AMER' THEN 1
        WHEN 'EMEA' THEN 2
        WHEN 'APAC' THEN 3
        WHEN 'LATAM' THEN 4
        ELSE 99
    END,
    -- Then by total bookings descending within each region
    total_bookings DESC;
