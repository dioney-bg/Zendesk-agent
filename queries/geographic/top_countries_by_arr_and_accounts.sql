/*
 * Top Countries by ARR and Account Count
 *
 * Description:
 *   Shows the top 5 countries ranked by:
 *   1. Total ARR (Annual Recurring Revenue)
 *   2. Total account count
 *   Includes "All Other Countries" aggregation and TOTAL row
 *
 * Data Source:
 *   - CS_RESET_DASHBOARD for account ARR
 *   - SALESFORCE_ACCOUNT_BCV for country assignments
 *
 * Filters Applied:
 *   - Latest SERVICE_DATE (most recent snapshot)
 *   - AS_OF_DATE = 'Quarterly'
 *   - CRM_NET_ARR_USD > 0 (positive ARR only)
 *
 * Output:
 *   Two sections:
 *   - Top 5 by ARR with percentages
 *   - Top 5 by account count with percentages
 *
 * Usage:
 *   make country-report
 *   OR
 *   snow sql -f queries/geographic/top_countries_by_arr_and_accounts.sql
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

country_summary AS (
    SELECT
        country,
        COUNT(DISTINCT crm_account_id) as accounts,
        SUM(arr) as total_arr
    FROM current_data
    GROUP BY country
),

total_summary AS (
    SELECT
        SUM(accounts) as total_accounts,
        SUM(total_arr) as total_arr
    FROM country_summary
),

ranked_by_arr AS (
    SELECT
        country,
        accounts,
        total_arr,
        ROUND(100.0 * total_arr / (SELECT total_arr FROM total_summary), 1) as pct_of_total_arr,
        ROW_NUMBER() OVER (ORDER BY total_arr DESC) as arr_rank
    FROM country_summary
),

ranked_by_accounts AS (
    SELECT
        country,
        accounts,
        total_arr,
        ROUND(100.0 * accounts / (SELECT total_accounts FROM total_summary), 1) as pct_of_total_accounts,
        ROW_NUMBER() OVER (ORDER BY accounts DESC) as account_rank
    FROM country_summary
)

-- Top 5 by ARR
SELECT
    'BY ARR' as ranking_type,
    country,
    accounts,
    CONCAT('$', ROUND(total_arr / 1000000, 1), 'M') as arr,
    CONCAT(pct_of_total_arr, '%') as pct_of_total
FROM ranked_by_arr
WHERE arr_rank <= 5

UNION ALL

SELECT
    'BY ARR' as ranking_type,
    'All Other Countries' as country,
    SUM(accounts) as accounts,
    CONCAT('$', ROUND(SUM(total_arr) / 1000000, 1), 'M') as arr,
    CONCAT(ROUND(SUM(pct_of_total_arr), 1), '%') as pct_of_total
FROM ranked_by_arr
WHERE arr_rank > 5

UNION ALL

SELECT
    'BY ARR' as ranking_type,
    'TOTAL' as country,
    SUM(accounts) as accounts,
    CONCAT('$', ROUND(SUM(total_arr) / 1000000, 1), 'M') as arr,
    '100%' as pct_of_total
FROM ranked_by_arr

UNION ALL

SELECT
    '---' as ranking_type,
    '---' as country,
    NULL as accounts,
    '---' as arr,
    '---' as pct_of_total

UNION ALL

-- Top 5 by Account Count
SELECT
    'BY ACCOUNTS' as ranking_type,
    country,
    accounts,
    CONCAT('$', ROUND(total_arr / 1000000, 1), 'M') as arr,
    CONCAT(pct_of_total_accounts, '%') as pct_of_total
FROM ranked_by_accounts
WHERE account_rank <= 5

UNION ALL

SELECT
    'BY ACCOUNTS' as ranking_type,
    'All Other Countries' as country,
    SUM(accounts) as accounts,
    CONCAT('$', ROUND(SUM(total_arr) / 1000000, 1), 'M') as arr,
    CONCAT(ROUND(SUM(pct_of_total_accounts), 1), '%') as pct_of_total
FROM ranked_by_accounts
WHERE account_rank > 5

UNION ALL

SELECT
    'BY ACCOUNTS' as ranking_type,
    'TOTAL' as country,
    SUM(accounts) as accounts,
    CONCAT('$', ROUND(SUM(total_arr) / 1000000, 1), 'M') as arr,
    '100%' as pct_of_total
FROM ranked_by_accounts;
