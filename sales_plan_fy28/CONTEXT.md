# FY28 Sales Planning - Agent Context

## Overview
This directory contains AI agents and tools to support Zendesk's FY28 sales planning process. These agents leverage historical Snowflake data to provide data-driven insights for strategic planning.

---

## Directory Structure

### `/industries`
Industry-specific analysis and planning tools for FY28.

**Key Analysis**: Industry x Region performance metrics for New Business opportunities (last 12 months)
- **Metrics Tracked**: Pipeline created, bookings, win rates, deal cycles, inbound demand %
- **Query**: `industry_region_summary.sql`
- **Output**: `data/industry_region_summary.csv`
- **Documentation**: `INDUSTRY_ANALYSIS.md` (analysis framework, metrics definitions, usage examples)

**Use Cases**:
- Identify high-performing industries for FY28 investment
- Understand regional variations in industry performance
- Analyze sales effectiveness (win rates) by vertical
- Evaluate sales velocity (deal cycles) across industries
- Assess inbound demand strength vs. outbound prospecting

**`/industries/data`**: Raw data exports and analysis results for industry-level metrics
