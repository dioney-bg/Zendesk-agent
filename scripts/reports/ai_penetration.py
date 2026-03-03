#!/usr/bin/env python3
"""
AI Penetration Report
Analysis of Copilot and AI Agents Advanced adoption across leaders
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.base_report import BaseReport


class AIPenetrationReport(BaseReport):
    """AI Penetration Report - Copilot and AAA adoption by leader"""

    def __init__(self):
        """Initialize AI Penetration report"""
        super().__init__(report_code='ai_penetration')

    def generate_query(self) -> str:
        """
        Generate or load the SQL query for this report

        Returns:
            SQL query string
        """
        # Load query from file
        query_file = Path('queries/ai_penetration/leader_comparison.sql')

        if query_file.exists():
            with open(query_file, 'r') as f:
                return f.read()
        else:
            # Fallback: inline query (keeping for compatibility)
            return self._get_inline_query()

    def _get_inline_query(self) -> str:
        """Fallback inline query if file not found"""
        return """
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
            SELECT DISTINCT crm_account_id,
                COALESCE(crm_is_copilot_penetrated, FALSE) AS has_copilot,
                COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) AS has_aaa,
                CASE WHEN COALESCE(crm_is_copilot_penetrated, FALSE) = TRUE
                        OR COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) = TRUE
                     THEN TRUE ELSE FALSE END AS has_any_ai
            FROM PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT
            WHERE source_snapshot_date = DATEADD(day, -2, CURRENT_DATE())
        ),
        ai_pen_q4_end AS (
            SELECT DISTINCT crm_account_id,
                CASE WHEN COALESCE(crm_is_copilot_penetrated, FALSE) = TRUE
                        OR COALESCE(crm_is_ai_agents_advanced_penetrated, FALSE) = TRUE
                     THEN TRUE ELSE FALSE END AS has_any_ai
            FROM PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT
            WHERE source_snapshot_date = '2026-01-31'
        ),
        current_summary AS (
            SELECT c.leader, COUNT(DISTINCT c.crm_account_id) AS total_accounts,
                COUNT(DISTINCT CASE WHEN a.has_any_ai = TRUE THEN c.crm_account_id END) AS ai_penetrated_accounts,
                COUNT(DISTINCT CASE WHEN a.has_copilot = TRUE THEN c.crm_account_id END) AS copilot_accounts,
                COUNT(DISTINCT CASE WHEN a.has_aaa = TRUE THEN c.crm_account_id END) AS aaa_accounts
            FROM customers_current c LEFT JOIN ai_pen_current a ON c.crm_account_id = a.crm_account_id
            GROUP BY c.leader
        ),
        q4_end_summary AS (
            SELECT c.leader, COUNT(DISTINCT c.crm_account_id) AS total_accounts_q4,
                COUNT(DISTINCT CASE WHEN a.has_any_ai = TRUE THEN c.crm_account_id END) AS ai_penetrated_accounts_q4
            FROM customers_q4_end c LEFT JOIN ai_pen_q4_end a ON c.crm_account_id = a.crm_account_id
            GROUP BY c.leader
        )
        SELECT curr.leader, curr.total_accounts, curr.ai_penetrated_accounts,
            ROUND(100.0 * curr.ai_penetrated_accounts / NULLIF(curr.total_accounts, 0), 2) AS penetration_pct,
            curr.copilot_accounts, curr.aaa_accounts,
            q4.ai_penetrated_accounts_q4,
            ROUND(100.0 * q4.ai_penetrated_accounts_q4 / NULLIF(q4.total_accounts_q4, 0), 2) AS q4_penetration_pct,
            ROUND((100.0 * curr.ai_penetrated_accounts / NULLIF(curr.total_accounts, 0)) -
                  (100.0 * q4.ai_penetrated_accounts_q4 / NULLIF(q4.total_accounts_q4, 0)), 2) AS change_pct_points
        FROM current_summary curr LEFT JOIN q4_end_summary q4 ON curr.leader = q4.leader
        ORDER BY CASE curr.leader
            WHEN 'AMER' THEN 1 WHEN 'EMEA' THEN 2 WHEN 'APAC' THEN 3
            WHEN 'LATAM' THEN 4 WHEN 'SMB' THEN 5 WHEN 'Digital' THEN 6
            ELSE 99 END
        """

    def format_slack(self, data: List[Dict[str, Any]]) -> str:
        """
        Custom Slack formatting for AI Penetration report

        Args:
            data: Report data

        Returns:
            Formatted Slack message
        """
        # Calculate totals
        total_accounts = sum(row["TOTAL_ACCOUNTS"] for row in data)
        total_ai_accounts = sum(row["AI_PENETRATED_ACCOUNTS"] for row in data)
        total_penetration = round(100.0 * total_ai_accounts / total_accounts, 2)

        # Calculate Q4 comparison
        q4_total_ai = sum(
            int(row["TOTAL_ACCOUNTS"] * float(row["Q4_PENETRATION_PCT"]) / 100)
            for row in data
        )
        q4_penetration = round(100.0 * q4_total_ai / total_accounts, 2)
        total_change = round(total_penetration - q4_penetration, 2)

        # Build message
        message = f"""🤖 *AI Penetration Report - Q1 FY2027*
_As of {datetime.now().strftime('%B %d, %Y')} (vs. Q4 End Jan 31, 2026)_

*Overall Summary:*
• Total Accounts: {total_accounts:,}
• AI Penetrated: {total_ai_accounts:,} ({total_penetration}%)
• Change from Q4: +{total_change} pp

*By Leader:*
"""

        for row in data:
            change = float(row["CHANGE_PCT_POINTS"])
            change_indicator = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            message += f"""
*{row['LEADER']}*
  • Penetration: {row['PENETRATION_PCT']}% ({row['AI_PENETRATED_ACCOUNTS']:,}/{row['TOTAL_ACCOUNTS']:,} accounts)
  • Change: {change_indicator} {row['CHANGE_PCT_POINTS']} pp (was {row['Q4_PENETRATION_PCT']}%)
  • Copilot: {row['COPILOT_ACCOUNTS']:,} | AAA: {row['AAA_ACCOUNTS']:,}"""

        message += "\n\n_Generated by Sales Strategy Reporting Agent_"

        return message


def main():
    """Standalone execution for testing"""
    import logging

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("AI PENETRATION REPORT")
    print("=" * 80)

    # Initialize and run report
    report = AIPenetrationReport()
    results = report.run(formats=['csv', 'excel', 'slack'])

    if results:
        print("\n✅ Report generated successfully!")
        print("\nGenerated files:")
        if 'csv' in results:
            print(f"  📄 CSV: {results['csv']}")
        if 'excel' in results:
            print(f"  📊 Excel: {results['excel']}")
        if 'slack' in results:
            # Copy to clipboard
            subprocess.run(['pbcopy'], input=results['slack'].encode())
            print(f"  📋 Slack: Copied to clipboard")
    else:
        print("\n❌ Report generation failed")

    print("=" * 80)


if __name__ == '__main__':
    main()
