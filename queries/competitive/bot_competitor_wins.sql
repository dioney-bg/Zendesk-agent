/*
 * AI Agent Wins vs Bot Competitors (Ada, Forethought, Sierra, Decagon)
 *
 * Description:
 *   Shows top 20 closed AI Agent bookings competing against standalone bot competitors
 *   Includes Ada, Forethought, Sierra, and Decagon
 *
 * Data Source:
 *   - functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings for bookings data
 *   - PRESENTATION.EDA_SALES_MARKETING.DDG_DASHBOARD_OPP_PLUS_QUOTE for competitor information
 *
 * Key Fields:
 *   - OPPORTUNITY_STATUS = 'Closed' (closed won deals)
 *   - PRODUCT_BOOKING_ARR_USD (booking ARR, not pipeline ARR)
 *   - PRODUCT IN ('Ultimate', 'Ultimate_AR', 'Copilot') (AI products)
 *   - PRIMARY_COMPETITOR_NEW__C (competitor field from DDG table)
 *
 * Competitor Logic:
 *   - Uses PRIMARY_COMPETITOR_NEW__C field (semicolon-separated list)
 *   - Searches for: Ada, Forethought, Sierra, Decagon (case insensitive)
 *   - Multiple competitors can be listed per opportunity
 *
 * Time Period:
 *   - Default: Since 2025-01-01 (change WHERE clause to adjust)
 *
 * Output:
 *   - Customer name, opportunity name, opportunity ID
 *   - Close date and month
 *   - Region and customer segment
 *   - AI Agent ARR (Ultimate + Ultimate_AR only)
 *   - Copilot ARR (Copilot only)
 *   - Total AI Booking (Agent + Copilot)
 *   - Competitor name(s)
 *
 * Usage:
 *   make bot-competitor-wins
 *   OR
 *   snow sql -f queries/competitive/bot_competitor_wins.sql
 *
 * Created: 2026-03-03
 * Author: Sales Strategy Agent
 */

WITH ai_bookings AS (
  SELECT
    p.CRM_ACCOUNT_NAME as customer_name,
    p.OPP_NAME as opportunity_name,
    p.CRM_OPPORTUNITY_ID,
    p.CLOSEDATE as close_date,
    p.PRO_FORMA_MARKET_SEGMENT as customer_segment,
    p.REGION,
    SUM(CASE WHEN p.PRODUCT IN ('Ultimate', 'Ultimate_AR')
             THEN p.PRODUCT_BOOKING_ARR_USD
             ELSE 0 END) as ai_agent_booking_arr,
    SUM(CASE WHEN p.PRODUCT = 'Copilot'
             THEN p.PRODUCT_BOOKING_ARR_USD
             ELSE 0 END) as copilot_booking_arr,
    SUM(CASE WHEN p.PRODUCT IN ('Ultimate', 'Ultimate_AR', 'Copilot')
             THEN p.PRODUCT_BOOKING_ARR_USD
             ELSE 0 END) as total_ai_booking_arr
  FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p
  WHERE p.OPPORTUNITY_STATUS = 'Closed'
    AND p.PRODUCT_BOOKING_ARR_USD > 0
    AND p.DATE_LABEL = 'today'
    AND p.PRODUCT IN ('Ultimate', 'Ultimate_AR', 'Copilot')
    AND p.CLOSEDATE >= '2025-01-01'  -- Adjust time period here
    AND p.CLOSEDATE <= CURRENT_DATE()
  GROUP BY
    p.CRM_ACCOUNT_NAME,
    p.OPP_NAME,
    p.CRM_OPPORTUNITY_ID,
    p.CLOSEDATE,
    p.PRO_FORMA_MARKET_SEGMENT,
    p.REGION
  HAVING SUM(CASE WHEN p.PRODUCT IN ('Ultimate', 'Ultimate_AR')
                  THEN p.PRODUCT_BOOKING_ARR_USD
                  ELSE 0 END) > 0
)
SELECT
  b.customer_name,
  b.opportunity_name,
  b.CRM_OPPORTUNITY_ID as opportunity_id,
  b.close_date,
  TO_CHAR(b.close_date, 'YYYY-MM') as month,
  b.REGION as region,
  b.customer_segment as customer_size,
  CONCAT('$', ROUND(b.ai_agent_booking_arr / 1000, 1), 'K') as ai_agent_arr,
  CONCAT('$', ROUND(b.copilot_booking_arr / 1000, 1), 'K') as copilot_arr,
  CONCAT('$', ROUND(b.total_ai_booking_arr / 1000, 1), 'K') as total_ai_booking,
  d.PRIMARY_COMPETITOR_NEW__C as competitor
FROM ai_bookings b
INNER JOIN PRESENTATION.EDA_SALES_MARKETING.DDG_DASHBOARD_OPP_PLUS_QUOTE d
  ON b.CRM_OPPORTUNITY_ID = d.OPPORTUNITY_ID
WHERE d.PRIMARY_COMPETITOR_NEW__C IS NOT NULL
  AND (d.PRIMARY_COMPETITOR_NEW__C ILIKE '%Ada%'
    OR d.PRIMARY_COMPETITOR_NEW__C ILIKE '%Forethought%'
    OR d.PRIMARY_COMPETITOR_NEW__C ILIKE '%Sierra%'
    OR d.PRIMARY_COMPETITOR_NEW__C ILIKE '%Decagon%')
ORDER BY b.ai_agent_booking_arr DESC
LIMIT 20;
