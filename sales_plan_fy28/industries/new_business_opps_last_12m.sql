-- New Business Opportunities - Last 12 Months
-- All new business opportunities with positive ARR created in last 12 months (by stage 2+ date)
-- Uses Total Booking product for consolidated ARR view
-- Separated by opportunity status: Closed, Lost, Open

-- =============================================================================
-- SECTION 1: CLOSED OPPORTUNITIES (Bookings)
-- =============================================================================
SELECT
    p.CRM_OPPORTUNITY_ID,

    -- Leader assignment (SMB/Digital = segment, others = region)
    CASE
        WHEN p.PRO_FORMA_MARKET_SEGMENT IN ('SMB', 'Digital')
            THEN p.PRO_FORMA_MARKET_SEGMENT
        WHEN p.REGION = 'NA'
            THEN 'AMER'
        ELSE COALESCE(p.REGION, 'Unknown')
    END AS leader,

    -- Region (clean NA to AMER)
    CASE
        WHEN p.REGION = 'NA' THEN 'AMER'
        ELSE COALESCE(p.REGION, 'Unknown')
    END AS region,

    -- Segment
    COALESCE(p.PRO_FORMA_MARKET_SEGMENT, 'Unknown') AS segment,

    -- ARR (booking ARR for closed deals)
    p.PRODUCT_BOOKING_ARR_USD AS net_arr_usd,

    -- Account attributes from BCV
    COALESCE(s.TERRITORY_COUNTRY_C, 'Unknown') AS country,
    COALESCE(s.SALES_STRATEGY_INDUSTRY_C, 'Unknown') AS industry,
    COALESCE(s.SALES_STRATEGY_SUB_INDUSTRY_C, 'Unknown') AS subindustry,

    -- GTM team
    COALESCE(p.gtm_team, 'Unknown') AS gtm_team,

    -- Deal lost reason (NULL for closed)
    NULL AS deal_lost_reason_cleaned,

    -- Sales play lead
    p.sales_play_lead,

    -- Additional context columns
    'Closed' AS opportunity_status,
    p.stage_2_plus_date_c,
    p.CLOSEDATE,
    p.STAGE_NAME,
    p.CRM_ACCOUNT_NAME,
    p.OPP_NAME

FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p

-- Join to account attributes
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

-- =============================================================================
-- SECTION 2: LOST OPPORTUNITIES
-- =============================================================================
SELECT
    p.CRM_OPPORTUNITY_ID,

    -- Leader assignment
    CASE
        WHEN p.PRO_FORMA_MARKET_SEGMENT IN ('SMB', 'Digital')
            THEN p.PRO_FORMA_MARKET_SEGMENT
        WHEN p.REGION = 'NA'
            THEN 'AMER'
        ELSE COALESCE(p.REGION, 'Unknown')
    END AS leader,

    -- Region
    CASE
        WHEN p.REGION = 'NA' THEN 'AMER'
        ELSE COALESCE(p.REGION, 'Unknown')
    END AS region,

    -- Segment
    COALESCE(p.PRO_FORMA_MARKET_SEGMENT, 'Unknown') AS segment,

    -- ARR (pipeline ARR for lost deals)
    p.PRODUCT_ARR_USD AS net_arr_usd,

    -- Account attributes
    COALESCE(s.TERRITORY_COUNTRY_C, 'Unknown') AS country,
    COALESCE(s.SALES_STRATEGY_INDUSTRY_C, 'Unknown') AS industry,
    COALESCE(s.SALES_STRATEGY_SUB_INDUSTRY_C, 'Unknown') AS subindustry,

    -- GTM team
    COALESCE(p.gtm_team, 'Unknown') AS gtm_team,

    -- Deal lost reason
    COALESCE(p.DEAL_LOST_REASONMULTI__C, 'Not Specified') AS deal_lost_reason_cleaned,

    -- Sales play lead
    p.sales_play_lead,

    -- Additional context columns
    'Lost' AS opportunity_status,
    p.stage_2_plus_date_c,
    p.CLOSEDATE,
    p.STAGE_NAME,
    p.CRM_ACCOUNT_NAME,
    p.OPP_NAME

FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p

-- Join to account attributes
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

UNION ALL

-- =============================================================================
-- SECTION 3: OPEN OPPORTUNITIES (Pipeline)
-- =============================================================================
SELECT
    p.CRM_OPPORTUNITY_ID,

    -- Leader assignment
    CASE
        WHEN p.PRO_FORMA_MARKET_SEGMENT IN ('SMB', 'Digital')
            THEN p.PRO_FORMA_MARKET_SEGMENT
        WHEN p.REGION = 'NA'
            THEN 'AMER'
        ELSE COALESCE(p.REGION, 'Unknown')
    END AS leader,

    -- Region
    CASE
        WHEN p.REGION = 'NA' THEN 'AMER'
        ELSE COALESCE(p.REGION, 'Unknown')
    END AS region,

    -- Segment
    COALESCE(p.PRO_FORMA_MARKET_SEGMENT, 'Unknown') AS segment,

    -- ARR (pipeline ARR for open deals)
    p.PRODUCT_ARR_USD AS net_arr_usd,

    -- Account attributes
    COALESCE(s.TERRITORY_COUNTRY_C, 'Unknown') AS country,
    COALESCE(s.SALES_STRATEGY_INDUSTRY_C, 'Unknown') AS industry,
    COALESCE(s.SALES_STRATEGY_SUB_INDUSTRY_C, 'Unknown') AS subindustry,

    -- GTM team
    COALESCE(p.gtm_team, 'Unknown') AS gtm_team,

    -- Deal lost reason (NULL for open)
    NULL AS deal_lost_reason_cleaned,

    -- Sales play lead
    p.sales_play_lead,

    -- Additional context columns
    'Open' AS opportunity_status,
    p.stage_2_plus_date_c,
    p.CLOSEDATE,
    p.STAGE_NAME,
    p.CRM_ACCOUNT_NAME,
    p.OPP_NAME

FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p

-- Join to account attributes
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

-- =============================================================================
-- ORDER BY: Status (Closed, Lost, Open), then Leader, then ARR descending
-- =============================================================================
ORDER BY
    -- Status order: Closed first, Lost second, Open last
    CASE opportunity_status
        WHEN 'Closed' THEN 1
        WHEN 'Lost' THEN 2
        WHEN 'Open' THEN 3
        ELSE 99
    END,

    -- Then by leader ordering
    CASE leader
        WHEN 'AMER' THEN 1
        WHEN 'EMEA' THEN 2
        WHEN 'APAC' THEN 3
        WHEN 'LATAM' THEN 4
        WHEN 'SMB' THEN 5
        WHEN 'Digital' THEN 6
        ELSE 99
    END,

    -- Then by ARR descending
    net_arr_usd DESC;
