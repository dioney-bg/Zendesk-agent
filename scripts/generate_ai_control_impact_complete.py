#!/usr/bin/env python3
"""
AI Control & Impact Dashboard - Complete Data Generator
Generates full dataset with all products, time comparisons, and pipeline breakdowns
"""

import subprocess
import json
import sys
from datetime import datetime

def run_snowflake_query(query):
    """Execute Snowflake query and return results"""
    try:
        result = subprocess.run(
            ['/Applications/SnowflakeCLI.app/Contents/MacOS/snow', 'sql', '-q', query, '--format', 'json'],
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout.strip()
        if not output:
            return []

        data = json.loads(output)
        return data if isinstance(data, list) else [data]

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(f"STDERR: {e.stderr}", file=sys.stderr)
        return []

def get_complete_dashboard_data():
    """
    Get complete dashboard data with all products and time periods
    """

    # Step 1: Get available service dates for time comparisons
    dates_query = """
    SELECT DISTINCT SERVICE_DATE, COUNT(DISTINCT CRM_ACCOUNT_ID) as customer_count
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
    WHERE AS_OF_DATE = 'Quarterly'
      AND CRM_NET_ARR_USD > 0
      AND SERVICE_DATE >= DATEADD(month, -4, CURRENT_DATE())
    GROUP BY SERVICE_DATE
    ORDER BY SERVICE_DATE DESC
    """

    print("Getting available dates...", file=sys.stderr)
    dates = run_snowflake_query(dates_query)

    if not dates or len(dates) == 0:
        print("Error: Could not get dates", file=sys.stderr)
        return None

    current_date = dates[0]['SERVICE_DATE']

    # LQ and LM: Use actual available historical dates
    lq_date = dates[1]['SERVICE_DATE'] if len(dates) > 1 else current_date
    lm_date = dates[1]['SERVICE_DATE'] if len(dates) > 1 else current_date  # Use same as LQ since we only have quarterly snapshots

    lq_count = dates[1]['CUSTOMER_COUNT'] if len(dates) > 1 else 0
    print(f"Dates: Current={current_date} ({dates[0]['CUSTOMER_COUNT']:,}), LQ={lq_date} ({lq_count:,})", file=sys.stderr)

    # Step 2: Main query - get all product combinations for all 3 periods
    main_query = f"""
WITH
-- Customer bases for each period
customers_current AS (
    SELECT CRM_ACCOUNT_ID
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
    WHERE SERVICE_DATE = '{current_date}'
        AND AS_OF_DATE = 'Quarterly'
        AND CRM_NET_ARR_USD > 0
),

customers_lq AS (
    SELECT CRM_ACCOUNT_ID
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
    WHERE SERVICE_DATE = '{lq_date}'
        AND AS_OF_DATE = 'Quarterly'
        AND CRM_NET_ARR_USD > 0
),

customers_lm AS (
    SELECT CRM_ACCOUNT_ID
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
    WHERE SERVICE_DATE = '{lm_date}'
        AND AS_OF_DATE = 'Quarterly'
        AND CRM_NET_ARR_USD > 0
),

-- AI Penetration for each period
ai_current AS (
    SELECT DISTINCT
        crm_account_id,
        COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) AS has_aaa,
        COALESCE(crm_is_ai_agents_essential_penetrated, FALSE) AS has_ai_agents_essential,
        COALESCE(crm_is_copilot_penetrated, FALSE) AS has_copilot,
        COALESCE(crm_is_gen_search_penetrated, FALSE) AS has_gen_search,
        COALESCE(crm_is_qa_paid_penetrated, FALSE) AS has_qa,
        COALESCE(crm_is_gen_ai_penetrated, FALSE) AS has_gen_ai,
        COALESCE(crm_is_paid_ai_penetrated, FALSE) AS has_paid_ai
    FROM PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT
    WHERE source_snapshot_date = DATEADD(day, -2, CURRENT_DATE())
),

ai_lq AS (
    SELECT DISTINCT
        crm_account_id,
        COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) AS has_aaa,
        COALESCE(crm_is_ai_agents_essential_penetrated, FALSE) AS has_ai_agents_essential,
        COALESCE(crm_is_copilot_penetrated, FALSE) AS has_copilot,
        COALESCE(crm_is_gen_search_penetrated, FALSE) AS has_gen_search,
        COALESCE(crm_is_qa_paid_penetrated, FALSE) AS has_qa,
        COALESCE(crm_is_gen_ai_penetrated, FALSE) AS has_gen_ai,
        COALESCE(crm_is_paid_ai_penetrated, FALSE) AS has_paid_ai
    FROM PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT
    WHERE source_snapshot_date = DATEADD(day, -2, TO_DATE('{lq_date}'))
),

ai_lm AS (
    SELECT DISTINCT
        crm_account_id,
        COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) AS has_aaa,
        COALESCE(crm_is_ai_agents_essential_penetrated, FALSE) AS has_ai_agents_essential,
        COALESCE(crm_is_copilot_penetrated, FALSE) AS has_copilot,
        COALESCE(crm_is_gen_search_penetrated, FALSE) AS has_gen_search,
        COALESCE(crm_is_qa_paid_penetrated, FALSE) AS has_qa,
        COALESCE(crm_is_gen_ai_penetrated, FALSE) AS has_gen_ai,
        COALESCE(crm_is_paid_ai_penetrated, FALSE) AS has_paid_ai
    FROM PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT
    WHERE source_snapshot_date = DATEADD(day, -2, TO_DATE('{lm_date}'))
),

-- Pipeline and Lost Opps (current only)
open_pipeline AS (
    SELECT DISTINCT CRM_ACCOUNT_ID
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    WHERE DATE_LABEL = 'today'
        AND OPPORTUNITY_STATUS = 'Open'
        AND PRODUCT = 'Total Booking'
        AND PRODUCT_ARR_USD > 0
        AND opportunity_is_commissionable = TRUE
        AND stage_2_plus_date_c IS NOT NULL
),

lost_opps_12m AS (
    SELECT DISTINCT CRM_ACCOUNT_ID
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    WHERE DATE_LABEL = 'today'
        AND OPPORTUNITY_STATUS = 'Lost'
        AND PRODUCT = 'Total Booking'
        AND CLOSEDATE >= DATEADD(month, -12, CURRENT_DATE())
        AND opportunity_is_commissionable = TRUE
        AND stage_2_plus_date_c IS NOT NULL
),

-- Combined datasets
combined_current AS (
    SELECT
        c.CRM_ACCOUNT_ID,
        COALESCE(a.has_aaa, FALSE) AS has_aaa,
        COALESCE(a.has_ai_agents_essential, FALSE) AS has_ai_agents_essential,
        COALESCE(a.has_copilot, FALSE) AS has_copilot,
        COALESCE(a.has_gen_search, FALSE) AS has_gen_search,
        COALESCE(a.has_qa, FALSE) AS has_qa,
        COALESCE(a.has_gen_ai, FALSE) AS has_gen_ai,
        COALESCE(a.has_paid_ai, FALSE) AS has_paid_ai,
        CASE WHEN op.CRM_ACCOUNT_ID IS NOT NULL THEN TRUE ELSE FALSE END AS has_open_pipe,
        CASE WHEN lo.CRM_ACCOUNT_ID IS NOT NULL THEN TRUE ELSE FALSE END AS has_lost_opp
    FROM customers_current c
    LEFT JOIN ai_current a ON c.CRM_ACCOUNT_ID = a.crm_account_id
    LEFT JOIN open_pipeline op ON c.CRM_ACCOUNT_ID = op.CRM_ACCOUNT_ID
    LEFT JOIN lost_opps_12m lo ON c.CRM_ACCOUNT_ID = lo.CRM_ACCOUNT_ID
),

combined_lq AS (
    SELECT
        c.CRM_ACCOUNT_ID,
        COALESCE(a.has_aaa, FALSE) AS has_aaa,
        COALESCE(a.has_ai_agents_essential, FALSE) AS has_ai_agents_essential,
        COALESCE(a.has_copilot, FALSE) AS has_copilot,
        COALESCE(a.has_gen_search, FALSE) AS has_gen_search,
        COALESCE(a.has_qa, FALSE) AS has_qa,
        COALESCE(a.has_gen_ai, FALSE) AS has_gen_ai,
        COALESCE(a.has_paid_ai, FALSE) AS has_paid_ai
    FROM customers_lq c
    LEFT JOIN ai_lq a ON c.CRM_ACCOUNT_ID = a.crm_account_id
),

combined_lm AS (
    SELECT
        c.CRM_ACCOUNT_ID,
        COALESCE(a.has_aaa, FALSE) AS has_aaa,
        COALESCE(a.has_ai_agents_essential, FALSE) AS has_ai_agents_essential,
        COALESCE(a.has_copilot, FALSE) AS has_copilot,
        COALESCE(a.has_gen_search, FALSE) AS has_gen_search,
        COALESCE(a.has_qa, FALSE) AS has_qa,
        COALESCE(a.has_gen_ai, FALSE) AS has_gen_ai,
        COALESCE(a.has_paid_ai, FALSE) AS has_paid_ai
    FROM customers_lm c
    LEFT JOIN ai_lm a ON c.CRM_ACCOUNT_ID = a.crm_account_id
)

-- Aggregate all metrics across all periods
SELECT
    -- Totals
    COUNT(DISTINCT curr.CRM_ACCOUNT_ID) AS total_current,
    COUNT(DISTINCT lq.CRM_ACCOUNT_ID) AS total_lq,
    COUNT(DISTINCT lm.CRM_ACCOUNT_ID) AS total_lm,

    -- Individual products - Current
    COUNT(DISTINCT CASE WHEN curr.has_aaa THEN curr.CRM_ACCOUNT_ID END) AS aaa_current,
    COUNT(DISTINCT CASE WHEN curr.has_ai_agents_essential THEN curr.CRM_ACCOUNT_ID END) AS ai_agents_essential_current,
    COUNT(DISTINCT CASE WHEN curr.has_copilot THEN curr.CRM_ACCOUNT_ID END) AS copilot_current,
    COUNT(DISTINCT CASE WHEN curr.has_gen_search THEN curr.CRM_ACCOUNT_ID END) AS gen_search_current,
    COUNT(DISTINCT CASE WHEN curr.has_qa THEN curr.CRM_ACCOUNT_ID END) AS qa_current,
    COUNT(DISTINCT CASE WHEN curr.has_gen_ai THEN curr.CRM_ACCOUNT_ID END) AS gen_ai_current,
    COUNT(DISTINCT CASE WHEN curr.has_paid_ai THEN curr.CRM_ACCOUNT_ID END) AS paid_ai_current,

    -- Individual products - LQ
    COUNT(DISTINCT CASE WHEN lq.has_aaa THEN lq.CRM_ACCOUNT_ID END) AS aaa_lq,
    COUNT(DISTINCT CASE WHEN lq.has_ai_agents_essential THEN lq.CRM_ACCOUNT_ID END) AS ai_agents_essential_lq,
    COUNT(DISTINCT CASE WHEN lq.has_copilot THEN lq.CRM_ACCOUNT_ID END) AS copilot_lq,
    COUNT(DISTINCT CASE WHEN lq.has_gen_search THEN lq.CRM_ACCOUNT_ID END) AS gen_search_lq,
    COUNT(DISTINCT CASE WHEN lq.has_qa THEN lq.CRM_ACCOUNT_ID END) AS qa_lq,
    COUNT(DISTINCT CASE WHEN lq.has_gen_ai THEN lq.CRM_ACCOUNT_ID END) AS gen_ai_lq,
    COUNT(DISTINCT CASE WHEN lq.has_paid_ai THEN lq.CRM_ACCOUNT_ID END) AS paid_ai_lq,

    -- Individual products - LM
    COUNT(DISTINCT CASE WHEN lm.has_aaa THEN lm.CRM_ACCOUNT_ID END) AS aaa_lm,
    COUNT(DISTINCT CASE WHEN lm.has_ai_agents_essential THEN lm.CRM_ACCOUNT_ID END) AS ai_agents_essential_lm,
    COUNT(DISTINCT CASE WHEN lm.has_copilot THEN lm.CRM_ACCOUNT_ID END) AS copilot_lm,
    COUNT(DISTINCT CASE WHEN lm.has_gen_search THEN lm.CRM_ACCOUNT_ID END) AS gen_search_lm,
    COUNT(DISTINCT CASE WHEN lm.has_qa THEN lm.CRM_ACCOUNT_ID END) AS qa_lm,
    COUNT(DISTINCT CASE WHEN lm.has_gen_ai THEN lm.CRM_ACCOUNT_ID END) AS gen_ai_lm,
    COUNT(DISTINCT CASE WHEN lm.has_paid_ai THEN lm.CRM_ACCOUNT_ID END) AS paid_ai_lm,

    -- Pre-compute key combinations for AAA + Copilot (most common)
    COUNT(DISTINCT CASE WHEN curr.has_aaa AND curr.has_copilot THEN curr.CRM_ACCOUNT_ID END) AS aaa_and_copilot_current,
    COUNT(DISTINCT CASE WHEN curr.has_aaa OR curr.has_copilot THEN curr.CRM_ACCOUNT_ID END) AS aaa_or_copilot_current,
    COUNT(DISTINCT CASE WHEN curr.has_aaa AND NOT curr.has_copilot THEN curr.CRM_ACCOUNT_ID END) AS aaa_only_current,
    COUNT(DISTINCT CASE WHEN curr.has_copilot AND NOT curr.has_aaa THEN curr.CRM_ACCOUNT_ID END) AS copilot_only_current,

    COUNT(DISTINCT CASE WHEN lq.has_aaa OR lq.has_copilot THEN lq.CRM_ACCOUNT_ID END) AS aaa_or_copilot_lq,
    COUNT(DISTINCT CASE WHEN lm.has_aaa OR lm.has_copilot THEN lm.CRM_ACCOUNT_ID END) AS aaa_or_copilot_lm,

    -- Not penetrated with pipeline/lost breakdown (AAA + Copilot)
    COUNT(DISTINCT CASE WHEN NOT curr.has_aaa AND NOT curr.has_copilot AND curr.has_open_pipe THEN curr.CRM_ACCOUNT_ID END) AS not_pen_with_pipe_current,
    COUNT(DISTINCT CASE WHEN NOT curr.has_aaa AND NOT curr.has_copilot AND NOT curr.has_open_pipe AND curr.has_lost_opp THEN curr.CRM_ACCOUNT_ID END) AS not_pen_with_lost_current,
    COUNT(DISTINCT CASE WHEN NOT curr.has_aaa AND NOT curr.has_copilot AND NOT curr.has_open_pipe AND NOT curr.has_lost_opp THEN curr.CRM_ACCOUNT_ID END) AS not_pen_dormant_current

FROM combined_current curr
FULL OUTER JOIN combined_lq lq ON 1=1
FULL OUTER JOIN combined_lm lm ON 1=1
"""

    print("Executing main query...", file=sys.stderr)
    results = run_snowflake_query(main_query)

    if not results:
        print("Error: No results from main query", file=sys.stderr)
        return None

    data = results[0]

    # Build structured output
    output = {
        'dates': {
            'current': current_date,
            'last_quarter': lq_date,
            'last_month': lm_date
        },
        'totals': {
            'current': data['TOTAL_CURRENT'],
            'last_quarter': data['TOTAL_LQ'],
            'last_month': data['TOTAL_LM']
        },
        'products': {
            'aaa': {
                'name': 'AI Agents Advanced',
                'current': data['AAA_CURRENT'],
                'last_quarter': data['AAA_LQ'],
                'last_month': data['AAA_LM']
            },
            'ai_agents_essential': {
                'name': 'AI Agents Essential',
                'current': data['AI_AGENTS_ESSENTIAL_CURRENT'],
                'last_quarter': data['AI_AGENTS_ESSENTIAL_LQ'],
                'last_month': data['AI_AGENTS_ESSENTIAL_LM']
            },
            'copilot': {
                'name': 'Copilot',
                'current': data['COPILOT_CURRENT'],
                'last_quarter': data['COPILOT_LQ'],
                'last_month': data['COPILOT_LM']
            },
            'gen_search': {
                'name': 'Generative Search',
                'current': data['GEN_SEARCH_CURRENT'],
                'last_quarter': data['GEN_SEARCH_LQ'],
                'last_month': data['GEN_SEARCH_LM']
            },
            'qa': {
                'name': 'QA (Paid)',
                'current': data['QA_CURRENT'],
                'last_quarter': data['QA_LQ'],
                'last_month': data['QA_LM']
            },
            'gen_ai': {
                'name': 'Gen AI (Any)',
                'current': data['GEN_AI_CURRENT'],
                'last_quarter': data['GEN_AI_LQ'],
                'last_month': data['GEN_AI_LM']
            },
            'paid_ai': {
                'name': 'Paid AI (Any)',
                'current': data['PAID_AI_CURRENT'],
                'last_quarter': data['PAID_AI_LQ'],
                'last_month': data['PAID_AI_LM']
            }
        },
        'precomputed': {
            'aaa_copilot': {
                'both_current': data['AAA_AND_COPILOT_CURRENT'],
                'either_current': data['AAA_OR_COPILOT_CURRENT'],
                'a_only_current': data['AAA_ONLY_CURRENT'],
                'b_only_current': data['COPILOT_ONLY_CURRENT'],
                'either_lq': data['AAA_OR_COPILOT_LQ'],
                'either_lm': data['AAA_OR_COPILOT_LM'],
                'not_pen_with_pipe': data['NOT_PEN_WITH_PIPE_CURRENT'],
                'not_pen_with_lost': data['NOT_PEN_WITH_LOST_CURRENT'],
                'not_pen_dormant': data['NOT_PEN_DORMANT_CURRENT']
            }
        },
        'generated_at': datetime.now().isoformat()
    }

    return output

def main():
    print("=" * 70, file=sys.stderr)
    print("AI Control & Impact Dashboard - Complete Data Generator", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    data = get_complete_dashboard_data()

    if data:
        print(json.dumps(data, indent=2))
        print(f"\n✅ Data generated successfully", file=sys.stderr)
        print(f"   Total customers: {data['totals']['current']:,}", file=sys.stderr)
        print(f"   Products: {len(data['products'])}", file=sys.stderr)
        print(f"   Dates: {data['dates']['current']} (current)", file=sys.stderr)
    else:
        print("\n❌ Failed to generate data", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
