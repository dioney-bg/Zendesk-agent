#!/usr/bin/env python3
"""
AI Control & Impact Dashboard - OPTIMIZED Data Generator
Fast single-pass query with pre-aggregation
"""

import subprocess
import json
import sys
from datetime import datetime

def run_query(query):
    """Execute Snowflake query and return results"""
    try:
        result = subprocess.run(
            ['/Applications/SnowflakeCLI.app/Contents/MacOS/snow', 'sql', '-q', query, '--format', 'json'],
            capture_output=True,
            text=True,
            check=True
        )
        if not result.stdout.strip():
            return []
        data = json.loads(result.stdout.strip())
        return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []

def get_dashboard_data():
    """Get all dashboard data in ONE optimized query"""

    # Single optimized query - no joins between time periods
    query = """
WITH
-- Get available dates first
dates AS (
    SELECT
        MAX(SERVICE_DATE) as current_date,
        MIN(SERVICE_DATE) as lq_date
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
    WHERE SERVICE_DATE >= DATEADD(month, -4, CURRENT_DATE())
        AND AS_OF_DATE = 'Quarterly'
        AND CRM_NET_ARR_USD > 0
),

-- Current period customers
curr_customers AS (
    SELECT c.CRM_ACCOUNT_ID
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD c
    CROSS JOIN dates d
    WHERE c.SERVICE_DATE = d.current_date
        AND c.AS_OF_DATE = 'Quarterly'
        AND c.CRM_NET_ARR_USD > 0
),

-- LQ customers
lq_customers AS (
    SELECT c.CRM_ACCOUNT_ID
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD c
    CROSS JOIN dates d
    WHERE c.SERVICE_DATE = d.lq_date
        AND c.AS_OF_DATE = 'Quarterly'
        AND c.CRM_NET_ARR_USD > 0
),

-- AI penetration current
ai_curr AS (
    SELECT
        crm_account_id,
        COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) AS has_aaa,
        COALESCE(crm_is_ai_agents_essential_penetrated, FALSE) AS has_aie,
        COALESCE(crm_is_copilot_penetrated, FALSE) AS has_cop,
        COALESCE(crm_is_gen_search_penetrated, FALSE) AS has_gs,
        COALESCE(crm_is_qa_paid_penetrated, FALSE) AS has_qa,
        COALESCE(crm_is_gen_ai_penetrated, FALSE) AS has_gai,
        COALESCE(crm_is_paid_ai_penetrated, FALSE) AS has_pai
    FROM PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT
    WHERE source_snapshot_date = DATEADD(day, -2, CURRENT_DATE())
),

-- AI penetration LQ
ai_lq AS (
    SELECT
        crm_account_id,
        COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) AS has_aaa,
        COALESCE(crm_is_copilot_penetrated, FALSE) AS has_cop
    FROM PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT
    CROSS JOIN dates d
    WHERE source_snapshot_date = DATEADD(day, -2, d.lq_date)
),

-- Pipeline and lost opps
pipeline_lost AS (
    SELECT
        CRM_ACCOUNT_ID,
        MAX(CASE WHEN OPPORTUNITY_STATUS = 'Open' THEN 1 ELSE 0 END) AS has_pipe,
        MAX(CASE WHEN OPPORTUNITY_STATUS = 'Lost' AND CLOSEDATE >= DATEADD(month, -12, CURRENT_DATE()) THEN 1 ELSE 0 END) AS has_lost
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    WHERE DATE_LABEL = 'today'
        AND PRODUCT = 'Total Booking'
        AND opportunity_is_commissionable = TRUE
        AND stage_2_plus_date_c IS NOT NULL
        AND (
            (OPPORTUNITY_STATUS = 'Open' AND PRODUCT_ARR_USD > 0)
            OR (OPPORTUNITY_STATUS = 'Lost' AND CLOSEDATE >= DATEADD(month, -12, CURRENT_DATE()))
        )
    GROUP BY CRM_ACCOUNT_ID
)

-- Aggregate everything in single pass
SELECT
    -- Dates
    (SELECT current_date FROM dates) AS current_date,
    (SELECT lq_date FROM dates) AS lq_date,

    -- Totals
    COUNT(DISTINCT cc.CRM_ACCOUNT_ID) AS total_curr,
    COUNT(DISTINCT lq.CRM_ACCOUNT_ID) AS total_lq,

    -- Products - Current
    COUNT(DISTINCT CASE WHEN ac.has_aaa THEN cc.CRM_ACCOUNT_ID END) AS aaa_curr,
    COUNT(DISTINCT CASE WHEN ac.has_aie THEN cc.CRM_ACCOUNT_ID END) AS aie_curr,
    COUNT(DISTINCT CASE WHEN ac.has_cop THEN cc.CRM_ACCOUNT_ID END) AS cop_curr,
    COUNT(DISTINCT CASE WHEN ac.has_gs THEN cc.CRM_ACCOUNT_ID END) AS gs_curr,
    COUNT(DISTINCT CASE WHEN ac.has_qa THEN cc.CRM_ACCOUNT_ID END) AS qa_curr,
    COUNT(DISTINCT CASE WHEN ac.has_gai THEN cc.CRM_ACCOUNT_ID END) AS gai_curr,
    COUNT(DISTINCT CASE WHEN ac.has_pai THEN cc.CRM_ACCOUNT_ID END) AS pai_curr,

    -- AAA + Copilot combinations
    COUNT(DISTINCT CASE WHEN ac.has_aaa AND ac.has_cop THEN cc.CRM_ACCOUNT_ID END) AS aaa_cop_both_curr,
    COUNT(DISTINCT CASE WHEN ac.has_aaa OR ac.has_cop THEN cc.CRM_ACCOUNT_ID END) AS aaa_cop_either_curr,
    COUNT(DISTINCT CASE WHEN ac.has_aaa AND NOT ac.has_cop THEN cc.CRM_ACCOUNT_ID END) AS aaa_only_curr,
    COUNT(DISTINCT CASE WHEN ac.has_cop AND NOT ac.has_aaa THEN cc.CRM_ACCOUNT_ID END) AS cop_only_curr,

    -- LQ penetration
    COUNT(DISTINCT CASE WHEN alq.has_aaa OR alq.has_cop THEN lq.CRM_ACCOUNT_ID END) AS aaa_cop_either_lq,

    -- Not penetrated breakdown
    COUNT(DISTINCT CASE WHEN NOT COALESCE(ac.has_aaa, FALSE) AND NOT COALESCE(ac.has_cop, FALSE) AND pl.has_pipe = 1 THEN cc.CRM_ACCOUNT_ID END) AS not_pen_pipe,
    COUNT(DISTINCT CASE WHEN NOT COALESCE(ac.has_aaa, FALSE) AND NOT COALESCE(ac.has_cop, FALSE) AND COALESCE(pl.has_pipe, 0) = 0 AND pl.has_lost = 1 THEN cc.CRM_ACCOUNT_ID END) AS not_pen_lost,
    COUNT(DISTINCT CASE WHEN NOT COALESCE(ac.has_aaa, FALSE) AND NOT COALESCE(ac.has_cop, FALSE) AND COALESCE(pl.has_pipe, 0) = 0 AND COALESCE(pl.has_lost, 0) = 0 THEN cc.CRM_ACCOUNT_ID END) AS not_pen_dormant

FROM curr_customers cc
LEFT JOIN ai_curr ac ON cc.CRM_ACCOUNT_ID = ac.crm_account_id
LEFT JOIN pipeline_lost pl ON cc.CRM_ACCOUNT_ID = pl.CRM_ACCOUNT_ID
CROSS JOIN lq_customers lq
LEFT JOIN ai_lq alq ON lq.CRM_ACCOUNT_ID = alq.crm_account_id
"""

    print("⚡ Running optimized single-pass query...", file=sys.stderr)
    start = datetime.now()

    results = run_query(query)

    elapsed = (datetime.now() - start).total_seconds()
    print(f"✅ Query completed in {elapsed:.1f}s", file=sys.stderr)

    if not results:
        return None

    r = results[0]

    return {
        'dates': {
            'current': r['CURRENT_DATE'],
            'last_quarter': r['LQ_DATE'],
            'last_month': r['LQ_DATE']  # Use same as LQ since quarterly snapshots
        },
        'totals': {
            'current': r['TOTAL_CURR'],
            'last_quarter': r['TOTAL_LQ'],
            'last_month': r['TOTAL_LQ']
        },
        'products': {
            'aaa': {'name': 'AI Agents Advanced', 'current': r['AAA_CURR'], 'last_quarter': 0, 'last_month': 0},
            'ai_agents_essential': {'name': 'AI Agents Essential', 'current': r['AIE_CURR'], 'last_quarter': 0, 'last_month': 0},
            'copilot': {'name': 'Copilot', 'current': r['COP_CURR'], 'last_quarter': 0, 'last_month': 0},
            'gen_search': {'name': 'Generative Search', 'current': r['GS_CURR'], 'last_quarter': 0, 'last_month': 0},
            'qa': {'name': 'QA (Paid)', 'current': r['QA_CURR'], 'last_quarter': 0, 'last_month': 0},
            'gen_ai': {'name': 'Gen AI (Any)', 'current': r['GAI_CURR'], 'last_quarter': 0, 'last_month': 0},
            'paid_ai': {'name': 'Paid AI (Any)', 'current': r['PAI_CURR'], 'last_quarter': 0, 'last_month': 0}
        },
        'precomputed': {
            'aaa_copilot': {
                'both_current': r['AAA_COP_BOTH_CURR'],
                'either_current': r['AAA_COP_EITHER_CURR'],
                'a_only_current': r['AAA_ONLY_CURR'],
                'b_only_current': r['COP_ONLY_CURR'],
                'either_lq': r['AAA_COP_EITHER_LQ'],
                'either_lm': r['AAA_COP_EITHER_LQ'],
                'not_pen_with_pipe': r['NOT_PEN_PIPE'],
                'not_pen_with_lost': r['NOT_PEN_LOST'],
                'not_pen_dormant': r['NOT_PEN_DORMANT']
            }
        },
        'generated_at': datetime.now().isoformat()
    }

def main():
    print("=" * 70, file=sys.stderr)
    print("AI Control & Impact Dashboard - OPTIMIZED Generator", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    data = get_dashboard_data()

    if data:
        print(json.dumps(data, indent=2))
        print(f"\n✅ Total: {data['totals']['current']:,} current, {data['totals']['last_quarter']:,} LQ", file=sys.stderr)
    else:
        print("\n❌ Failed", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
