#!/usr/bin/env python3
"""
Generate ES Impact Metrics Table
Builds a table similar to the format shown with:
- Pipeline QTD Created (with vs LW, vs LY, % Target)
- Open Pipeline Coverage (CQ, CQ+1, CQ+2)
- Bookings QTD Actual (with vs LW, vs LY, % Target)
"""

import subprocess
import csv
from io import StringIO

# Targets from user data
TARGETS = {
    'Expansion': {
        'pipe': 20832960,
        'bookings': 7762216
    },
    'New Business': {
        'pipe': 15052102,
        'bookings': 1477362
    }
}

def run_snowflake_query(query_file):
    """Run a Snowflake query and return results as list of dicts"""
    result = subprocess.run(
        ['snow', 'sql', '-f', query_file, '--format=csv'],
        capture_output=True,
        text=True,
        check=True
    )

    # Parse CSV output
    reader = csv.DictReader(StringIO(result.stdout))
    return list(reader)

def format_currency(value):
    """Format number as currency (M or K)"""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:,.0f}"

def format_percentage(value):
    """Format as percentage"""
    return f"{value:.0f}%"

def format_coverage(value):
    """Format as coverage multiplier"""
    return f"{value:.1f}x"

def calculate_percentage_change(current, previous):
    """Calculate percentage change"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

def main():
    print("📊 Generating ES Impact Metrics Table...")
    print()

    # Run all queries
    print("Running queries...")

    # Pipeline Created
    qtd_pipe = run_snowflake_query('queries/es_metrics/fy27q1_es_pipeline_created.sql')
    lw_pipe = run_snowflake_query('queries/es_metrics/fy27q1_es_pipeline_created_lw.sql')
    ly_pipe = run_snowflake_query('queries/es_metrics/fy26q1_es_pipeline_created_ly.sql')

    # Open Pipeline
    open_pipe = run_snowflake_query('queries/es_metrics/fy27_es_open_pipeline.sql')

    # Bookings
    qtd_bookings = run_snowflake_query('queries/es_metrics/fy27q1_es_bookings.sql')
    lw_bookings = run_snowflake_query('queries/es_metrics/fy27q1_es_bookings_lw.sql')
    ly_bookings = run_snowflake_query('queries/es_metrics/fy26q1_es_bookings_ly.sql')

    print("✅ Queries complete")
    print()

    # Convert to dicts for easy lookup
    def to_dict(data):
        return {row['METRIC']: float(row[list(row.keys())[1]]) for row in data}

    qtd_pipe_dict = to_dict(qtd_pipe)
    lw_pipe_dict = to_dict(lw_pipe)
    ly_pipe_dict = to_dict(ly_pipe)

    qtd_bookings_dict = to_dict(qtd_bookings)
    lw_bookings_dict = to_dict(lw_bookings)
    ly_bookings_dict = to_dict(ly_bookings)

    # Open pipeline by quarter and metric
    open_pipe_dict = {}
    for row in open_pipe:
        quarter = row['CLOSE_QUARTER']
        metric = row['METRIC']
        arr = float(row['OPEN_PIPELINE_ARR'])
        if metric not in open_pipe_dict:
            open_pipe_dict[metric] = {}
        open_pipe_dict[metric][quarter] = arr

    # Calculate total targets
    total_pipe_target = TARGETS['Expansion']['pipe'] + TARGETS['New Business']['pipe']
    total_bookings_target = TARGETS['Expansion']['bookings'] + TARGETS['New Business']['bookings']

    # Build the table
    print("=" * 140)
    print(f"{'Impact Metrics':<20} {'Pipeline':<50} {'Open Pipeline':<35} {'Bookings':<35}")
    print(f"{'ES':<20} {'QTD Created':<12} {'vs LW':<8} {'vs LY':<8} {'% Target':<10} "
          f"{'CQ Coverage':<12} {'CQ+1 Coverage':<12} {'CQ+2 Coverage':<12} "
          f"{'QTD Actual':<12} {'vs LW':<8} {'vs LY':<8} {'% Target':<10}")
    print("=" * 140)

    # Row 1: Total
    metric = 'Total'

    # Pipeline
    pipe_qtd = qtd_pipe_dict.get(metric, 0)
    pipe_lw = lw_pipe_dict.get(metric, 0)
    pipe_ly = ly_pipe_dict.get(metric, 0)
    pipe_vs_lw = calculate_percentage_change(pipe_qtd, pipe_lw)
    pipe_vs_ly = calculate_percentage_change(pipe_qtd, pipe_ly)
    pipe_pct_target = (pipe_qtd / total_pipe_target * 100) if total_pipe_target > 0 else 0

    # Open Pipeline Coverage
    # For total, we need to think about what makes sense for coverage
    # Coverage = Open Pipeline / Remaining Target
    # For Q1 (CQ), remaining target = total_bookings_target - qtd_bookings
    bookings_qtd = qtd_bookings_dict.get(metric, 0)
    remaining_q1_target = max(total_bookings_target - bookings_qtd, 0)
    q1_open = open_pipe_dict.get(metric, {}).get('Q1', 0)
    q2_open = open_pipe_dict.get(metric, {}).get('Q2', 0)
    q3_open = open_pipe_dict.get(metric, {}).get('Q3', 0)

    # For coverage, we'll use remaining Q1 target as denominator for CQ
    # For CQ+1 and CQ+2, we'd need Q2/Q3 targets but we don't have them
    # So let's use the same Q1 target as a proxy
    cq_coverage = (q1_open / remaining_q1_target) if remaining_q1_target > 0 else 0
    cq1_coverage = (q2_open / total_bookings_target) if total_bookings_target > 0 else 0
    cq2_coverage = (q3_open / total_bookings_target) if total_bookings_target > 0 else 0

    # Bookings
    bookings_lw = lw_bookings_dict.get(metric, 0)
    bookings_ly = ly_bookings_dict.get(metric, 0)
    bookings_vs_lw = calculate_percentage_change(bookings_qtd, bookings_lw)
    bookings_vs_ly = calculate_percentage_change(bookings_qtd, bookings_ly)
    bookings_pct_target = (bookings_qtd / total_bookings_target * 100) if total_bookings_target > 0 else 0

    print(f"{'Total ($)':<20} "
          f"{format_currency(pipe_qtd):<12} {format_percentage(pipe_vs_lw):<8} {format_percentage(pipe_vs_ly):<8} {format_percentage(pipe_pct_target):<10} "
          f"{format_coverage(cq_coverage):<12} {format_coverage(cq1_coverage):<12} {format_coverage(cq2_coverage):<12} "
          f"{format_currency(bookings_qtd):<12} {format_percentage(bookings_vs_lw):<8} {format_percentage(bookings_vs_ly):<8} {format_percentage(bookings_pct_target):<10}")

    # Row 2: New Customer (New Business)
    metric = 'New Business'

    # Pipeline
    pipe_qtd = qtd_pipe_dict.get(metric, 0)
    pipe_lw = lw_pipe_dict.get(metric, 0)
    pipe_ly = ly_pipe_dict.get(metric, 0)
    pipe_vs_lw = calculate_percentage_change(pipe_qtd, pipe_lw)
    pipe_vs_ly = calculate_percentage_change(pipe_qtd, pipe_ly)
    pipe_pct_target = (pipe_qtd / TARGETS['New Business']['pipe'] * 100) if TARGETS['New Business']['pipe'] > 0 else 0

    # Open Pipeline Coverage
    bookings_qtd = qtd_bookings_dict.get(metric, 0)
    remaining_q1_target = max(TARGETS['New Business']['bookings'] - bookings_qtd, 0)
    q1_open = open_pipe_dict.get(metric, {}).get('Q1', 0)
    q2_open = open_pipe_dict.get(metric, {}).get('Q2', 0)
    q3_open = open_pipe_dict.get(metric, {}).get('Q3', 0)

    cq_coverage = (q1_open / remaining_q1_target) if remaining_q1_target > 0 else 0
    cq1_coverage = (q2_open / TARGETS['New Business']['bookings']) if TARGETS['New Business']['bookings'] > 0 else 0
    cq2_coverage = (q3_open / TARGETS['New Business']['bookings']) if TARGETS['New Business']['bookings'] > 0 else 0

    # Bookings
    bookings_lw = lw_bookings_dict.get(metric, 0)
    bookings_ly = ly_bookings_dict.get(metric, 0)
    bookings_vs_lw = calculate_percentage_change(bookings_qtd, bookings_lw)
    bookings_vs_ly = calculate_percentage_change(bookings_qtd, bookings_ly)
    bookings_pct_target = (bookings_qtd / TARGETS['New Business']['bookings'] * 100) if TARGETS['New Business']['bookings'] > 0 else 0

    print(f"{'New Customer':<20} "
          f"{format_currency(pipe_qtd):<12} {format_percentage(pipe_vs_lw):<8} {format_percentage(pipe_vs_ly):<8} {format_percentage(pipe_pct_target):<10} "
          f"{format_coverage(cq_coverage):<12} {format_coverage(cq1_coverage):<12} {format_coverage(cq2_coverage):<12} "
          f"{format_currency(bookings_qtd):<12} {format_percentage(bookings_vs_lw):<8} {format_percentage(bookings_vs_ly):<8} {format_percentage(bookings_pct_target):<10}")

    # Row 3: X-Sell / Up-Sell (Expansion)
    metric = 'X-Sell / Up-Sell'

    # Pipeline
    pipe_qtd = qtd_pipe_dict.get(metric, 0)
    pipe_lw = lw_pipe_dict.get(metric, 0)
    pipe_ly = ly_pipe_dict.get(metric, 0)
    pipe_vs_lw = calculate_percentage_change(pipe_qtd, pipe_lw)
    pipe_vs_ly = calculate_percentage_change(pipe_qtd, pipe_ly)
    pipe_pct_target = (pipe_qtd / TARGETS['Expansion']['pipe'] * 100) if TARGETS['Expansion']['pipe'] > 0 else 0

    # Open Pipeline Coverage
    bookings_qtd = qtd_bookings_dict.get(metric, 0)
    remaining_q1_target = max(TARGETS['Expansion']['bookings'] - bookings_qtd, 0)
    q1_open = open_pipe_dict.get(metric, {}).get('Q1', 0)
    q2_open = open_pipe_dict.get(metric, {}).get('Q2', 0)
    q3_open = open_pipe_dict.get(metric, {}).get('Q3', 0)

    cq_coverage = (q1_open / remaining_q1_target) if remaining_q1_target > 0 else 0
    cq1_coverage = (q2_open / TARGETS['Expansion']['bookings']) if TARGETS['Expansion']['bookings'] > 0 else 0
    cq2_coverage = (q3_open / TARGETS['Expansion']['bookings']) if TARGETS['Expansion']['bookings'] > 0 else 0

    # Bookings
    bookings_lw = lw_bookings_dict.get(metric, 0)
    bookings_ly = ly_bookings_dict.get(metric, 0)
    bookings_vs_lw = calculate_percentage_change(bookings_qtd, bookings_lw)
    bookings_vs_ly = calculate_percentage_change(bookings_qtd, bookings_ly)
    bookings_pct_target = (bookings_qtd / TARGETS['Expansion']['bookings'] * 100) if TARGETS['Expansion']['bookings'] > 0 else 0

    print(f"{'X-Sell / Up-Sell':<20} "
          f"{format_currency(pipe_qtd):<12} {format_percentage(pipe_vs_lw):<8} {format_percentage(pipe_vs_ly):<8} {format_percentage(pipe_pct_target):<10} "
          f"{format_coverage(cq_coverage):<12} {format_coverage(cq1_coverage):<12} {format_coverage(cq2_coverage):<12} "
          f"{format_currency(bookings_qtd):<12} {format_percentage(bookings_vs_lw):<8} {format_percentage(bookings_vs_ly):<8} {format_percentage(bookings_pct_target):<10}")

    print("=" * 140)
    print()
    print("✅ ES Impact Metrics Table generated successfully!")

if __name__ == '__main__':
    main()
