/*
 * AI Agent Pipeline vs Bot Competitors (Ada, Forethought, Sierra, Decagon)
 *
 * Description:
 *   Shows top 20 open AI Agent opportunities competing against standalone bot competitors
 *   Includes Ada, Forethought, Sierra, and Decagon
 *
 * Data Source:
 *   - functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings for pipeline data
 *   - functional.gtm_sales_ops.COMPETITORS_T for competitor information
 *
 * Key Fields:
 *   - OPPORTUNITY_STATUS = 'Open' (open opportunities, not closed)
 *   - PRODUCT_ARR_USD > 0 (pipeline ARR, not booking ARR)
 *   - opportunity_is_commissionable = TRUE (data quality filter)
 *   - stage_2_plus_date_c IS NOT NULL (data quality filter)
 *   - PRODUCT IN ('Ultimate', 'Ultimate_AR', 'Copilot') (AI products)
 *   - MAIN_COMPETITOR or MAIN_LOST_COMPETITOR (competitor fields from COMPETITORS_T)
 *
 * Competitor Logic:
 *   - Uses COMPETITORS_T table (lowercase values: ada, forethought, sierra, decagon)
 *   - Checks both MAIN_COMPETITOR and MAIN_LOST_COMPETITOR fields
 *   - Exact match on competitor names
 *
 * Time Period:
 *   - Default: Close date >= 2026-02-01 (FY2027 YTD)
 *   - Adjust WHERE clause to change time period
 *
 * Output:
 *   - Customer name, opportunity name, opportunity ID
 *   - Close date (forecast) and month
 *   - Region and customer segment
 *   - AI Agent ARR (Ultimate + Ultimate_AR only)
 *   - Copilot ARR (Copilot only)
 *   - Total AI Pipeline (Agent + Copilot)
 *   - Competitor name
 *
 * Usage:
 *   make bot-competitor-pipeline
 *   OR
 *   snow sql -f queries/competitive/bot_competitor_pipeline.sql
 *
 * Created: 2026-03-03
 * Author: Sales Strategy Agent
 */

WITH ai_pipeline AS (
  SELECT
    p.CRM_ACCOUNT_NAME as customer_name,
    p.OPP_NAME as opportunity_name,
    p.CRM_OPPORTUNITY_ID,
    p.CLOSEDATE as close_date,
    p.PRO_FORMA_MARKET_SEGMENT as customer_segment,
    p.REGION,
    SUM(CASE WHEN p.PRODUCT IN ('Ultimate', 'Ultimate_AR')
             THEN p.PRODUCT_ARR_USD
             ELSE 0 END) as ai_agent_arr,
    SUM(CASE WHEN p.PRODUCT = 'Copilot'
             THEN p.PRODUCT_ARR_USD
             ELSE 0 END) as copilot_arr,
    SUM(CASE WHEN p.PRODUCT IN ('Ultimate', 'Ultimate_AR', 'Copilot')
             THEN p.PRODUCT_ARR_USD
             ELSE 0 END) as total_ai_arr
  FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p
  WHERE p.OPPORTUNITY_STATUS = 'Open'
    AND p.PRODUCT_ARR_USD > 0
    AND p.opportunity_is_commissionable = TRUE
    AND p.stage_2_plus_date_c IS NOT NULL
    AND p.DATE_LABEL = 'today'
    AND p.PRODUCT IN ('Ultimate', 'Ultimate_AR', 'Copilot')
    AND p.CLOSEDATE >= '2026-02-01'  -- Adjust time period here
  GROUP BY
    p.CRM_ACCOUNT_NAME,
    p.OPP_NAME,
    p.CRM_OPPORTUNITY_ID,
    p.CLOSEDATE,
    p.PRO_FORMA_MARKET_SEGMENT,
    p.REGION
  HAVING SUM(CASE WHEN p.PRODUCT IN ('Ultimate', 'Ultimate_AR')
                  THEN p.PRODUCT_ARR_USD
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
  CONCAT('$', ROUND(b.ai_agent_arr / 1000, 1), 'K') as ai_agent_arr,
  CONCAT('$', ROUND(b.copilot_arr / 1000, 1), 'K') as copilot_arr,
  CONCAT('$', ROUND(b.total_ai_arr / 1000, 1), 'K') as total_ai_pipeline,
  COALESCE(LOWER(c.MAIN_COMPETITOR), LOWER(c.MAIN_LOST_COMPETITOR), 'Unknown') as competitor
FROM ai_pipeline b
LEFT JOIN functional.gtm_sales_ops.COMPETITORS_T c
  ON b.CRM_OPPORTUNITY_ID = c.ID
WHERE LOWER(COALESCE(c.MAIN_COMPETITOR, c.MAIN_LOST_COMPETITOR, ''))
      IN ('ada', 'forethought', 'sierra', 'decagon')
ORDER BY b.ai_agent_arr DESC
LIMIT 20;
