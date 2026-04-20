# Interactive FY27 Sales Report - Documentation

**Version:** 1.0
**Last Updated:** 2026-03-30
**Maintainer:** Dioney Blanco

---

## Overview

This interactive HTML report provides real-time sales performance data for FY27 with:
- Closed bookings by region/segment (Feb-Apr 2026)
- Open pipeline by quarter (Q1-Q4)
- Top 5 renewal accounts by region × segment (Q1/Q2)
- Bullseye P1/P2 recommendations (AI Agents, Copilot, Seat Upgrade, ES)

**Key Features:**
- ✅ Interactive checkboxes for region/segment filtering
- ✅ Dynamic charts (Chart.js)
- ✅ Self-contained single HTML file (no dependencies)
- ✅ Clickable Salesforce account links
- ✅ Data refresh date display

---

## File Structure

```
outputs/
├── fy27_sales_report_standalone.html  # Self-contained report (share this)
├── fy27_sales_report_interactive.html # HTML template (references external JS)
├── report-data.js                     # Data file (external reference)
└── generate_report_data.py            # Python script to generate JS from CSV
```

---

## Data Sources

### 1. Closed Bookings (FY27 Q1)
**Table:** `functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings`

**Filters:**
```sql
WHERE OPPORTUNITY_STATUS = 'Closed'
  AND DATE_LABEL = 'today'
  AND opportunity_is_commissionable = TRUE
  AND stage_2_plus_date_c IS NOT NULL
  AND OPPORTUNITY_TYPE IN ('Expansion', 'New Business')
  AND PRODUCT = 'Total Booking'
  AND CLOSEDATE BETWEEN '2026-02-01' AND '2026-04-30'
  AND PRODUCT_BOOKING_ARR_USD > 0
```

**Aggregation:** Sum by region/segment for Feb, Mar, and total Q1

---

### 2. Open Pipeline (FY27 by Quarter)
**Table:** `functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings`

**Filters:**
```sql
WHERE OPPORTUNITY_STATUS = 'Open'
  AND DATE_LABEL = 'today'
  AND opportunity_is_commissionable = TRUE
  AND stage_2_plus_date_c IS NOT NULL
  AND OPPORTUNITY_TYPE IN ('Expansion', 'New Business')
  AND PRODUCT = 'Total Booking'
  AND PRODUCT_ARR_USD > 0
  AND CLOSEDATE BETWEEN '2026-02-01' AND '2027-01-31'
```

**Quarter Calculation:**
```sql
CASE
  WHEN CLOSEDATE BETWEEN '2026-02-01' AND '2026-04-30' THEN 'Q1'
  WHEN CLOSEDATE BETWEEN '2026-05-01' AND '2026-07-31' THEN 'Q2'
  WHEN CLOSEDATE BETWEEN '2026-08-01' AND '2026-10-31' THEN 'Q3'
  WHEN CLOSEDATE BETWEEN '2026-11-01' AND '2027-01-31' THEN 'Q4'
END
```

**Aggregation:** Sum by region/segment/quarter

---

### 3. Renewal Accounts (Top 5 per Region × Segment)
**Base Table:** `PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD`

**Filters:**
```sql
WHERE SERVICE_DATE = (SELECT MAX(SERVICE_DATE) FROM CUSTOMER_SUCCESS__CS_RESET_DASHBOARD)
  AND AS_OF_DATE = 'Quarterly'
  AND CRM_NET_ARR_USD > 0
  AND CRM_NEXT_RENEWAL_DATE BETWEEN '2026-02-01' AND '2026-07-31'
  AND CRM_ACCOUNT_ID NOT IN (
    SELECT DISTINCT CRM_ACCOUNT_ID
    FROM gtmsi_consolidated_pipeline_bookings
    WHERE OPPORTUNITY_STATUS = 'Open' AND DATE_LABEL = 'today'
  )
```

**Ranking:**
```sql
ROW_NUMBER() OVER (PARTITION BY region, segment ORDER BY arr DESC) as rank
WHERE rank <= 5
```

---

### 4. Bullseye Recommendations
**Table:** `PRESENTATION.BULLSEYE_PRO.CUSTOMERS`

**Recommendation Types:**
- `AI_AGENTS_ADVANCED` - AI Agents Advanced recommendation
- `COPILOT` - Copilot recommendation
- `SEAT_CHANGE` - Seat upgrade recommendation
- `ES` - Employee Service recommendation

**Logic:**
```sql
MAX(CASE
  WHEN (rec_1_priority IN (1, 2) AND rec_1_type = 'AI_AGENTS_ADVANCED')
    OR (rec_2_priority IN (1, 2) AND rec_2_type = 'AI_AGENTS_ADVANCED')
    OR (rec_3_priority IN (1, 2) AND rec_3_type = 'AI_AGENTS_ADVANCED')
  THEN 1 ELSE 0
END) as has_ai_agents_rec
```

Checks all 3 recommendation slots (rec_1, rec_2, rec_3) for Priority 1 or 2

---

## How to Regenerate the Report

### Quick Regeneration (Existing Script)

```bash
cd /Users/dioney.blanco/Zendesk-agent

# 1. Query data and generate JS
bash << 'EOF'
date +%s.%N > /tmp/claude_query_start_time

# Get latest snapshot date
LATEST_DATE=$(snow sql -q "SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD" --format=csv | tail -1)
echo "$LATEST_DATE" > /tmp/data_refresh_date.txt

# Query bookings
snow sql -q "..." --format=csv > /tmp/bookings_data.csv

# Query pipeline
snow sql -q "..." --format=csv > /tmp/pipeline_data.csv

# Query renewals
snow sql -q "..." --format=csv > /tmp/renewal_data.csv

# Generate JS from CSV
python3 outputs/generate_report_data.py

# Create self-contained HTML
python3 << 'PYTHON'
with open('outputs/fy27_sales_report_interactive.html', 'r') as f:
    html = f.read()
with open('outputs/report-data.js', 'r') as f:
    js = f.read()
html = html.replace('<script src="report-data.js"></script>', f'<script>\n{js}\n</script>')
with open('outputs/fy27_sales_report_standalone.html', 'w') as f:
    f.write(html)
PYTHON

# Cleanup
rm /tmp/*.csv /tmp/data_refresh_date.txt
EOF

# 2. Open the report
open outputs/fy27_sales_report_standalone.html
```

---

## Report Architecture

### HTML Structure

```
┌─────────────────────────────────────┐
│ Header (Purple - Brand Color)       │
│ - Title: FY27 Sales Performance     │
│ - Subtitle: Date range               │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Filters (Yellow - Brand Color)       │
│ - Region checkboxes                  │
│ - Segment checkboxes                 │
│ - Select All / Unselect All buttons │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Metrics Cards (3 columns)            │
│ - Closed Bookings (Purple)           │
│   └─ Data refresh date shown here   │
│ - Total Pipeline (Teal)              │
│ - Q1 Pipeline Remaining (Orange)    │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Closed Bookings Table + Chart        │
│ - Table: Region/Segment/Feb/Mar/Q1  │
│ - Chart: Stacked bar by region      │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Open Pipeline Table + Chart          │
│ - Table: Region/Segment/Q1-Q4/Total │
│ - Chart: Bar by quarter              │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Renewal Accounts Table               │
│ - Top 5 per region × segment        │
│ - Columns: Account, AE, ARR, Date,  │
│   Bullseye recommendations           │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Footer                               │
│ - Generation date                    │
│ - Data source info                   │
└─────────────────────────────────────┘
```

### JavaScript Data Flow

```
1. Page Load
   ├─> initCheckboxes()
   │   ├─> Create region checkboxes
   │   ├─> Create segment checkboxes
   │   └─> Set data refresh date
   └─> filterData()

2. User Changes Filter
   └─> filterData()
       ├─> getSelectedRegions()
       ├─> getSelectedSegments()
       ├─> Filter bookingsData
       ├─> Filter pipelineData
       ├─> Filter renewalData
       ├─> updateMetrics()
       ├─> updateBookingsTable()
       ├─> updatePipelineTable()
       ├─> updateRenewalTable()
       ├─> updateBookingsChart()
       └─> updatePipelineChart()
```

---

## Adding New Features

### Example 1: Add a New Metric Card

**Step 1:** Add HTML element
```html
<div class="metric-card blue">
    <div class="metric-label">New Metric</div>
    <div class="metric-value" id="newMetric">$0.00M</div>
    <div class="metric-subtitle">Description</div>
</div>
```

**Step 2:** Update CSS grid
```css
.metrics-grid {
    grid-template-columns: repeat(4, 1fr); /* Changed from 3 to 4 */
}
```

**Step 3:** Update JavaScript
```javascript
function updateMetrics(filteredBookings, filteredPipeline, filteredRenewals) {
    // ... existing metrics ...

    const newMetricValue = calculateNewMetric(filteredBookings);
    document.getElementById('newMetric').textContent = formatCurrency(newMetricValue);
}
```

---

### Example 2: Add a New Column to Renewal Table

**Step 1:** Query additional data in Snowflake
```sql
-- Add new column to SELECT
SELECT
  CRM_ACCOUNT_ID,
  CRM_ACCOUNT_NAME,
  NEW_COLUMN,  -- Add here
  ...
```

**Step 2:** Update Python data parsing
```python
renewals.append({
    'account_id': row['CRM_ACCOUNT_ID'],
    'new_column': row['NEW_COLUMN'],  # Add here
    ...
})
```

**Step 3:** Add table header
```html
<th>New Column</th>
```

**Step 4:** Add table cell in JavaScript
```javascript
tr.innerHTML = `
    <td>${row.region}</td>
    <td>${row.new_column}</td>  <!-- Add here -->
    ...
`;
```

---

### Example 3: Add a New Bullseye Recommendation

**Step 1:** Update SQL query
```sql
bullseye_recommendations AS (
  SELECT
    crm_account_id,
    -- ... existing recommendations ...
    MAX(CASE
      WHEN (rec_1_priority IN (1, 2) AND rec_1_type = 'NEW_PRODUCT')
        OR (rec_2_priority IN (1, 2) AND rec_2_type = 'NEW_PRODUCT')
        OR (rec_3_priority IN (1, 2) AND rec_3_type = 'NEW_PRODUCT')
      THEN 1 ELSE 0
    END) as has_new_product_rec
  FROM PRESENTATION.BULLSEYE_PRO.CUSTOMERS
  GROUP BY crm_account_id
)
```

**Step 2:** Update Python parsing
```python
'has_new_product_rec': int(row['HAS_NEW_PRODUCT_REC'])
```

**Step 3:** Add table column
```html
<th>New Product</th>
```

**Step 4:** Update JavaScript table rendering
```javascript
<td>${row.has_new_product_rec ? '✅' : ''}</td>
```

---

## Suggestions for Easier Maintenance

### 1. Create a Makefile Target

Add to your project's Makefile:

```makefile
.PHONY: sales-report
sales-report: ## Generate interactive FY27 sales report
	@echo "🔄 Generating interactive sales report..."
	@./scripts/generate_sales_report.sh
	@echo "✅ Report generated: outputs/fy27_sales_report_standalone.html"
	@open outputs/fy27_sales_report_standalone.html
```

Then run: `make sales-report`

---

### 2. Create a Standalone Script

Create `scripts/generate_sales_report.sh`:

```bash
#!/bin/bash
# Generate FY27 Interactive Sales Report
# Usage: ./scripts/generate_sales_report.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

echo "📊 Generating FY27 Sales Report..."

# 1. Get latest snapshot date
LATEST_DATE=$(snow sql -q "SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD" --format=csv | tail -1)
echo "   Latest data: $LATEST_DATE"
echo "$LATEST_DATE" > /tmp/data_refresh_date.txt

# 2. Query all data
echo "   Querying bookings..."
snow sql -f queries/sales_report/bookings.sql --format=csv > /tmp/bookings_data.csv

echo "   Querying pipeline..."
snow sql -f queries/sales_report/pipeline.sql --format=csv > /tmp/pipeline_data.csv

echo "   Querying renewals..."
snow sql -f queries/sales_report/renewals.sql --format=csv > /tmp/renewal_data.csv

# 3. Generate JavaScript
echo "   Generating JavaScript..."
python3 outputs/generate_report_data.py

# 4. Create self-contained HTML
echo "   Creating self-contained HTML..."
python3 scripts/embed_report_js.py

# 5. Cleanup
rm /tmp/bookings_data.csv /tmp/pipeline_data.csv /tmp/renewal_data.csv /tmp/data_refresh_date.txt

echo "✅ Report ready: outputs/fy27_sales_report_standalone.html"
```

---

### 3. Modularize SQL Queries

Create separate SQL files:

```
queries/sales_report/
├── bookings.sql        # Closed bookings query
├── pipeline.sql        # Open pipeline query
└── renewals.sql        # Renewal accounts query
```

**Benefits:**
- Version control for queries
- Easier to test individually
- Can be run with `snow sql -f <file>`

---

### 4. Use a Templating System (Advanced)

Convert to Jinja2 templates for easier maintenance:

```
templates/
├── base.html           # Base HTML structure
├── metrics.html        # Metric cards template
├── tables.html         # Table templates
└── charts.html         # Chart configurations
```

**Pros:**
- Separate HTML from data logic
- Reusable components
- Easier to add new sections

**Cons:**
- Adds dependency (Jinja2)
- More complex build process

---

### 5. Add Configuration File

Create `config/sales_report.yaml`:

```yaml
# FY27 Sales Report Configuration

report:
  title: "FY27 Sales Performance"
  fiscal_year:
    start: "2026-02-01"
    end: "2027-01-31"
  quarters:
    Q1: ["2026-02-01", "2026-04-30"]
    Q2: ["2026-05-01", "2026-07-31"]
    Q3: ["2026-08-01", "2026-10-31"]
    Q4: ["2026-11-01", "2027-01-31"]

data_sources:
  bookings:
    table: "functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings"
    filters:
      - "OPPORTUNITY_STATUS = 'Closed'"
      - "DATE_LABEL = 'today'"
      - "opportunity_is_commissionable = TRUE"

  pipeline:
    table: "functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings"
    filters:
      - "OPPORTUNITY_STATUS = 'Open'"

  renewals:
    table: "PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD"
    top_n: 5

bullseye:
  recommendations:
    - type: "AI_AGENTS_ADVANCED"
      label: "AI Agents"
    - type: "COPILOT"
      label: "Copilot"
    - type: "SEAT_CHANGE"
      label: "Seat Upgrade"
    - type: "ES"
      label: "ES"

styling:
  brand_colors:
    berry_purple: "#9A4497"
    eggnog_yellow: "#FFD874"
    matcha_green: "#DEF991"
    teal: "#145F55"
    peach: "#FFA179"
    boba_blue: "#6440E0"
```

---

## Recommended Approach (Best Balance)

**For your use case, I recommend:**

1. ✅ **Create Makefile target** (`make sales-report`)
   - Simple one-command regeneration
   - No additional complexity

2. ✅ **Move SQL to separate files** (`queries/sales_report/*.sql`)
   - Version control
   - Easier testing
   - Can share queries with team

3. ✅ **Keep current Python script** (`generate_report_data.py`)
   - Already works well
   - No need to overcomplicate

4. ✅ **Create shell script** (`scripts/generate_sales_report.sh`)
   - Combines all steps
   - Easy to understand and modify

**Don't need (yet):**
- ❌ Jinja2 templates (adds complexity)
- ❌ Config YAML (current approach is clear)
- ❌ Advanced build system (overkill for now)

---

## Common Modifications

### Change Date Range
Edit in `queries/sales_report/bookings.sql`:
```sql
WHERE CLOSEDATE BETWEEN '2026-02-01' AND '2026-04-30'
```

### Change Top N Accounts
Edit in `queries/sales_report/renewals.sql`:
```sql
WHERE rank <= 5  -- Change to 10, 20, etc.
```

### Add New Region
Regions auto-populate from data. Just ensure data has the new region.

### Change Brand Colors
Edit CSS in `fy27_sales_report_interactive.html`:
```css
.metric-card.purple { background: #9A4497; }
```

---

## Troubleshooting

### Report Shows Blank Data
**Cause:** JavaScript not embedded or external JS file missing
**Fix:** Always share `fy27_sales_report_standalone.html` (not the interactive version)

### Data Refresh Date Not Showing
**Cause:** Missing element ID in HTML
**Fix:** Ensure `<div id="dataRefreshDate">` exists in purple metric card

### Checkboxes Not Working
**Cause:** JavaScript function names mismatch
**Fix:** Check that HTML onclick calls match JS function names

### Wrong Data (Old Snapshot)
**Cause:** Query not using `MAX(SERVICE_DATE)`
**Fix:** Ensure all queries use:
```sql
WHERE SERVICE_DATE = (SELECT MAX(SERVICE_DATE) FROM ...)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-30 | Initial version with bookings, pipeline, renewals, Bullseye recommendations |

---

## Next Steps / Future Enhancements

**Potential features to add:**
- [ ] Year-over-year comparison section
- [ ] Win rate by product (closed-won / (closed-won + closed-lost))
- [ ] Average deal size by segment
- [ ] Sales cycle length analysis
- [ ] Forecast vs actual tracking
- [ ] Export to PDF functionality
- [ ] Email report scheduling
- [ ] Mobile-responsive design improvements

**Maintenance tasks:**
- [ ] Move SQL queries to separate files
- [ ] Create Makefile target
- [ ] Create shell script for regeneration
- [ ] Add unit tests for data transformations
- [ ] Document query performance optimization

---

## Contact

For questions or enhancements, contact:
- **Dioney Blanco** - Repository maintainer
- **Claude Code** - AI assistant for modifications

---

**Last Updated:** 2026-03-30
