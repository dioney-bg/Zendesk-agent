#!/usr/bin/env python3
"""
Generate AI Control & Impact Dashboard Data - Enhanced with time comparisons and pipeline data
"""

import subprocess
import json
import sys
from datetime import datetime, timedelta

def run_snowflake_query(query):
    """Execute Snowflake query and return results as list of dicts"""
    try:
        result = subprocess.run(
            ['/Applications/SnowflakeCLI.app/Contents/MacOS/snow', 'sql', '-q', query, '--format', 'json'],
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout.strip()
        if not output:
            print("Error: Empty output from Snowflake", file=sys.stderr)
            return []

        try:
            data = json.loads(output)
            return data if isinstance(data, list) else [data]
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            print(f"Output was: {output[:500]}", file=sys.stderr)
            return []

    except subprocess.CalledProcessError as e:
        print(f"Error executing query: {e}", file=sys.stderr)
        print(f"STDERR: {e.stderr}", file=sys.stderr)
        return []

def get_enhanced_penetration_data():
    """
    Get complete customer penetration data with time comparisons and pipeline info
    """

    query = """
WITH customer_base_current AS (
    SELECT
        CRM_ACCOUNT_ID,
        CRM_NET_ARR_USD,
        PRO_FORMA_MARKET_SEGMENT,
        CASE WHEN PRO_FORMA_REGION = 'NA' THEN 'AMER' ELSE PRO_FORMA_REGION END AS region
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
    WHERE SERVICE_DATE = (SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD)
        AND AS_OF_DATE = 'Quarterly'
        AND CRM_NET_ARR_USD > 0
),

customer_base_lq AS (
    SELECT
        CRM_ACCOUNT_ID,
        CRM_NET_ARR_USD
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
    WHERE SERVICE_DATE = DATEADD(month, -3, (SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD))
        AND AS_OF_DATE = 'Quarterly'
        AND CRM_NET_ARR_USD > 0
),

customer_base_lm AS (
    SELECT
        CRM_ACCOUNT_ID,
        CRM_NET_ARR_USD
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
    WHERE SERVICE_DATE = DATEADD(month, -1, (SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD))
        AND AS_OF_DATE = 'Quarterly'
        AND CRM_NET_ARR_USD > 0
),

ai_penetration_current AS (
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

ai_penetration_lq AS (
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
    WHERE source_snapshot_date = DATEADD(month, -3, DATEADD(day, -2, CURRENT_DATE()))
),

ai_penetration_lm AS (
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
    WHERE source_snapshot_date = DATEADD(month, -1, DATEADD(day, -2, CURRENT_DATE()))
),

open_pipeline AS (
    SELECT DISTINCT
        CRM_ACCOUNT_ID,
        TRUE AS has_open_pipe
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    WHERE DATE_LABEL = 'today'
        AND OPPORTUNITY_STATUS = 'Open'
        AND PRODUCT = 'Total Booking'
        AND PRODUCT_ARR_USD > 0
        AND opportunity_is_commissionable = TRUE
        AND stage_2_plus_date_c IS NOT NULL
),

lost_opps_12m AS (
    SELECT DISTINCT
        CRM_ACCOUNT_ID,
        TRUE AS has_lost_opp
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    WHERE DATE_LABEL = 'today'
        AND OPPORTUNITY_STATUS = 'Lost'
        AND PRODUCT = 'Total Booking'
        AND CLOSEDATE >= DATEADD(month, -12, CURRENT_DATE())
        AND opportunity_is_commissionable = TRUE
        AND stage_2_plus_date_c IS NOT NULL
),

combined_current AS (
    SELECT
        c.CRM_ACCOUNT_ID,
        COALESCE(a.has_aaa, FALSE) AS has_aaa,
        COALESCE(a.has_copilot, FALSE) AS has_copilot,
        COALESCE(a.has_ai_agents_essential, FALSE) AS has_ai_agents_essential,
        COALESCE(a.has_gen_search, FALSE) AS has_gen_search,
        COALESCE(a.has_qa, FALSE) AS has_qa,
        COALESCE(a.has_gen_ai, FALSE) AS has_gen_ai,
        COALESCE(a.has_paid_ai, FALSE) AS has_paid_ai,
        COALESCE(op.has_open_pipe, FALSE) AS has_open_pipe,
        COALESCE(lo.has_lost_opp, FALSE) AS has_lost_opp
    FROM customer_base_current c
    LEFT JOIN ai_penetration_current a ON c.CRM_ACCOUNT_ID = a.crm_account_id
    LEFT JOIN open_pipeline op ON c.CRM_ACCOUNT_ID = op.CRM_ACCOUNT_ID
    LEFT JOIN lost_opps_12m lo ON c.CRM_ACCOUNT_ID = lo.CRM_ACCOUNT_ID
),

combined_lq AS (
    SELECT
        c.CRM_ACCOUNT_ID,
        COALESCE(a.has_aaa, FALSE) AS has_aaa,
        COALESCE(a.has_copilot, FALSE) AS has_copilot,
        COALESCE(a.has_ai_agents_essential, FALSE) AS has_ai_agents_essential,
        COALESCE(a.has_gen_search, FALSE) AS has_gen_search,
        COALESCE(a.has_qa, FALSE) AS has_qa,
        COALESCE(a.has_gen_ai, FALSE) AS has_gen_ai,
        COALESCE(a.has_paid_ai, FALSE) AS has_paid_ai
    FROM customer_base_lq c
    LEFT JOIN ai_penetration_lq a ON c.CRM_ACCOUNT_ID = a.crm_account_id
),

combined_lm AS (
    SELECT
        c.CRM_ACCOUNT_ID,
        COALESCE(a.has_aaa, FALSE) AS has_aaa,
        COALESCE(a.has_copilot, FALSE) AS has_copilot,
        COALESCE(a.has_ai_agents_essential, FALSE) AS has_ai_agents_essential,
        COALESCE(a.has_gen_search, FALSE) AS has_gen_search,
        COALESCE(a.has_qa, FALSE) AS has_qa,
        COALESCE(a.has_gen_ai, FALSE) AS has_gen_ai,
        COALESCE(a.has_paid_ai, FALSE) AS has_paid_ai
    FROM customer_base_lm c
    LEFT JOIN ai_penetration_lm a ON c.CRM_ACCOUNT_ID = a.crm_account_id
)

SELECT
    -- Current period metrics
    COUNT(DISTINCT curr.CRM_ACCOUNT_ID) AS total_customers_current,

    -- Product counts - Current
    COUNT(DISTINCT CASE WHEN curr.has_aaa = TRUE THEN curr.CRM_ACCOUNT_ID END) AS aaa_count_current,
    COUNT(DISTINCT CASE WHEN curr.has_copilot = TRUE THEN curr.CRM_ACCOUNT_ID END) AS copilot_count_current,
    COUNT(DISTINCT CASE WHEN curr.has_ai_agents_essential = TRUE THEN curr.CRM_ACCOUNT_ID END) AS ai_agents_essential_count_current,
    COUNT(DISTINCT CASE WHEN curr.has_gen_search = TRUE THEN curr.CRM_ACCOUNT_ID END) AS gen_search_count_current,
    COUNT(DISTINCT CASE WHEN curr.has_qa = TRUE THEN curr.CRM_ACCOUNT_ID END) AS qa_count_current,
    COUNT(DISTINCT CASE WHEN curr.has_gen_ai = TRUE THEN curr.CRM_ACCOUNT_ID END) AS gen_ai_count_current,
    COUNT(DISTINCT CASE WHEN curr.has_paid_ai = TRUE THEN curr.CRM_ACCOUNT_ID END) AS paid_ai_count_current,

    -- AAA + Copilot combinations - Current
    COUNT(DISTINCT CASE WHEN curr.has_aaa = TRUE AND curr.has_copilot = TRUE THEN curr.CRM_ACCOUNT_ID END) AS aaa_and_copilot_current,
    COUNT(DISTINCT CASE WHEN curr.has_aaa = TRUE OR curr.has_copilot = TRUE THEN curr.CRM_ACCOUNT_ID END) AS aaa_or_copilot_current,
    COUNT(DISTINCT CASE WHEN curr.has_aaa = TRUE AND curr.has_copilot = FALSE THEN curr.CRM_ACCOUNT_ID END) AS aaa_only_not_copilot_current,
    COUNT(DISTINCT CASE WHEN curr.has_copilot = TRUE AND curr.has_aaa = FALSE THEN curr.CRM_ACCOUNT_ID END) AS copilot_only_not_aaa_current,

    -- Not penetrated breakdowns - Current (AAA + Copilot example)
    COUNT(DISTINCT CASE WHEN curr.has_aaa = FALSE AND curr.has_copilot = FALSE AND curr.has_open_pipe = TRUE THEN curr.CRM_ACCOUNT_ID END) AS not_pen_with_pipe_current,
    COUNT(DISTINCT CASE WHEN curr.has_aaa = FALSE AND curr.has_copilot = FALSE AND curr.has_open_pipe = FALSE AND curr.has_lost_opp = TRUE THEN curr.CRM_ACCOUNT_ID END) AS not_pen_with_lost_current,
    COUNT(DISTINCT CASE WHEN curr.has_aaa = FALSE AND curr.has_copilot = FALSE AND curr.has_open_pipe = FALSE AND curr.has_lost_opp = FALSE THEN curr.CRM_ACCOUNT_ID END) AS not_pen_no_activity_current,

    -- Last Quarter metrics
    COUNT(DISTINCT lq.CRM_ACCOUNT_ID) AS total_customers_lq,
    COUNT(DISTINCT CASE WHEN lq.has_aaa = TRUE OR lq.has_copilot = TRUE THEN lq.CRM_ACCOUNT_ID END) AS aaa_or_copilot_lq,

    -- Last Month metrics
    COUNT(DISTINCT lm.CRM_ACCOUNT_ID) AS total_customers_lm,
    COUNT(DISTINCT CASE WHEN lm.has_aaa = TRUE OR lm.has_copilot = TRUE THEN lm.CRM_ACCOUNT_ID END) AS aaa_or_copilot_lm

FROM combined_current curr
LEFT JOIN combined_lq lq ON 1=1
LEFT JOIN combined_lm lm ON 1=1
"""

    print("Fetching enhanced penetration dataset with time comparisons...", file=sys.stderr)
    results = run_snowflake_query(query)

    if not results:
        print("Error: Query returned no results", file=sys.stderr)
        return None

    data = results[0]

    # Build response structure
    return {
        'current': {
            'total_customers': data['TOTAL_CUSTOMERS_CURRENT'],
            'products': {
                'aaa': {'name': 'AI Agents Advanced', 'count': data['AAA_COUNT_CURRENT']},
                'ai_agents_essential': {'name': 'AI Agents Essential', 'count': data['AI_AGENTS_ESSENTIAL_COUNT_CURRENT']},
                'copilot': {'name': 'Copilot', 'count': data['COPILOT_COUNT_CURRENT']},
                'gen_search': {'name': 'Generative Search', 'count': data['GEN_SEARCH_COUNT_CURRENT']},
                'qa': {'name': 'QA (Paid)', 'count': data['QA_COUNT_CURRENT']},
                'gen_ai': {'name': 'Gen AI (Any)', 'count': data['GEN_AI_COUNT_CURRENT']},
                'paid_ai': {'name': 'Paid AI (Any)', 'count': data['PAID_AI_COUNT_CURRENT']}
            },
            'combinations': {
                'aaa_copilot': {
                    'both': data['AAA_AND_COPILOT_CURRENT'],
                    'either': data['AAA_OR_COPILOT_CURRENT'],
                    'a_only': data['AAA_ONLY_NOT_COPILOT_CURRENT'],
                    'b_only': data['COPILOT_ONLY_NOT_AAA_CURRENT'],
                    'not_pen_with_pipe': data['NOT_PEN_WITH_PIPE_CURRENT'],
                    'not_pen_with_lost': data['NOT_PEN_WITH_LOST_CURRENT'],
                    'not_pen_no_activity': data['NOT_PEN_NO_ACTIVITY_CURRENT']
                }
            }
        },
        'last_quarter': {
            'total_customers': data['TOTAL_CUSTOMERS_LQ'],
            'aaa_or_copilot': data['AAA_OR_COPILOT_LQ']
        },
        'last_month': {
            'total_customers': data['TOTAL_CUSTOMERS_LM'],
            'aaa_or_copilot': data['AAA_OR_COPILOT_LM']
        },
        'generated_at': datetime.now().isoformat()
    }

def main():
    print("Generating AI Control & Impact Dashboard - Enhanced Version...", file=sys.stderr)

    data = get_enhanced_penetration_data()

    if data:
        print(json.dumps(data, indent=2))
    else:
        print("Error: Failed to generate data", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
