#!/usr/bin/env python3
"""
Generate AI Control & Impact Dashboard Data - Full Dataset
Fetches ALL customer penetration data for dynamic product selection
"""

import subprocess
import json
import sys
from datetime import datetime

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

def get_full_penetration_data():
    """
    Get complete customer penetration data for all products
    This allows client-side dynamic filtering
    """

    query = """
WITH customers AS (
    SELECT
        CRM_ACCOUNT_ID,
        CRM_NET_ARR_USD,
        PRO_FORMA_MARKET_SEGMENT,
        CASE
            WHEN PRO_FORMA_REGION = 'NA' THEN 'AMER'
            ELSE PRO_FORMA_REGION
        END AS region
    FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD
    WHERE SERVICE_DATE = (SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD)
        AND AS_OF_DATE = 'Quarterly'
        AND CRM_NET_ARR_USD > 0
),

ai_penetration AS (
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
)

SELECT
    COUNT(*) AS total_customers,

    -- AI Agents Advanced
    COUNT(CASE WHEN COALESCE(a.has_aaa, FALSE) = TRUE THEN 1 END) AS aaa_count,

    -- AI Agents Essential
    COUNT(CASE WHEN COALESCE(a.has_ai_agents_essential, FALSE) = TRUE THEN 1 END) AS ai_agents_essential_count,

    -- Copilot
    COUNT(CASE WHEN COALESCE(a.has_copilot, FALSE) = TRUE THEN 1 END) AS copilot_count,

    -- Generative Search
    COUNT(CASE WHEN COALESCE(a.has_gen_search, FALSE) = TRUE THEN 1 END) AS gen_search_count,

    -- QA Paid
    COUNT(CASE WHEN COALESCE(a.has_qa, FALSE) = TRUE THEN 1 END) AS qa_count,

    -- Gen AI (Any)
    COUNT(CASE WHEN COALESCE(a.has_gen_ai, FALSE) = TRUE THEN 1 END) AS gen_ai_count,

    -- Paid AI (Any)
    COUNT(CASE WHEN COALESCE(a.has_paid_ai, FALSE) = TRUE THEN 1 END) AS paid_ai_count,

    -- Combinations for each pair (pre-compute common combinations)
    -- AAA + Copilot
    COUNT(CASE WHEN COALESCE(a.has_aaa, FALSE) = TRUE AND COALESCE(a.has_copilot, FALSE) = TRUE THEN 1 END) AS aaa_and_copilot,
    COUNT(CASE WHEN COALESCE(a.has_aaa, FALSE) = TRUE OR COALESCE(a.has_copilot, FALSE) = TRUE THEN 1 END) AS aaa_or_copilot,
    COUNT(CASE WHEN COALESCE(a.has_aaa, FALSE) = TRUE AND COALESCE(a.has_copilot, FALSE) = FALSE THEN 1 END) AS aaa_only_not_copilot,
    COUNT(CASE WHEN COALESCE(a.has_copilot, FALSE) = TRUE AND COALESCE(a.has_aaa, FALSE) = FALSE THEN 1 END) AS copilot_only_not_aaa,

    -- AAA + Gen Search
    COUNT(CASE WHEN COALESCE(a.has_aaa, FALSE) = TRUE AND COALESCE(a.has_gen_search, FALSE) = TRUE THEN 1 END) AS aaa_and_gen_search,
    COUNT(CASE WHEN COALESCE(a.has_aaa, FALSE) = TRUE OR COALESCE(a.has_gen_search, FALSE) = TRUE THEN 1 END) AS aaa_or_gen_search,

    -- Copilot + Gen Search
    COUNT(CASE WHEN COALESCE(a.has_copilot, FALSE) = TRUE AND COALESCE(a.has_gen_search, FALSE) = TRUE THEN 1 END) AS copilot_and_gen_search,
    COUNT(CASE WHEN COALESCE(a.has_copilot, FALSE) = TRUE OR COALESCE(a.has_gen_search, FALSE) = TRUE THEN 1 END) AS copilot_or_gen_search,

    -- Gen AI + Copilot
    COUNT(CASE WHEN COALESCE(a.has_gen_ai, FALSE) = TRUE AND COALESCE(a.has_copilot, FALSE) = TRUE THEN 1 END) AS gen_ai_and_copilot,
    COUNT(CASE WHEN COALESCE(a.has_gen_ai, FALSE) = TRUE OR COALESCE(a.has_copilot, FALSE) = TRUE THEN 1 END) AS gen_ai_or_copilot,

    -- Paid AI + Copilot
    COUNT(CASE WHEN COALESCE(a.has_paid_ai, FALSE) = TRUE AND COALESCE(a.has_copilot, FALSE) = TRUE THEN 1 END) AS paid_ai_and_copilot,
    COUNT(CASE WHEN COALESCE(a.has_paid_ai, FALSE) = TRUE OR COALESCE(a.has_copilot, FALSE) = TRUE THEN 1 END) AS paid_ai_or_copilot,

    -- AI Agents Essential + Copilot
    COUNT(CASE WHEN COALESCE(a.has_ai_agents_essential, FALSE) = TRUE AND COALESCE(a.has_copilot, FALSE) = TRUE THEN 1 END) AS ai_agents_essential_and_copilot,
    COUNT(CASE WHEN COALESCE(a.has_ai_agents_essential, FALSE) = TRUE OR COALESCE(a.has_copilot, FALSE) = TRUE THEN 1 END) AS ai_agents_essential_or_copilot,

    -- QA + Copilot
    COUNT(CASE WHEN COALESCE(a.has_qa, FALSE) = TRUE AND COALESCE(a.has_copilot, FALSE) = TRUE THEN 1 END) AS qa_and_copilot,
    COUNT(CASE WHEN COALESCE(a.has_qa, FALSE) = TRUE OR COALESCE(a.has_copilot, FALSE) = TRUE THEN 1 END) AS qa_or_copilot

FROM customers c
LEFT JOIN ai_penetration a ON c.CRM_ACCOUNT_ID = a.crm_account_id
"""

    print("Fetching complete penetration dataset...", file=sys.stderr)
    results = run_snowflake_query(query)

    if not results:
        print("Error: Query returned no results", file=sys.stderr)
        return None

    data = results[0]

    # Build product definitions
    products = {
        'aaa': {
            'name': 'AI Agents Advanced',
            'count': data['AAA_COUNT']
        },
        'ai_agents_essential': {
            'name': 'AI Agents Essential',
            'count': data['AI_AGENTS_ESSENTIAL_COUNT']
        },
        'copilot': {
            'name': 'Copilot',
            'count': data['COPILOT_COUNT']
        },
        'gen_search': {
            'name': 'Generative Search',
            'count': data['GEN_SEARCH_COUNT']
        },
        'qa': {
            'name': 'QA (Paid)',
            'count': data['QA_COUNT']
        },
        'gen_ai': {
            'name': 'Gen AI (Any)',
            'count': data['GEN_AI_COUNT']
        },
        'paid_ai': {
            'name': 'Paid AI (Any)',
            'count': data['PAID_AI_COUNT']
        }
    }

    # Build combination lookup (for quick retrieval)
    combinations = {
        'aaa_copilot': {
            'both': data['AAA_AND_COPILOT'],
            'either': data['AAA_OR_COPILOT'],
            'a_only': data['AAA_ONLY_NOT_COPILOT'],
            'b_only': data['COPILOT_ONLY_NOT_AAA']
        },
        'aaa_gen_search': {
            'both': data['AAA_AND_GEN_SEARCH'],
            'either': data['AAA_OR_GEN_SEARCH']
        },
        'copilot_gen_search': {
            'both': data['COPILOT_AND_GEN_SEARCH'],
            'either': data['COPILOT_OR_GEN_SEARCH']
        },
        'gen_ai_copilot': {
            'both': data['GEN_AI_AND_COPILOT'],
            'either': data['GEN_AI_OR_COPILOT']
        },
        'paid_ai_copilot': {
            'both': data['PAID_AI_AND_COPILOT'],
            'either': data['PAID_AI_OR_COPILOT']
        },
        'ai_agents_essential_copilot': {
            'both': data['AI_AGENTS_ESSENTIAL_AND_COPILOT'],
            'either': data['AI_AGENTS_ESSENTIAL_OR_COPILOT']
        },
        'qa_copilot': {
            'both': data['QA_AND_COPILOT'],
            'either': data['QA_OR_COPILOT']
        }
    }

    return {
        'total_customers': data['TOTAL_CUSTOMERS'],
        'products': products,
        'combinations': combinations,
        'generated_at': datetime.now().isoformat()
    }

def main():
    print("Generating AI Control & Impact Dashboard - Full Dataset...", file=sys.stderr)

    data = get_full_penetration_data()

    if data:
        # Output JSON for embedding in HTML
        print(json.dumps(data, indent=2))
    else:
        print("Error: Failed to generate data", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
