# FY27 Sales Report - Enhancement Recommendations

**Context:** Executive audience, weekly cadence, already have bookings/pipeline/renewals

---

## 🎯 High-Impact Additions (Recommended)

### 1. Executive Summary Section (Top Priority)
**Why:** First thing leadership sees, tells the story
**Effort:** 1 hour
**Value:** High

**Add at top (before filters):**

```html
<div class="executive-summary">
    <h2>📊 This Week's Story</h2>

    <div class="insight-grid">
        <div class="insight positive">
            <span class="icon">📈</span>
            <div class="insight-content">
                <strong>Strong Performance</strong>
                <p>AMER Commercial: $3.8M closed (↑15% vs last week)</p>
            </div>
        </div>

        <div class="insight warning">
            <span class="icon">⚠️</span>
            <div class="insight-content">
                <strong>Needs Attention</strong>
                <p>EMEA Q2 renewals: 23 accounts, $8.2M at risk</p>
            </div>
        </div>

        <div class="insight neutral">
            <span class="icon">📅</span>
            <div class="insight-content">
                <strong>Context</strong>
                <p>Q1 closes in 4 weeks (Apr 30, 2026)</p>
            </div>
        </div>
    </div>
</div>
```

**SQL to generate insights:**
```sql
-- Identify top performer (for "Strong Performance")
SELECT
    region,
    segment,
    total_fy27_q1_arr,
    -- Compare to last week's snapshot
    LAG(total_fy27_q1_arr) OVER (PARTITION BY region, segment ORDER BY snapshot_date) as last_week
FROM bookings_history
WHERE snapshot_date IN (CURRENT_DATE(), CURRENT_DATE() - 7)
ORDER BY (total_fy27_q1_arr - last_week) DESC
LIMIT 1;

-- Identify risk areas (for "Needs Attention")
SELECT
    region,
    COUNT(*) as accounts,
    SUM(arr) as total_arr
FROM renewal_accounts
WHERE quarter = 'Q2'
    AND region = 'EMEA'  -- Or identify programmatically
GROUP BY region;
```

---

### 2. Week-over-Week Trends (High Priority)
**Why:** Executives care about momentum
**Effort:** 2-3 hours
**Value:** High

**Add to metric cards:**

```html
<div class="metric-card purple">
    <div class="metric-label">Closed Bookings FY27 Q1</div>
    <div class="metric-value" id="totalBookings">$48.5M</div>
    <div class="metric-change positive">↑ $2.3M vs last week (+5%)</div>
    <div class="metric-subtitle">Feb - Apr 2026</div>
</div>
```

**Implementation:**
1. Store last week's metrics in a CSV: `data/weekly_snapshots.csv`
2. Python script calculates deltas
3. Add to metric cards

**SQL pattern:**
```sql
-- Store weekly snapshots
CREATE TABLE IF NOT EXISTS weekly_snapshots (
    snapshot_date DATE,
    metric_name VARCHAR,
    metric_value DECIMAL
);

-- Compare this week to last week
WITH this_week AS (
    SELECT SUM(total_arr) as bookings
    FROM closed_bookings
    WHERE snapshot_date = CURRENT_DATE()
),
last_week AS (
    SELECT SUM(total_arr) as bookings
    FROM closed_bookings
    WHERE snapshot_date = CURRENT_DATE() - 7
)
SELECT
    this_week.bookings as current,
    last_week.bookings as previous,
    this_week.bookings - last_week.bookings as delta,
    ROUND(100.0 * (this_week.bookings - last_week.bookings) / last_week.bookings, 1) as pct_change
FROM this_week, last_week;
```

---

### 3. Win Rate & Conversion Metrics (Medium Priority)
**Why:** Shows sales effectiveness
**Effort:** 2 hours
**Value:** Medium-High

**Add new metric card:**

```html
<div class="metric-card green">
    <div class="metric-label">Q1 Win Rate</div>
    <div class="metric-value">68%</div>
    <div class="metric-subtitle">142 won / 209 closed opps</div>
</div>
```

**SQL:**
```sql
-- Win rate for closed opportunities in Q1
WITH q1_closed AS (
    SELECT
        OPPORTUNITY_STATUS,
        COUNT(*) as opp_count,
        SUM(PRODUCT_BOOKING_ARR_USD) as arr
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    WHERE CLOSEDATE BETWEEN '2026-02-01' AND '2026-04-30'
        AND DATE_LABEL = 'today'
        AND opportunity_is_commissionable = TRUE
        AND stage_2_plus_date_c IS NOT NULL
        AND OPPORTUNITY_TYPE IN ('Expansion', 'New Business')
        AND PRODUCT = 'Total Booking'
        AND OPPORTUNITY_STATUS IN ('Closed', 'Lost')
    GROUP BY OPPORTUNITY_STATUS
)
SELECT
    SUM(CASE WHEN OPPORTUNITY_STATUS = 'Closed' THEN opp_count ELSE 0 END) as won_count,
    SUM(CASE WHEN OPPORTUNITY_STATUS = 'Lost' THEN opp_count ELSE 0 END) as lost_count,
    SUM(opp_count) as total_closed,
    ROUND(100.0 * SUM(CASE WHEN OPPORTUNITY_STATUS = 'Closed' THEN opp_count ELSE 0 END) / SUM(opp_count), 1) as win_rate_pct
FROM q1_closed;
```

---

### 4. AI Penetration Overview (Medium Priority)
**Why:** AI is strategic priority, you already have this data
**Effort:** 1 hour (reuse existing queries)
**Value:** Medium

**Add new section after metrics:**

```html
<div class="section">
    <h2 class="section-title">AI Product Penetration</h2>
    <div class="ai-metrics">
        <div class="ai-stat">
            <div class="ai-stat-value">34.2%</div>
            <div class="ai-stat-label">Overall AI Adoption</div>
            <div class="ai-stat-detail">2,103 of 6,157 accounts</div>
        </div>
        <div class="ai-stat">
            <div class="ai-stat-value">37.0%</div>
            <div class="ai-stat-label">AMER (Leading)</div>
        </div>
        <div class="ai-stat">
            <div class="ai-stat-value">31.1%</div>
            <div class="ai-stat-label">Digital (Lowest)</div>
        </div>
    </div>
</div>
```

**Reuse:** You already have `queries/ai_penetration/*.sql` - adapt for summary

---

### 5. Top Competitive Wins (Low-Medium Priority)
**Why:** Shows market positioning, morale booster
**Effort:** 1-2 hours
**Value:** Medium

**Add section:**

```html
<div class="section">
    <h2 class="section-title">🏆 Notable Wins This Week</h2>
    <div class="wins-grid">
        <div class="win-card">
            <div class="win-account">Acme Corporation</div>
            <div class="win-details">
                <span class="win-arr">$2.5M ARR</span>
                <span class="win-competitor">vs. Ada</span>
            </div>
            <div class="win-product">AI Agents Advanced</div>
        </div>
        <!-- Repeat for top 3-5 wins -->
    </div>
</div>
```

**SQL (reuse competitive queries):**
```sql
-- Top 5 competitive wins this week
SELECT
    p.CRM_ACCOUNT_NAME,
    p.PRODUCT_BOOKING_ARR_USD as arr,
    opp.primary_competitor_new_c as competitor,
    p.CLOSEDATE
FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings p
LEFT JOIN cleansed.salesforce.salesforce_opportunity_bcv opp
    ON p.CRM_OPPORTUNITY_ID = opp.ID
WHERE p.OPPORTUNITY_STATUS = 'Closed'
    AND p.DATE_LABEL = 'today'
    AND p.CLOSEDATE >= CURRENT_DATE() - 7  -- This week
    AND p.PRODUCT IN ('Ultimate', 'Ultimate_AR')
    AND opp.primary_competitor_new_c IS NOT NULL
ORDER BY p.PRODUCT_BOOKING_ARR_USD DESC
LIMIT 5;
```

---

### 6. Pipeline Health Indicators (Medium Priority)
**Why:** Forward-looking metrics executives care about
**Effort:** 2 hours
**Value:** Medium-High

**Add new metrics:**

```html
<div class="health-indicators">
    <div class="indicator">
        <span class="indicator-label">Pipeline Coverage (Q1)</span>
        <span class="indicator-value good">2.8x</span>
        <span class="indicator-note">Target: 2.5x</span>
    </div>
    <div class="indicator">
        <span class="indicator-label">Avg Days in Pipeline</span>
        <span class="indicator-value">45 days</span>
        <span class="indicator-note">↓ 5 days vs last month</span>
    </div>
</div>
```

**SQL:**
```sql
-- Pipeline coverage: Open pipeline / Target for period
WITH q1_target AS (
    SELECT 50000000 as target_arr  -- $50M target
),
q1_pipeline AS (
    SELECT SUM(PRODUCT_ARR_USD) as pipeline
    FROM gtmsi_consolidated_pipeline_bookings
    WHERE OPPORTUNITY_STATUS = 'Open'
        AND CLOSEDATE BETWEEN '2026-02-01' AND '2026-04-30'
        AND PRODUCT = 'Total Booking'
)
SELECT
    ROUND(q1_pipeline.pipeline / q1_target.target_arr, 1) as coverage_ratio
FROM q1_pipeline, q1_target;

-- Average days in pipeline
SELECT
    AVG(DATEDIFF(day, stage_2_plus_date_c, CURRENT_DATE())) as avg_days
FROM gtmsi_consolidated_pipeline_bookings
WHERE OPPORTUNITY_STATUS = 'Open'
    AND stage_2_plus_date_c IS NOT NULL;
```

---

### 7. At-Risk Accounts Section (Low Priority)
**Why:** Proactive risk management
**Effort:** 2 hours
**Value:** Medium (if you have health data)

**Add section:**

```html
<div class="section">
    <h2 class="section-title">⚠️ Accounts Needing Attention</h2>
    <table class="risk-table">
        <thead>
            <tr>
                <th>Account</th>
                <th>ARR</th>
                <th>Risk Type</th>
                <th>Renewal Date</th>
                <th>Owner</th>
            </tr>
        </thead>
        <tbody id="riskTableBody"></tbody>
    </table>
</div>
```

**SQL:**
```sql
-- High-value accounts with health issues and upcoming renewals
SELECT
    c.CRM_ACCOUNT_NAME,
    c.CRM_NET_ARR_USD as arr,
    h.crm_health_status as health,
    h.crm_health_risk_type as risk_type,
    c.CRM_NEXT_RENEWAL_DATE as renewal_date,
    c.CRM_RENEWAL_OWNER_NAME as owner
FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD c
LEFT JOIN FOUNDATIONAL.CUSTOMER.DIM_CRM_ACCOUNTS_DAILY_SNAPSHOT_BCV h
    ON c.CRM_ACCOUNT_ID = h.crm_account_id
WHERE c.SERVICE_DATE = (SELECT MAX(SERVICE_DATE) FROM CUSTOMER_SUCCESS__CS_RESET_DASHBOARD)
    AND c.AS_OF_DATE = 'Quarterly'
    AND c.CRM_NET_ARR_USD > 100000  -- High value only
    AND h.crm_health_status IN ('Red', 'Yellow')
    AND c.CRM_NEXT_RENEWAL_DATE BETWEEN CURRENT_DATE() AND CURRENT_DATE() + 90
ORDER BY c.CRM_NET_ARR_USD DESC
LIMIT 10;
```

---

### 8. Mini Sparkline Trends (Low Priority, Visual Polish)
**Why:** Visual trend indicators
**Effort:** 3 hours
**Value:** Low (nice-to-have)

**Add to metric cards:**

```html
<div class="metric-card">
    <div class="metric-value">$48.5M</div>
    <canvas id="bookingsTrend" class="mini-chart"></canvas>
</div>
```

**Use Chart.js with last 4-8 weeks of data**

---

## 🎯 Prioritized Roadmap

### Phase 1: Quick Wins (This Week - 4 hours)
1. **Executive Summary** (1 hr)
   - 3 insight boxes at top
   - Manually curated for now

2. **Week-over-Week Deltas** (2 hrs)
   - Add to metric cards
   - Store weekly snapshots

3. **AI Penetration Summary** (1 hr)
   - Reuse existing queries
   - Add 3-stat overview

**Why first:** High impact, low effort, uses existing data

---

### Phase 2: Standard Metrics (Next Week - 4 hours)
4. **Win Rate Metric** (2 hrs)
   - New metric card
   - Query closed vs lost opps

5. **Pipeline Health** (2 hrs)
   - Coverage ratio
   - Average days in pipeline

**Why next:** Important KPIs executives expect

---

### Phase 3: Competitive Intelligence (Week 3 - 2 hours)
6. **Top Wins Section** (2 hrs)
   - Notable wins this week
   - Competitive displacement

**Why later:** Nice-to-have, requires more data wrangling

---

### Phase 4: Risk Management (If Needed - 2 hours)
7. **At-Risk Accounts** (2 hrs)
   - Only if health data is reliable
   - High-value accounts with issues

**Why last:** Depends on data quality

---

## 📊 Recommended Layout (New Structure)

```
┌─────────────────────────────────────┐
│ Header                               │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ 📊 Executive Summary (NEW)          │
│ ├─ Strong Performance                │
│ ├─ Needs Attention                   │
│ └─ Context                           │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Filters (Region/Segment)             │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Metrics (4 cards now)                │
│ ├─ Closed Bookings (+ WoW Δ) (NEW)  │
│ ├─ Total Pipeline (+ WoW Δ) (NEW)   │
│ ├─ Q1 Pipeline                       │
│ └─ Win Rate (NEW)                    │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ 🤖 AI Penetration Overview (NEW)    │
│ ├─ Overall: 34.2%                    │
│ ├─ Top: AMER 37%                     │
│ └─ Bottom: Digital 31%               │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Closed Bookings (existing)           │
│ ├─ Table                             │
│ └─ Chart                             │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Open Pipeline (existing)             │
│ ├─ Table                             │
│ └─ Chart                             │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ 🏆 Notable Wins This Week (NEW)     │
│ ├─ Top 3-5 competitive wins          │
│ └─ Customer names + ARR + competitor │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Renewal Accounts (existing)          │
│ └─ Top 5 by region × segment         │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Footer                               │
└─────────────────────────────────────┘
```

---

## 🚀 Implementation Guide

### Step 1: Executive Summary (Start Here)

**Create:** `queries/sales_report/executive_summary.sql`

```sql
-- Generate insights for executive summary
-- Run manually or automate

-- 1. Top performer (Strong Performance)
WITH week_comparison AS (
    SELECT
        region,
        segment,
        SUM(total_fy27_q1_arr) as current_week,
        -- Compare to stored snapshot
        LAG(SUM(total_fy27_q1_arr)) OVER (PARTITION BY region, segment ORDER BY snapshot_date) as last_week
    FROM bookings_by_week
    WHERE snapshot_date >= CURRENT_DATE() - 7
    GROUP BY region, segment, snapshot_date
)
SELECT
    region,
    segment,
    current_week,
    last_week,
    current_week - last_week as delta,
    ROUND(100.0 * (current_week - last_week) / last_week, 1) as pct_change
FROM week_comparison
WHERE last_week IS NOT NULL
ORDER BY delta DESC
LIMIT 1;

-- 2. Risk areas (Needs Attention)
-- Identify region/segment with most Q2 renewals
SELECT
    region,
    COUNT(*) as renewal_count,
    ROUND(SUM(arr)/1000000, 1) as total_arr_millions
FROM renewal_accounts
WHERE quarter = 'Q2'
GROUP BY region
ORDER BY total_arr_millions DESC
LIMIT 1;

-- 3. Context (Timeline)
SELECT
    DATEDIFF(day, CURRENT_DATE(), '2026-04-30') as days_until_q1_close;
```

**Add to Python script:**
```python
# In generate_report_data.py

# Read executive insights (manually curated for now)
executive_insights = {
    'strong': {
        'title': 'AMER Commercial',
        'metric': '$3.8M closed',
        'change': '↑15% vs last week'
    },
    'attention': {
        'title': 'EMEA Q2 renewals',
        'metric': '23 accounts',
        'detail': '$8.2M at risk'
    },
    'context': {
        'title': 'Q1 closes in 4 weeks',
        'date': 'Apr 30, 2026'
    }
}

# Add to JavaScript
js_content = f"""
const executiveInsights = {json.dumps(executive_insights, indent=2)};
...
"""
```

---

### Step 2: Week-over-Week Tracking

**Create:** `data/weekly_snapshots.csv`

```csv
snapshot_date,metric_name,metric_value
2026-03-23,closed_bookings_q1,46200000
2026-03-23,total_pipeline_fy27,423000000
2026-03-30,closed_bookings_q1,48500000
2026-03-30,total_pipeline_fy27,425300000
```

**Python function:**
```python
def calculate_wow_change(current, previous):
    """Calculate week-over-week change"""
    delta = current - previous
    pct_change = (delta / previous * 100) if previous > 0 else 0

    return {
        'delta': delta,
        'pct_change': round(pct_change, 1),
        'direction': 'up' if delta > 0 else 'down',
        'formatted': f"↑ {format_currency(delta)} vs last week (+{pct_change:.1f}%)" if delta > 0
                     else f"↓ {format_currency(abs(delta))} vs last week ({pct_change:.1f}%)"
    }

# Load snapshots
snapshots = pd.read_csv('data/weekly_snapshots.csv')
last_week = snapshots[snapshots['snapshot_date'] == last_week_date]
this_week = snapshots[snapshots['snapshot_date'] == current_date]

# Calculate changes
bookings_change = calculate_wow_change(
    this_week['closed_bookings_q1'],
    last_week['closed_bookings_q1']
)
```

---

### Step 3: Win Rate Metric

**Add to:** `queries/sales_report/win_rate.sql`

```sql
-- Win rate for Q1
WITH closed_opps AS (
    SELECT
        CASE WHEN OPPORTUNITY_STATUS = 'Closed' THEN 1 ELSE 0 END as is_won,
        CASE WHEN OPPORTUNITY_STATUS = 'Lost' THEN 1 ELSE 0 END as is_lost
    FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
    WHERE CLOSEDATE BETWEEN '2026-02-01' AND '2026-04-30'
        AND DATE_LABEL = 'today'
        AND opportunity_is_commissionable = TRUE
        AND stage_2_plus_date_c IS NOT NULL
        AND OPPORTUNITY_TYPE IN ('Expansion', 'New Business')
        AND PRODUCT = 'Total Booking'
        AND OPPORTUNITY_STATUS IN ('Closed', 'Lost')
)
SELECT
    SUM(is_won) as won_count,
    SUM(is_lost) as lost_count,
    SUM(is_won) + SUM(is_lost) as total_count,
    ROUND(100.0 * SUM(is_won) / (SUM(is_won) + SUM(is_lost)), 1) as win_rate_pct
FROM closed_opps;
```

---

## ⚠️ Things NOT to Add

**Don't add these (too much for executives):**

1. ❌ **Detailed dashboards** - Keep it simple
2. ❌ **100+ charts** - 5-8 charts max
3. ❌ **Raw data dumps** - Summarize, don't show everything
4. ❌ **Complex filters** - Region/Segment is enough
5. ❌ **Drill-downs to opportunity level** - Keep aggregated
6. ❌ **Historical time series** - Just WoW is enough
7. ❌ **Statistical analysis** - No regression, forecasting
8. ❌ **Multiple tabs** - Single scrolling page

**Remember:** Executives want answers, not tools.

---

## 🎨 Visual Design Suggestions

### Color Coding for Insights

```css
.insight.positive {
    border-left: 4px solid #145F55;  /* Teal - good news */
}

.insight.warning {
    border-left: 4px solid #FFA179;  /* Peach - attention needed */
}

.insight.neutral {
    border-left: 4px solid #6440E0;  /* Boba blue - informational */
}

.metric-change.positive {
    color: #145F55;  /* Green up arrow */
}

.metric-change.negative {
    color: #FFA179;  /* Red down arrow */
}
```

### Icons to Use

```
📈 Growth/increase
📉 Decline/decrease
⚠️ Warning/attention needed
✅ Good/on track
❌ Bad/off track
🏆 Win/achievement
🎯 Target/goal
📊 Data/analytics
🤖 AI/automation
💰 Revenue/money
📅 Timeline/date
🔔 Alert/notification
```

---

## 📝 Sample Commentary Box

Add at top of executive summary:

```html
<div class="commentary-box">
    <strong>This Week's Context:</strong>
    Spring Summit (Mar 25-27) drove spike in AMER bookings.
    EMEA had bank holiday week (lower activity expected).
    Q1 closes April 30 - 4 weeks remaining.
</div>
```

**Update this manually each week** - adds human touch.

---

## 🔄 Automation Suggestions

### Weekly Snapshot Script

**Create:** `scripts/save_weekly_snapshot.sh`

```bash
#!/bin/bash
# Save this week's metrics for WoW comparison

SNAPSHOT_DATE=$(date +%Y-%m-%d)

# Query current metrics
BOOKINGS=$(snow sql -q "SELECT SUM(total_arr) FROM bookings" --format=csv | tail -1)
PIPELINE=$(snow sql -q "SELECT SUM(pipeline_arr) FROM pipeline" --format=csv | tail -1)

# Append to snapshots file
echo "$SNAPSHOT_DATE,closed_bookings_q1,$BOOKINGS" >> data/weekly_snapshots.csv
echo "$SNAPSHOT_DATE,total_pipeline_fy27,$PIPELINE" >> data/weekly_snapshots.csv

echo "✅ Snapshot saved for $SNAPSHOT_DATE"
```

**Run:** Every Monday before generating report

---

## 🎯 My Top 3 Recommendations

**If you only add 3 things, add these:**

### 1. Executive Summary (Highest Impact)
- 3 insight boxes at top
- Tells the story in 10 seconds
- Manually curate for now (automate later)

### 2. Week-over-Week Deltas (Easy + Valuable)
- Add ↑/↓ to metric cards
- Shows momentum
- Relatively easy to implement

### 3. AI Penetration Summary (Strategic + Reuses Work)
- 3-stat overview section
- You already have queries for this
- Shows progress on strategic initiative

**These 3 additions = 4 hours work, huge value for executives**

---

## 📚 Resources

All SQL queries mentioned:
- `queries/sales_report/executive_summary.sql` (NEW)
- `queries/sales_report/win_rate.sql` (NEW)
- `queries/sales_report/competitive_wins.sql` (NEW)
- Reuse existing: `queries/ai_penetration/*.sql`

Documentation:
- Implementation details: Above
- Design guidelines: Visual section
- Automation: Snapshot script

---

**Start with Phase 1 (Executive Summary + WoW Deltas + AI Overview). Get feedback from leadership. Then decide what to add next based on what they ask for.**

Don't add everything at once - iterate based on real feedback!
