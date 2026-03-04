/*
 * AMER Leader - Industry Growth Analysis YoY
 *
 * Description:
 *   Shows top 5 industries by YoY ARR growth for AMER leader only
 *   AMER leader = accounts in AMER region (excluding SMB/Digital segments)
 *
 * Data Source:
 *   - CS_RESET_DASHBOARD for ARR, accounts, and leader assignment
 *   - SALESFORCE_ACCOUNT_BCV for industry assignments (current assignment applied to both periods)
 *
 * Leader Assignment Logic:
 *   - SMB/Digital segments → Leader = segment name (excluded from AMER)
 *   - All other segments → Leader = PRO_FORMA_REGION
 *   - This query filters for: PRO_FORMA_REGION = 'AMER' AND segment NOT IN ('SMB', 'Digital')
 *
 * Comparison Period:
 *   - Current: Latest SERVICE_DATE
 *   - Prior: ~13 months prior
 *
 * Output:
 *   - Top 5 industries by ARR growth (absolute $)
 *   - Current/prior accounts and ARR
 *   - Growth in $ and %
 *   - "All Other Industries" aggregation
 *   - TOTAL row for validation
 *
 * Usage:
 *   make amer-industry-growth
 *   OR
 *   snow sql -f queries/industry/amer_industry_growth_yoy.sql
 *
 * Created: 2026-03-03
 * Author: Sales Strategy Agent
 */

WITH current_amer AS (
    SELECT
        c.CRM_ACCOUNT_ID as crm_account_id,
        COALESCE(s.SALES_STRATEGY_INDUSTRY_C, 'Unknown/Not Assigned') as industry,
        c.CRM_NET_ARR_USD as arr
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD c
    LEFT JOIN CLEANSED.SALESFORCE.SALESFORCE_ACCOUNT_BCV s
        ON c.CRM_ACCOUNT_ID = s.ID
    WHERE c.SERVICE_DATE = (SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD)
        AND c.AS_OF_DATE = 'Quarterly'
        AND c.CRM_NET_ARR_USD > 0
        AND CASE
            WHEN c.PRO_FORMA_MARKET_SEGMENT IN ('SMB', 'Digital')
                THEN c.PRO_FORMA_MARKET_SEGMENT
            ELSE COALESCE(c.PRO_FORMA_REGION, 'Unknown')
        END = 'AMER'
),

prior_amer AS (
    SELECT
        c.CRM_ACCOUNT_ID as crm_account_id,
        COALESCE(s.SALES_STRATEGY_INDUSTRY_C, 'Unknown/Not Assigned') as industry,
        c.CRM_NET_ARR_USD as arr
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD c
    LEFT JOIN CLEANSED.SALESFORCE.SALESFORCE_ACCOUNT_BCV s
        ON c.CRM_ACCOUNT_ID = s.ID
    WHERE c.SERVICE_DATE = DATEADD(month, -13, (SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD))
        AND c.AS_OF_DATE = 'Quarterly'
        AND c.CRM_NET_ARR_USD > 0
        AND CASE
            WHEN c.PRO_FORMA_MARKET_SEGMENT IN ('SMB', 'Digital')
                THEN c.PRO_FORMA_MARKET_SEGMENT
            ELSE COALESCE(c.PRO_FORMA_REGION, 'Unknown')
        END = 'AMER'
),

industry_comparison AS (
    SELECT
        COALESCE(cur.industry, pri.industry) as industry,
        COUNT(DISTINCT cur.crm_account_id) as current_accounts,
        COUNT(DISTINCT pri.crm_account_id) as prior_accounts,
        COUNT(DISTINCT cur.crm_account_id) - COUNT(DISTINCT pri.crm_account_id) as account_growth,
        COALESCE(SUM(cur.arr), 0) as current_arr,
        COALESCE(SUM(pri.arr), 0) as prior_arr,
        COALESCE(SUM(cur.arr), 0) - COALESCE(SUM(pri.arr), 0) as arr_growth_usd,
        CASE
            WHEN COALESCE(SUM(pri.arr), 0) = 0 THEN NULL
            ELSE ROUND(100.0 * (COALESCE(SUM(cur.arr), 0) - COALESCE(SUM(pri.arr), 0)) / SUM(pri.arr), 1)
        END as arr_growth_pct
    FROM current_amer cur
    FULL OUTER JOIN prior_amer pri
        ON cur.crm_account_id = pri.crm_account_id
        AND cur.industry = pri.industry
    GROUP BY COALESCE(cur.industry, pri.industry)
),

ranked_by_arr_growth AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY arr_growth_usd DESC) as growth_rank
    FROM industry_comparison
)

-- Top 5 by ARR Growth
SELECT
    industry,
    current_accounts,
    prior_accounts,
    account_growth,
    CONCAT('$', ROUND(current_arr / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(prior_arr / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(arr_growth_usd / 1000000, 1), 'M') as arr_growth,
    CONCAT(COALESCE(arr_growth_pct, 0), '%') as arr_growth_pct
FROM ranked_by_arr_growth
WHERE growth_rank <= 5

UNION ALL

SELECT
    'All Other Industries' as industry,
    SUM(current_accounts) as current_accounts,
    SUM(prior_accounts) as prior_accounts,
    SUM(account_growth) as account_growth,
    CONCAT('$', ROUND(SUM(current_arr) / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(SUM(prior_arr) / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(SUM(arr_growth_usd) / 1000000, 1), 'M') as arr_growth,
    CONCAT(ROUND(100.0 * SUM(arr_growth_usd) / NULLIF(SUM(prior_arr), 0), 1), '%') as arr_growth_pct
FROM ranked_by_arr_growth
WHERE growth_rank > 5

UNION ALL

SELECT
    'TOTAL (AMER)' as industry,
    SUM(current_accounts) as current_accounts,
    SUM(prior_accounts) as prior_accounts,
    SUM(account_growth) as account_growth,
    CONCAT('$', ROUND(SUM(current_arr) / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(SUM(prior_arr) / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(SUM(arr_growth_usd) / 1000000, 1), 'M') as arr_growth,
    CONCAT(ROUND(100.0 * SUM(arr_growth_usd) / NULLIF(SUM(prior_arr), 0), 1), '%') as arr_growth_pct
FROM ranked_by_arr_growth;
