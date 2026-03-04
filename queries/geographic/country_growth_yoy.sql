/*
 * Country Growth Analysis - Year over Year
 *
 * Description:
 *   Shows top 5 countries by YoY growth in two ways:
 *   1. By ARR growth (absolute dollars)
 *   2. By account count growth
 *   Compares current period vs prior year
 *
 * Data Source:
 *   - CS_RESET_DASHBOARD for ARR and accounts
 *   - SALESFORCE_ACCOUNT_BCV for country assignments (current assignment applied to both periods)
 *
 * Comparison Period:
 *   - Current: 2026-03-02 (latest SERVICE_DATE)
 *   - Prior: 2025-01-31 (~13 months prior)
 *
 * Filters Applied:
 *   - AS_OF_DATE = 'Quarterly'
 *   - CRM_NET_ARR_USD > 0 (positive ARR only)
 *
 * Output:
 *   Two sections:
 *   - Top 5 by ARR growth with current/prior comparison
 *   - Top 5 by account growth with current/prior comparison
 *   - "All Other Countries" aggregation
 *   - TOTAL row for validation
 *
 * Usage:
 *   make country-growth-report
 *   OR
 *   snow sql -f queries/geographic/country_growth_yoy.sql
 *
 * Created: 2026-03-03
 * Author: Sales Strategy Agent
 */

WITH current_data AS (
    SELECT
        c.CRM_ACCOUNT_ID as crm_account_id,
        COALESCE(s.TERRITORY_COUNTRY_C, 'Unknown/Not Assigned') as country,
        c.CRM_NET_ARR_USD as arr
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD c
    LEFT JOIN CLEANSED.SALESFORCE.SALESFORCE_ACCOUNT_BCV s
        ON c.CRM_ACCOUNT_ID = s.ID
    WHERE c.SERVICE_DATE = (SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD)
        AND c.AS_OF_DATE = 'Quarterly'
        AND c.CRM_NET_ARR_USD > 0
),

prior_year_data AS (
    SELECT
        c.CRM_ACCOUNT_ID as crm_account_id,
        COALESCE(s.TERRITORY_COUNTRY_C, 'Unknown/Not Assigned') as country,
        c.CRM_NET_ARR_USD as arr
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD c
    LEFT JOIN CLEANSED.SALESFORCE.SALESFORCE_ACCOUNT_BCV s
        ON c.CRM_ACCOUNT_ID = s.ID
    WHERE c.SERVICE_DATE = DATEADD(month, -13, (SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD))
        AND c.AS_OF_DATE = 'Quarterly'
        AND c.CRM_NET_ARR_USD > 0
),

country_comparison AS (
    SELECT
        COALESCE(cur.country, pri.country) as country,
        COUNT(DISTINCT cur.crm_account_id) as current_accounts,
        COUNT(DISTINCT pri.crm_account_id) as prior_accounts,
        COUNT(DISTINCT cur.crm_account_id) - COUNT(DISTINCT pri.crm_account_id) as account_growth,
        COALESCE(SUM(cur.arr), 0) as current_arr,
        COALESCE(SUM(pri.arr), 0) as prior_arr,
        COALESCE(SUM(cur.arr), 0) - COALESCE(SUM(pri.arr), 0) as arr_growth_usd,
        CASE
            WHEN COALESCE(SUM(pri.arr), 0) = 0 THEN NULL
            ELSE ROUND(100.0 * (COALESCE(SUM(cur.arr), 0) - COALESCE(SUM(pri.arr), 0)) / SUM(pri.arr), 1)
        END as arr_growth_pct,
        CASE
            WHEN COUNT(DISTINCT pri.crm_account_id) = 0 THEN NULL
            ELSE ROUND(100.0 * (COUNT(DISTINCT cur.crm_account_id) - COUNT(DISTINCT pri.crm_account_id)) / COUNT(DISTINCT pri.crm_account_id), 1)
        END as account_growth_pct
    FROM current_data cur
    FULL OUTER JOIN prior_year_data pri
        ON cur.crm_account_id = pri.crm_account_id
        AND cur.country = pri.country
    GROUP BY COALESCE(cur.country, pri.country)
),

ranked_by_arr_growth AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY arr_growth_usd DESC) as arr_growth_rank
    FROM country_comparison
    WHERE arr_growth_usd IS NOT NULL
),

ranked_by_account_growth AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY account_growth DESC) as account_growth_rank
    FROM country_comparison
    WHERE account_growth IS NOT NULL
)

-- Top 5 by ARR Growth
SELECT
    'BY ARR GROWTH' as ranking_type,
    country,
    current_accounts,
    prior_accounts,
    account_growth,
    CONCAT('$', ROUND(current_arr / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(prior_arr / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(arr_growth_usd / 1000000, 1), 'M') as arr_growth,
    CONCAT(arr_growth_pct, '%') as arr_growth_pct
FROM ranked_by_arr_growth
WHERE arr_growth_rank <= 5

UNION ALL

SELECT
    'BY ARR GROWTH' as ranking_type,
    'All Other Countries' as country,
    SUM(current_accounts) as current_accounts,
    SUM(prior_accounts) as prior_accounts,
    SUM(account_growth) as account_growth,
    CONCAT('$', ROUND(SUM(current_arr) / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(SUM(prior_arr) / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(SUM(arr_growth_usd) / 1000000, 1), 'M') as arr_growth,
    CONCAT(ROUND(100.0 * SUM(arr_growth_usd) / NULLIF(SUM(prior_arr), 0), 1), '%') as arr_growth_pct
FROM ranked_by_arr_growth
WHERE arr_growth_rank > 5

UNION ALL

SELECT
    'BY ARR GROWTH' as ranking_type,
    'TOTAL' as country,
    SUM(current_accounts) as current_accounts,
    SUM(prior_accounts) as prior_accounts,
    SUM(account_growth) as account_growth,
    CONCAT('$', ROUND(SUM(current_arr) / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(SUM(prior_arr) / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(SUM(arr_growth_usd) / 1000000, 1), 'M') as arr_growth,
    CONCAT(ROUND(100.0 * SUM(arr_growth_usd) / NULLIF(SUM(prior_arr), 0), 1), '%') as arr_growth_pct
FROM ranked_by_arr_growth

UNION ALL

SELECT
    '---' as ranking_type,
    '---' as country,
    NULL, NULL, NULL,
    '---' as current_arr,
    '---' as prior_arr,
    '---' as arr_growth,
    '---' as arr_growth_pct

UNION ALL

-- Top 5 by Account Growth
SELECT
    'BY ACCOUNT GROWTH' as ranking_type,
    country,
    current_accounts,
    prior_accounts,
    account_growth,
    CONCAT('$', ROUND(current_arr / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(prior_arr / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(arr_growth_usd / 1000000, 1), 'M') as arr_growth,
    CONCAT(account_growth_pct, '%') as account_growth_pct
FROM ranked_by_account_growth
WHERE account_growth_rank <= 5

UNION ALL

SELECT
    'BY ACCOUNT GROWTH' as ranking_type,
    'All Other Countries' as country,
    SUM(current_accounts) as current_accounts,
    SUM(prior_accounts) as prior_accounts,
    SUM(account_growth) as account_growth,
    CONCAT('$', ROUND(SUM(current_arr) / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(SUM(prior_arr) / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(SUM(arr_growth_usd) / 1000000, 1), 'M') as arr_growth,
    CONCAT(ROUND(100.0 * SUM(account_growth) / NULLIF(SUM(prior_accounts), 0), 1), '%') as account_growth_pct
FROM ranked_by_account_growth
WHERE account_growth_rank > 5

UNION ALL

SELECT
    'BY ACCOUNT GROWTH' as ranking_type,
    'TOTAL' as country,
    SUM(current_accounts) as current_accounts,
    SUM(prior_accounts) as prior_accounts,
    SUM(account_growth) as account_growth,
    CONCAT('$', ROUND(SUM(current_arr) / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(SUM(prior_arr) / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(SUM(arr_growth_usd) / 1000000, 1), 'M') as arr_growth,
    CONCAT(ROUND(100.0 * SUM(account_growth) / NULLIF(SUM(prior_accounts), 0), 1), '%') as account_growth_pct
FROM ranked_by_account_growth;
