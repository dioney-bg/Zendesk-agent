/*
 * Countries with Account Decreases - Year over Year
 *
 * Description:
 *   Shows top 5 countries with biggest account decreases YoY
 *   Includes current/prior ARR to show if ARR grew despite account loss
 *   Provides complete context with increases/no-change summary
 *
 * Data Source:
 *   - CS_RESET_DASHBOARD for ARR and accounts
 *   - SALESFORCE_ACCOUNT_BCV for country assignments (current assignment applied to both periods)
 *
 * Comparison Period:
 *   - Current: Latest SERVICE_DATE
 *   - Prior: ~13 months prior
 *
 * Output:
 *   - Top 5 countries with biggest account losses
 *   - "All Other Countries" (with decreases)
 *   - Summary breakdown: decreases/increases/no-change
 *   - TOTAL row for validation
 *
 * Usage:
 *   make country-decreases-report
 *   OR
 *   snow sql -f queries/geographic/country_decreases_yoy.sql
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
        COUNT(DISTINCT cur.crm_account_id) - COUNT(DISTINCT pri.crm_account_id) as account_change,
        COALESCE(SUM(cur.arr), 0) as current_arr,
        COALESCE(SUM(pri.arr), 0) as prior_arr,
        COALESCE(SUM(cur.arr), 0) - COALESCE(SUM(pri.arr), 0) as arr_change_usd,
        CASE
            WHEN COALESCE(SUM(pri.arr), 0) = 0 THEN NULL
            ELSE ROUND(100.0 * (COALESCE(SUM(cur.arr), 0) - COALESCE(SUM(pri.arr), 0)) / SUM(pri.arr), 1)
        END as arr_change_pct
    FROM current_data cur
    FULL OUTER JOIN prior_year_data pri
        ON cur.crm_account_id = pri.crm_account_id
        AND cur.country = pri.country
    GROUP BY COALESCE(cur.country, pri.country)
),

ranked_by_account_decrease AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY account_change ASC) as decrease_rank
    FROM country_comparison
    WHERE account_change < 0
),

decreased AS (
    SELECT
        COUNT(*) as country_count,
        SUM(current_accounts) as current_accounts,
        SUM(prior_accounts) as prior_accounts,
        SUM(account_change) as account_change,
        SUM(current_arr) as current_arr,
        SUM(prior_arr) as prior_arr,
        SUM(arr_change_usd) as arr_change
    FROM country_comparison
    WHERE account_change < 0
),

increased AS (
    SELECT
        COUNT(*) as country_count,
        SUM(current_accounts) as current_accounts,
        SUM(prior_accounts) as prior_accounts,
        SUM(account_change) as account_change,
        SUM(current_arr) as current_arr,
        SUM(prior_arr) as prior_arr,
        SUM(arr_change_usd) as arr_change
    FROM country_comparison
    WHERE account_change > 0
),

no_change AS (
    SELECT
        COUNT(*) as country_count,
        SUM(current_accounts) as current_accounts,
        SUM(prior_accounts) as prior_accounts,
        SUM(account_change) as account_change,
        SUM(current_arr) as current_arr,
        SUM(prior_arr) as prior_arr,
        SUM(arr_change_usd) as arr_change
    FROM country_comparison
    WHERE account_change = 0
)

-- Top 5 with biggest decreases
SELECT
    country,
    current_accounts,
    prior_accounts,
    account_change,
    CONCAT('$', ROUND(current_arr / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(prior_arr / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(arr_change_usd / 1000000, 1), 'M') as arr_change,
    CONCAT(COALESCE(arr_change_pct, 0), '%') as arr_change_pct
FROM ranked_by_account_decrease
WHERE decrease_rank <= 5

UNION ALL

SELECT
    'All Other Countries (w/ Decreases)' as country,
    SUM(current_accounts) as current_accounts,
    SUM(prior_accounts) as prior_accounts,
    SUM(account_change) as account_change,
    CONCAT('$', ROUND(SUM(current_arr) / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(SUM(prior_arr) / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(SUM(arr_change_usd) / 1000000, 1), 'M') as arr_change,
    CONCAT(ROUND(100.0 * SUM(arr_change_usd) / NULLIF(SUM(prior_arr), 0), 1), '%') as arr_change_pct
FROM ranked_by_account_decrease
WHERE decrease_rank > 5

UNION ALL

SELECT
    'SUBTOTAL (Countries w/ Decreases)' as country,
    SUM(current_accounts) as current_accounts,
    SUM(prior_accounts) as prior_accounts,
    SUM(account_change) as account_change,
    CONCAT('$', ROUND(SUM(current_arr) / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(SUM(prior_arr) / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(SUM(arr_change_usd) / 1000000, 1), 'M') as arr_change,
    CONCAT(ROUND(100.0 * SUM(arr_change_usd) / NULLIF(SUM(prior_arr), 0), 1), '%') as arr_change_pct
FROM ranked_by_account_decrease

UNION ALL

SELECT '---', NULL, NULL, NULL, '---', '---', '---', '---'

UNION ALL

-- Summary breakdown
SELECT
    'Countries with DECREASES' as category,
    country_count,
    current_accounts,
    prior_accounts,
    account_change,
    CONCAT('$', ROUND(current_arr / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(prior_arr / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(arr_change / 1000000, 1), 'M') as arr_change,
    CONCAT(ROUND(100.0 * arr_change / NULLIF(prior_arr, 0), 1), '%') as arr_change_pct
FROM decreased

UNION ALL

SELECT
    'Countries with INCREASES' as category,
    country_count,
    current_accounts,
    prior_accounts,
    account_change,
    CONCAT('$', ROUND(current_arr / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(prior_arr / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(arr_change / 1000000, 1), 'M') as arr_change,
    CONCAT(ROUND(100.0 * arr_change / NULLIF(prior_arr, 0), 1), '%') as arr_change_pct
FROM increased

UNION ALL

SELECT
    'Countries with NO CHANGE' as category,
    country_count,
    current_accounts,
    prior_accounts,
    account_change,
    CONCAT('$', ROUND(current_arr / 1000000, 1), 'M') as current_arr,
    CONCAT('$', ROUND(prior_arr / 1000000, 1), 'M') as prior_arr,
    CONCAT('$', ROUND(arr_change / 1000000, 1), 'M') as arr_change,
    CONCAT(ROUND(100.0 * arr_change / NULLIF(prior_arr, 0), 1), '%') as arr_change_pct
FROM no_change

UNION ALL

SELECT
    'TOTAL (ALL COUNTRIES)' as category,
    (SELECT SUM(country_count) FROM (SELECT country_count FROM decreased UNION ALL SELECT country_count FROM increased UNION ALL SELECT country_count FROM no_change) x),
    (SELECT SUM(current_accounts) FROM (SELECT current_accounts FROM decreased UNION ALL SELECT current_accounts FROM increased UNION ALL SELECT current_accounts FROM no_change) x),
    (SELECT SUM(prior_accounts) FROM (SELECT prior_accounts FROM decreased UNION ALL SELECT prior_accounts FROM increased UNION ALL SELECT prior_accounts FROM no_change) x),
    (SELECT SUM(account_change) FROM (SELECT account_change FROM decreased UNION ALL SELECT account_change FROM increased UNION ALL SELECT account_change FROM no_change) x),
    CONCAT('$', ROUND((SELECT SUM(current_arr) FROM (SELECT current_arr FROM decreased UNION ALL SELECT current_arr FROM increased UNION ALL SELECT current_arr FROM no_change) x) / 1000000, 1), 'M'),
    CONCAT('$', ROUND((SELECT SUM(prior_arr) FROM (SELECT prior_arr FROM decreased UNION ALL SELECT prior_arr FROM increased UNION ALL SELECT prior_arr FROM no_change) x) / 1000000, 1), 'M'),
    CONCAT('$', ROUND((SELECT SUM(arr_change) FROM (SELECT arr_change FROM decreased UNION ALL SELECT arr_change FROM increased UNION ALL SELECT arr_change FROM no_change) x) / 1000000, 1), 'M'),
    CONCAT(ROUND(100.0 * (SELECT SUM(arr_change) FROM (SELECT arr_change FROM decreased UNION ALL SELECT arr_change FROM increased UNION ALL SELECT arr_change FROM no_change) x) / NULLIF((SELECT SUM(prior_arr) FROM (SELECT prior_arr FROM decreased UNION ALL SELECT prior_arr FROM increased UNION ALL SELECT prior_arr FROM no_change) x), 0), 1), '%');
