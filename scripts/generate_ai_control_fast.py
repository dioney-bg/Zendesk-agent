#!/usr/bin/env python3
"""
AI Control & Impact Dashboard - FAST Generator
Two separate queries - NO cross joins
"""

import subprocess
import json
import sys
from datetime import datetime

def run_query(query):
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
    """Get dashboard data with THREE fast queries - no cross joins"""

    print("⚡ Query 1/3: Current period data...", file=sys.stderr)
    start1 = datetime.now()

    # Query 1: Current period (FAST - single date, no cross join)
    # Using Weekly data for most recent snapshot
    query1 = """
WITH
customers AS (
    SELECT CRM_ACCOUNT_ID
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
    WHERE SERVICE_DATE = (SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD WHERE AS_OF_DATE = 'Weekly' AND CRM_NET_ARR_USD > 0)
        AND AS_OF_DATE = 'Weekly'
        AND CRM_NET_ARR_USD > 0
),
ai_pen AS (
    SELECT
        crm_account_id,
        COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) AS aaa,
        COALESCE(crm_is_ai_agents_essential_penetrated, FALSE) AS aie,
        COALESCE(crm_is_copilot_penetrated, FALSE) AS cop,
        COALESCE(crm_is_gen_search_penetrated, FALSE) AS gs,
        COALESCE(crm_is_qa_paid_penetrated, FALSE) AS qa,
        COALESCE(crm_is_gen_ai_penetrated, FALSE) AS gai,
        COALESCE(crm_is_paid_ai_penetrated, FALSE) AS pai
    FROM PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT
    WHERE source_snapshot_date = DATEADD(day, -2, CURRENT_DATE())
),
pipe_lost AS (
    SELECT
        CRM_ACCOUNT_ID,
        MAX(CASE WHEN OPPORTUNITY_STATUS = 'Open' THEN 1 ELSE 0 END) AS has_pipe,
        MAX(CASE WHEN OPPORTUNITY_STATUS = 'Lost' THEN 1 ELSE 0 END) AS has_lost
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    WHERE DATE_LABEL = 'today'
        AND PRODUCT = 'Total Booking'
        AND opportunity_is_commissionable = TRUE
        AND stage_2_plus_date_c IS NOT NULL
        AND ((OPPORTUNITY_STATUS = 'Open' AND PRODUCT_ARR_USD > 0) OR (OPPORTUNITY_STATUS = 'Lost' AND CLOSEDATE >= DATEADD(month, -12, CURRENT_DATE())))
    GROUP BY CRM_ACCOUNT_ID
)
SELECT
    (SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD WHERE AS_OF_DATE = 'Weekly' AND CRM_NET_ARR_USD > 0) AS curr_date,
    COUNT(DISTINCT c.CRM_ACCOUNT_ID) AS total,
    COUNT(DISTINCT CASE WHEN a.aaa THEN c.CRM_ACCOUNT_ID END) AS aaa,
    COUNT(DISTINCT CASE WHEN a.aie THEN c.CRM_ACCOUNT_ID END) AS aie,
    COUNT(DISTINCT CASE WHEN a.cop THEN c.CRM_ACCOUNT_ID END) AS cop,
    COUNT(DISTINCT CASE WHEN a.gs THEN c.CRM_ACCOUNT_ID END) AS gs,
    COUNT(DISTINCT CASE WHEN a.qa THEN c.CRM_ACCOUNT_ID END) AS qa,
    COUNT(DISTINCT CASE WHEN a.gai THEN c.CRM_ACCOUNT_ID END) AS gai,
    COUNT(DISTINCT CASE WHEN a.pai THEN c.CRM_ACCOUNT_ID END) AS pai,
    COUNT(DISTINCT CASE WHEN a.aaa AND a.cop THEN c.CRM_ACCOUNT_ID END) AS aaa_cop_both,
    COUNT(DISTINCT CASE WHEN a.aaa OR a.cop THEN c.CRM_ACCOUNT_ID END) AS aaa_cop_either,
    COUNT(DISTINCT CASE WHEN a.aaa AND NOT a.cop THEN c.CRM_ACCOUNT_ID END) AS aaa_only,
    COUNT(DISTINCT CASE WHEN a.cop AND NOT a.aaa THEN c.CRM_ACCOUNT_ID END) AS cop_only,
    COUNT(DISTINCT CASE WHEN NOT COALESCE(a.aaa, FALSE) AND NOT COALESCE(a.cop, FALSE) AND p.has_pipe = 1 THEN c.CRM_ACCOUNT_ID END) AS not_pen_pipe,
    COUNT(DISTINCT CASE WHEN NOT COALESCE(a.aaa, FALSE) AND NOT COALESCE(a.cop, FALSE) AND COALESCE(p.has_pipe, 0) = 0 AND p.has_lost = 1 THEN c.CRM_ACCOUNT_ID END) AS not_pen_lost,
    COUNT(DISTINCT CASE WHEN NOT COALESCE(a.aaa, FALSE) AND NOT COALESCE(a.cop, FALSE) AND COALESCE(p.has_pipe, 0) = 0 AND COALESCE(p.has_lost, 0) = 0 THEN c.CRM_ACCOUNT_ID END) AS not_pen_dorm
FROM customers c
LEFT JOIN ai_pen a ON c.CRM_ACCOUNT_ID = a.crm_account_id
LEFT JOIN pipe_lost p ON c.CRM_ACCOUNT_ID = p.CRM_ACCOUNT_ID
"""

    r1 = run_query(query1)
    elapsed1 = (datetime.now() - start1).total_seconds()
    print(f"   ✅ Done in {elapsed1:.1f}s", file=sys.stderr)

    if not r1:
        return None

    curr = r1[0]

    print("⚡ Query 2/3: Last quarter data...", file=sys.stderr)
    start2 = datetime.now()

    # Query 2: LQ period (FAST - separate query, no cross join)
    # Using Weekly data for ~13 weeks back (approximately last quarter)
    query2 = """
WITH
lq_date AS (
    SELECT SERVICE_DATE AS lq_date
    FROM (
        SELECT SERVICE_DATE, ROW_NUMBER() OVER (ORDER BY SERVICE_DATE DESC) as rn
        FROM (
            SELECT DISTINCT SERVICE_DATE
            FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
            WHERE AS_OF_DATE = 'Weekly'
              AND CRM_NET_ARR_USD > 0
        )
    )
    WHERE rn = 13  -- ~13 weeks back = ~3 months
),
customers AS (
    SELECT c.CRM_ACCOUNT_ID
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD c
    CROSS JOIN lq_date d
    WHERE c.SERVICE_DATE = d.lq_date
        AND c.AS_OF_DATE = 'Weekly'
        AND c.CRM_NET_ARR_USD > 0
),
ai_pen AS (
    SELECT
        crm_account_id,
        COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) AS aaa,
        COALESCE(crm_is_ai_agents_essential_penetrated, FALSE) AS aie,
        COALESCE(crm_is_copilot_penetrated, FALSE) AS cop,
        COALESCE(crm_is_gen_search_penetrated, FALSE) AS gs,
        COALESCE(crm_is_qa_paid_penetrated, FALSE) AS qa,
        COALESCE(crm_is_gen_ai_penetrated, FALSE) AS gai,
        COALESCE(crm_is_paid_ai_penetrated, FALSE) AS pai
    FROM PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT
    CROSS JOIN lq_date d
    WHERE source_snapshot_date = DATEADD(day, -2, d.lq_date)
),
pipe_lost AS (
    SELECT
        CRM_ACCOUNT_ID,
        MAX(CASE WHEN OPPORTUNITY_STATUS = 'Open' THEN 1 ELSE 0 END) AS has_pipe,
        MAX(CASE WHEN OPPORTUNITY_STATUS = 'Lost' THEN 1 ELSE 0 END) AS has_lost
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    CROSS JOIN lq_date d
    WHERE DATE_LABEL = 'today'
        AND PRODUCT = 'Total Booking'
        AND opportunity_is_commissionable = TRUE
        AND stage_2_plus_date_c IS NOT NULL
        AND ((OPPORTUNITY_STATUS = 'Open' AND PRODUCT_ARR_USD > 0) OR (OPPORTUNITY_STATUS = 'Lost' AND CLOSEDATE >= DATEADD(month, -12, d.lq_date)))
    GROUP BY CRM_ACCOUNT_ID
)
SELECT
    (SELECT lq_date FROM lq_date) AS lq_date,
    COUNT(DISTINCT c.CRM_ACCOUNT_ID) AS total,
    -- Individual products LQ
    COUNT(DISTINCT CASE WHEN a.aaa THEN c.CRM_ACCOUNT_ID END) AS aaa,
    COUNT(DISTINCT CASE WHEN a.aie THEN c.CRM_ACCOUNT_ID END) AS aie,
    COUNT(DISTINCT CASE WHEN a.cop THEN c.CRM_ACCOUNT_ID END) AS cop,
    COUNT(DISTINCT CASE WHEN a.gs THEN c.CRM_ACCOUNT_ID END) AS gs,
    COUNT(DISTINCT CASE WHEN a.qa THEN c.CRM_ACCOUNT_ID END) AS qa,
    COUNT(DISTINCT CASE WHEN a.gai THEN c.CRM_ACCOUNT_ID END) AS gai,
    COUNT(DISTINCT CASE WHEN a.pai THEN c.CRM_ACCOUNT_ID END) AS pai,
    -- AAA + Copilot combinations LQ
    COUNT(DISTINCT CASE WHEN a.aaa OR a.cop THEN c.CRM_ACCOUNT_ID END) AS aaa_cop_either,
    COUNT(DISTINCT CASE WHEN a.aaa AND a.cop THEN c.CRM_ACCOUNT_ID END) AS aaa_cop_both,
    COUNT(DISTINCT CASE WHEN a.aaa AND NOT a.cop THEN c.CRM_ACCOUNT_ID END) AS aaa_only,
    COUNT(DISTINCT CASE WHEN a.cop AND NOT a.aaa THEN c.CRM_ACCOUNT_ID END) AS cop_only,
    COUNT(DISTINCT CASE WHEN NOT COALESCE(a.aaa, FALSE) AND NOT COALESCE(a.cop, FALSE) AND p.has_pipe = 1 THEN c.CRM_ACCOUNT_ID END) AS not_pen_pipe,
    COUNT(DISTINCT CASE WHEN NOT COALESCE(a.aaa, FALSE) AND NOT COALESCE(a.cop, FALSE) AND COALESCE(p.has_pipe, 0) = 0 AND p.has_lost = 1 THEN c.CRM_ACCOUNT_ID END) AS not_pen_lost,
    COUNT(DISTINCT CASE WHEN NOT COALESCE(a.aaa, FALSE) AND NOT COALESCE(a.cop, FALSE) AND COALESCE(p.has_pipe, 0) = 0 AND COALESCE(p.has_lost, 0) = 0 THEN c.CRM_ACCOUNT_ID END) AS not_pen_dorm
FROM customers c
LEFT JOIN ai_pen a ON c.CRM_ACCOUNT_ID = a.crm_account_id
LEFT JOIN pipe_lost p ON c.CRM_ACCOUNT_ID = p.CRM_ACCOUNT_ID
"""

    r2 = run_query(query2)
    elapsed2 = (datetime.now() - start2).total_seconds()
    print(f"   ✅ Done in {elapsed2:.1f}s", file=sys.stderr)

    lq = r2[0] if r2 else {
        'LQ_DATE': curr['CURR_DATE'],
        'TOTAL': 0,
        'AAA': 0, 'AIE': 0, 'COP': 0, 'GS': 0, 'QA': 0, 'GAI': 0, 'PAI': 0,
        'AAA_COP_EITHER': 0,
        'AAA_COP_BOTH': 0,
        'AAA_ONLY': 0,
        'COP_ONLY': 0,
        'NOT_PEN_PIPE': 0,
        'NOT_PEN_LOST': 0,
        'NOT_PEN_DORM': 0
    }

    print("⚡ Query 3/3: Last month data...", file=sys.stderr)
    start3 = datetime.now()

    # Query 3: LM period - Using Weekly data for ~5 weeks back (approximately last month)
    query3 = """
WITH
lm_date AS (
    SELECT SERVICE_DATE AS lm_date
    FROM (
        SELECT SERVICE_DATE, ROW_NUMBER() OVER (ORDER BY SERVICE_DATE DESC) as rn
        FROM (
            SELECT DISTINCT SERVICE_DATE
            FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
            WHERE AS_OF_DATE = 'Weekly'
              AND CRM_NET_ARR_USD > 0
        )
    )
    WHERE rn = 5  -- ~5 weeks back = ~1 month
),
customers AS (
    SELECT c.CRM_ACCOUNT_ID
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD c
    CROSS JOIN lm_date d
    WHERE c.SERVICE_DATE = d.lm_date
        AND c.AS_OF_DATE = 'Weekly'
        AND c.CRM_NET_ARR_USD > 0
),
ai_pen AS (
    SELECT
        crm_account_id,
        COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) AS aaa,
        COALESCE(crm_is_ai_agents_essential_penetrated, FALSE) AS aie,
        COALESCE(crm_is_copilot_penetrated, FALSE) AS cop,
        COALESCE(crm_is_gen_search_penetrated, FALSE) AS gs,
        COALESCE(crm_is_qa_paid_penetrated, FALSE) AS qa,
        COALESCE(crm_is_gen_ai_penetrated, FALSE) AS gai,
        COALESCE(crm_is_paid_ai_penetrated, FALSE) AS pai
    FROM PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT
    CROSS JOIN lm_date d
    WHERE source_snapshot_date = DATEADD(day, -2, d.lm_date)
),
pipe_lost AS (
    SELECT
        CRM_ACCOUNT_ID,
        MAX(CASE WHEN OPPORTUNITY_STATUS = 'Open' THEN 1 ELSE 0 END) AS has_pipe,
        MAX(CASE WHEN OPPORTUNITY_STATUS = 'Lost' THEN 1 ELSE 0 END) AS has_lost
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    CROSS JOIN lm_date d
    WHERE DATE_LABEL = 'today'
        AND PRODUCT = 'Total Booking'
        AND opportunity_is_commissionable = TRUE
        AND stage_2_plus_date_c IS NOT NULL
        AND ((OPPORTUNITY_STATUS = 'Open' AND PRODUCT_ARR_USD > 0) OR (OPPORTUNITY_STATUS = 'Lost' AND CLOSEDATE >= DATEADD(month, -12, d.lm_date)))
    GROUP BY CRM_ACCOUNT_ID
)
SELECT
    (SELECT lm_date FROM lm_date) AS lm_date,
    COUNT(DISTINCT c.CRM_ACCOUNT_ID) AS total,
    -- Individual products LM
    COUNT(DISTINCT CASE WHEN a.aaa THEN c.CRM_ACCOUNT_ID END) AS aaa,
    COUNT(DISTINCT CASE WHEN a.aie THEN c.CRM_ACCOUNT_ID END) AS aie,
    COUNT(DISTINCT CASE WHEN a.cop THEN c.CRM_ACCOUNT_ID END) AS cop,
    COUNT(DISTINCT CASE WHEN a.gs THEN c.CRM_ACCOUNT_ID END) AS gs,
    COUNT(DISTINCT CASE WHEN a.qa THEN c.CRM_ACCOUNT_ID END) AS qa,
    COUNT(DISTINCT CASE WHEN a.gai THEN c.CRM_ACCOUNT_ID END) AS gai,
    COUNT(DISTINCT CASE WHEN a.pai THEN c.CRM_ACCOUNT_ID END) AS pai,
    -- AAA + Copilot combinations LM
    COUNT(DISTINCT CASE WHEN a.aaa OR a.cop THEN c.CRM_ACCOUNT_ID END) AS aaa_cop_either,
    COUNT(DISTINCT CASE WHEN a.aaa AND a.cop THEN c.CRM_ACCOUNT_ID END) AS aaa_cop_both,
    COUNT(DISTINCT CASE WHEN a.aaa AND NOT a.cop THEN c.CRM_ACCOUNT_ID END) AS aaa_only,
    COUNT(DISTINCT CASE WHEN a.cop AND NOT a.aaa THEN c.CRM_ACCOUNT_ID END) AS cop_only,
    COUNT(DISTINCT CASE WHEN NOT COALESCE(a.aaa, FALSE) AND NOT COALESCE(a.cop, FALSE) AND p.has_pipe = 1 THEN c.CRM_ACCOUNT_ID END) AS not_pen_pipe,
    COUNT(DISTINCT CASE WHEN NOT COALESCE(a.aaa, FALSE) AND NOT COALESCE(a.cop, FALSE) AND COALESCE(p.has_pipe, 0) = 0 AND p.has_lost = 1 THEN c.CRM_ACCOUNT_ID END) AS not_pen_lost,
    COUNT(DISTINCT CASE WHEN NOT COALESCE(a.aaa, FALSE) AND NOT COALESCE(a.cop, FALSE) AND COALESCE(p.has_pipe, 0) = 0 AND COALESCE(p.has_lost, 0) = 0 THEN c.CRM_ACCOUNT_ID END) AS not_pen_dorm
FROM customers c
LEFT JOIN ai_pen a ON c.CRM_ACCOUNT_ID = a.crm_account_id
LEFT JOIN pipe_lost p ON c.CRM_ACCOUNT_ID = p.CRM_ACCOUNT_ID
"""

    r3 = run_query(query3)
    elapsed3 = (datetime.now() - start3).total_seconds()
    print(f"   ✅ Done in {elapsed3:.1f}s", file=sys.stderr)

    lm = r3[0] if r3 else {
        'LM_DATE': lq['LQ_DATE'],
        'TOTAL': 0,
        'AAA': 0, 'AIE': 0, 'COP': 0, 'GS': 0, 'QA': 0, 'GAI': 0, 'PAI': 0,
        'AAA_COP_EITHER': 0,
        'AAA_COP_BOTH': 0,
        'AAA_ONLY': 0,
        'COP_ONLY': 0,
        'NOT_PEN_PIPE': 0,
        'NOT_PEN_LOST': 0,
        'NOT_PEN_DORM': 0
    }

    total_time = elapsed1 + elapsed2 + elapsed3
    print(f"\n✅ Total time: {total_time:.1f}s", file=sys.stderr)

    return {
        'dates': {
            'current': curr['CURR_DATE'],
            'last_quarter': lq['LQ_DATE'],
            'last_month': lm.get('LM_DATE', lq['LQ_DATE'])
        },
        'totals': {
            'current': curr['TOTAL'],
            'last_quarter': lq['TOTAL'],
            'last_month': lm['TOTAL']
        },
        'products': {
            'aaa': {'name': 'AI Agents Advanced', 'current': curr['AAA'], 'last_quarter': lq['AAA'], 'last_month': lm['AAA']},
            'ai_agents_essential': {'name': 'AI Agents Essential', 'current': curr['AIE'], 'last_quarter': lq['AIE'], 'last_month': lm['AIE']},
            'copilot': {'name': 'Copilot', 'current': curr['COP'], 'last_quarter': lq['COP'], 'last_month': lm['COP']},
            'gen_search': {'name': 'Generative Search', 'current': curr['GS'], 'last_quarter': lq['GS'], 'last_month': lm['GS']},
            'qa': {'name': 'QA (Paid)', 'current': curr['QA'], 'last_quarter': lq['QA'], 'last_month': lm['QA']},
            'gen_ai': {'name': 'Gen AI (Any)', 'current': curr['GAI'], 'last_quarter': lq['GAI'], 'last_month': lm['GAI']},
            'paid_ai': {'name': 'Paid AI (Any)', 'current': curr['PAI'], 'last_quarter': lq['PAI'], 'last_month': lm['PAI']}
        },
        'precomputed': {
            'aaa_copilot': {
                'both_current': curr['AAA_COP_BOTH'],
                'either_current': curr['AAA_COP_EITHER'],
                'a_only_current': curr['AAA_ONLY'],
                'b_only_current': curr['COP_ONLY'],
                'either_lq': lq['AAA_COP_EITHER'],
                'either_lm': lm['AAA_COP_EITHER'],
                'both_lq': lq['AAA_COP_BOTH'],
                'both_lm': lm['AAA_COP_BOTH'],
                'a_only_lq': lq['AAA_ONLY'],
                'a_only_lm': lm['AAA_ONLY'],
                'b_only_lq': lq['COP_ONLY'],
                'b_only_lm': lm['COP_ONLY'],
                'not_pen_with_pipe': curr['NOT_PEN_PIPE'],
                'not_pen_with_lost': curr['NOT_PEN_LOST'],
                'not_pen_dormant': curr['NOT_PEN_DORM'],
                'not_pen_with_pipe_lq': lq['NOT_PEN_PIPE'],
                'not_pen_with_lost_lq': lq['NOT_PEN_LOST'],
                'not_pen_dormant_lq': lq['NOT_PEN_DORM'],
                'not_pen_with_pipe_lm': lm['NOT_PEN_PIPE'],
                'not_pen_with_lost_lm': lm['NOT_PEN_LOST'],
                'not_pen_dormant_lm': lm['NOT_PEN_DORM']
            }
        },
        'generated_at': datetime.now().isoformat()
    }

def main():
    print("=" * 70, file=sys.stderr)
    print("AI Control & Impact Dashboard - FAST Generator", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    data = get_dashboard_data()

    if data:
        print(json.dumps(data, indent=2))
        print(f"\n📊 Current: {data['totals']['current']:,}, LQ: {data['totals']['last_quarter']:,}", file=sys.stderr)
    else:
        print("\n❌ Failed", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
