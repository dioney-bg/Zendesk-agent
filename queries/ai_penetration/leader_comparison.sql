-- AI Penetration by Leader - Current vs Q4 Comparison
-- Part of: Sales Strategy Reporting Agent
-- Report: AI Penetration Report

WITH customers_current AS (
    SELECT CRM_ACCOUNT_ID,
        CASE WHEN PRO_FORMA_MARKET_SEGMENT IN ('SMB', 'Digital')
             THEN PRO_FORMA_MARKET_SEGMENT
             ELSE COALESCE(PRO_FORMA_REGION, 'Unknown')
        END AS leader
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
    WHERE SERVICE_DATE = '2026-03-02'
        AND AS_OF_DATE = 'Quarterly'
        AND CRM_NET_ARR_USD > 0
),

customers_q4_end AS (
    SELECT CRM_ACCOUNT_ID,
        CASE WHEN PRO_FORMA_MARKET_SEGMENT IN ('SMB', 'Digital')
             THEN PRO_FORMA_MARKET_SEGMENT
             ELSE COALESCE(PRO_FORMA_REGION, 'Unknown')
        END AS leader
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
    WHERE SERVICE_DATE = '2026-01-31'
        AND AS_OF_DATE = 'Quarterly'
        AND CRM_NET_ARR_USD > 0
),

ai_pen_current AS (
    SELECT DISTINCT
        crm_account_id,
        COALESCE(crm_is_copilot_penetrated, FALSE) AS has_copilot,
        COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) AS has_aaa,
        CASE WHEN COALESCE(crm_is_copilot_penetrated, FALSE) = TRUE
                OR COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) = TRUE
             THEN TRUE
             ELSE FALSE
        END AS has_any_ai
    FROM PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT
    WHERE source_snapshot_date = DATEADD(day, -2, CURRENT_DATE())
),

ai_pen_q4_end AS (
    SELECT DISTINCT
        crm_account_id,
        CASE WHEN COALESCE(crm_is_copilot_penetrated, FALSE) = TRUE
                OR COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) = TRUE
             THEN TRUE
             ELSE FALSE
        END AS has_any_ai
    FROM PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT
    WHERE source_snapshot_date = '2026-01-31'
),

current_summary AS (
    SELECT
        c.leader,
        COUNT(DISTINCT c.crm_account_id) AS total_accounts,
        COUNT(DISTINCT CASE WHEN a.has_any_ai = TRUE THEN c.crm_account_id END) AS ai_penetrated_accounts,
        COUNT(DISTINCT CASE WHEN a.has_copilot = TRUE THEN c.crm_account_id END) AS copilot_accounts,
        COUNT(DISTINCT CASE WHEN a.has_aaa = TRUE THEN c.crm_account_id END) AS aaa_accounts
    FROM customers_current c
    LEFT JOIN ai_pen_current a ON c.crm_account_id = a.crm_account_id
    GROUP BY c.leader
),

q4_end_summary AS (
    SELECT
        c.leader,
        COUNT(DISTINCT c.crm_account_id) AS total_accounts_q4,
        COUNT(DISTINCT CASE WHEN a.has_any_ai = TRUE THEN c.crm_account_id END) AS ai_penetrated_accounts_q4
    FROM customers_q4_end c
    LEFT JOIN ai_pen_q4_end a ON c.crm_account_id = a.crm_account_id
    GROUP BY c.leader
)

SELECT
    curr.leader,
    curr.total_accounts,
    curr.ai_penetrated_accounts,
    ROUND(100.0 * curr.ai_penetrated_accounts / NULLIF(curr.total_accounts, 0), 2) AS penetration_pct,
    curr.copilot_accounts,
    curr.aaa_accounts,
    q4.ai_penetrated_accounts_q4,
    ROUND(100.0 * q4.ai_penetrated_accounts_q4 / NULLIF(q4.total_accounts_q4, 0), 2) AS q4_penetration_pct,
    ROUND(
        (100.0 * curr.ai_penetrated_accounts / NULLIF(curr.total_accounts, 0)) -
        (100.0 * q4.ai_penetrated_accounts_q4 / NULLIF(q4.total_accounts_q4, 0)),
        2
    ) AS change_pct_points
FROM current_summary curr
LEFT JOIN q4_end_summary q4 ON curr.leader = q4.leader
ORDER BY
    CASE curr.leader
        WHEN 'AMER' THEN 1
        WHEN 'EMEA' THEN 2
        WHEN 'APAC' THEN 3
        WHEN 'LATAM' THEN 4
        WHEN 'SMB' THEN 5
        WHEN 'Digital' THEN 6
        ELSE 99
    END
