# Industry Analysis - New Business Performance

## Overview
This document contains analysis of New Business opportunity performance by industry and region over the last 12 months. Use this data to identify high-performing industries, understand regional variations, and inform FY28 planning decisions.

---

## Data Source
- **Query**: `industry_region_summary.sql`
- **Output**: `data/industry_region_summary.csv`
- **Time Period**: Last 12 months (opportunities with stage 2+ date in last 12 months)
- **Opportunity Type**: New Business only
- **Product**: Total Booking (consolidated view)

---

## Metrics Explained

### 1. Total Pipeline Created
- **Definition**: Sum of all ARR from opportunities that reached Stage 2+ in the last 12 months
- **Includes**: Open + Closed + Lost opportunities
- **Use Case**: Understand total opportunity generation by industry/region

### 2. Total Bookings
- **Definition**: Sum of `PRODUCT_BOOKING_ARR_USD` from closed/won deals
- **Includes**: Only closed opportunities
- **Use Case**: Actual revenue realized by industry/region

### 3. Won Deal Count
- **Definition**: Count of distinct closed/won opportunities
- **Use Case**: Volume of successful deals (combine with bookings for average deal size)

### 4. Win Rate %
- **Formula**: `Closed Deals / (Closed Deals + Lost Deals) * 100`
- **Exclusions**: Duplicate opportunities are excluded from lost count
- **Use Case**: Sales effectiveness by industry/region
- **Interpretation**:
  - >40% = Strong performance
  - 25-40% = Average performance
  - <25% = Needs improvement or competitive challenges

### 5. Average Deal Cycle (Days)
- **Formula**: Average days from `stage_2_plus_date_c` to `CLOSEDATE` for closed/lost deals
- **Minimum**: 1 day (if calculation results in 0 or negative, defaults to 1)
- **Use Case**: Sales velocity by industry/region
- **Interpretation**:
  - <90 days = Fast sales cycle
  - 90-180 days = Standard cycle
  - >180 days = Long/complex sales cycle

### 6. Inbound %
- **Formula**: `Opportunities with 'inbound' in sales_play_lead / Total Opportunities * 100`
- **Use Case**: Marketing-generated demand vs. outbound prospecting
- **Interpretation**:
  - High inbound % = Strong market pull, effective marketing
  - Low inbound % = Reliance on outbound, may need marketing investment

---

## Analysis Framework

### High-Performing Industries (Target for Growth)
Look for industries with:
- ✅ High win rates (>35%)
- ✅ Strong bookings volume
- ✅ Reasonable deal cycles (<180 days)
- ✅ Growing pipeline creation

**Planning Action**: Increase investment, add capacity, develop industry-specific playbooks

### Challenged Industries (Needs Strategy Adjustment)
Look for industries with:
- ⚠️ Low win rates (<25%)
- ⚠️ Long deal cycles (>200 days)
- ⚠️ Declining pipeline
- ⚠️ Low inbound % (outbound struggling)

**Planning Action**: Investigate root causes, consider competitive positioning, adjust GTM strategy

### Emerging Opportunities (Growth Potential)
Look for industries with:
- 🚀 High inbound % (market interest)
- 🚀 Small volume but high win rates (early success)
- 🚀 Fast deal cycles (product-market fit)

**Planning Action**: Pilot expansion, develop case studies, invest in marketing

### Regional Variations
Compare same industry across regions:
- Different win rates may indicate competitive landscape differences
- Different deal cycles may reflect buyer maturity or market dynamics
- Different inbound % may show marketing effectiveness by region

---

## Key Questions This Data Answers

### For FY28 Planning:
1. **Which industries should we prioritize?**
   - Sort by total bookings + win rate
   - Identify industries with consistent performance across regions

2. **Where are we struggling to win?**
   - Filter for low win rates (<25%)
   - Investigate competitive losses, feature gaps, or pricing issues

3. **Which industries have fastest sales cycles?**
   - Sort by avg_deal_cycle_days ascending
   - Consider these for quota allocation (faster revenue recognition)

4. **Where is inbound demand strongest?**
   - Sort by inbound_pct descending
   - Allocate marketing budget to industries with proven demand generation

5. **Regional focus areas?**
   - Compare bookings by region
   - Identify where each region over/under-performs by industry

---

## Usage Examples

### Example 1: Identify Top 3 Industries for AMER
```sql
SELECT industry, total_bookings, win_rate_pct, avg_deal_cycle_days
FROM industry_region_summary
WHERE region = 'AMER'
ORDER BY total_bookings DESC
LIMIT 3;
```

### Example 2: Find Fast-Cycle, High-Win-Rate Industries
```sql
SELECT region, industry, win_rate_pct, avg_deal_cycle_days, total_bookings
FROM industry_region_summary
WHERE win_rate_pct > 35
  AND avg_deal_cycle_days < 120
ORDER BY total_bookings DESC;
```

### Example 3: Inbound Demand Leaders
```sql
SELECT region, industry, inbound_pct, total_pipeline_created
FROM industry_region_summary
WHERE inbound_pct > 30
ORDER BY inbound_pct DESC;
```

---

## Data Quality Notes

### Exclusions Applied:
- ✅ Only commissionable opportunities
- ✅ Only opportunities with stage 2+ date (qualified pipeline)
- ✅ Duplicate lost opportunities excluded from win rate calculation
- ✅ Only positive ARR opportunities

### Known Limitations:
- Industry field can be "Unknown" if not populated in Salesforce
- Sales play lead may be NULL or inconsistently formatted
- Deal cycle excludes still-open opportunities (only closed/lost have cycle data)

---

## Next Steps for Analysis

1. **Deep Dive by Industry**: For top 5 industries, analyze:
   - Sub-industry breakdown
   - Competitive landscape (win/loss reasons)
   - GTM team performance
   - Account size distribution

2. **Regional Benchmarking**: Compare each region's performance:
   - Which industries does each region excel in?
   - Where are regional gaps vs. global average?

3. **Cohort Analysis**: Track industries over time:
   - YoY growth in pipeline creation
   - Win rate trends (improving or declining?)
   - Deal cycle evolution

4. **Segment Overlay**: Add market segment dimension:
   - Which industries perform best in Enterprise vs. Commercial?
   - SMB/Digital leader performance by industry

---

## Related Queries

- **Base Data**: `new_business_opps_last_12m.sql` (opportunity-level detail)
- **Summary**: `industry_region_summary.sql` (this analysis)
- **Output**: `data/industry_region_summary.csv`

---

## Last Updated
Generated: 2026-04-20
Data Period: Last 12 months (rolling)
