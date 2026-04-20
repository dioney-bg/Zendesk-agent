# FY27 Interactive Sales Report - Quick Start

**For the impatient:** Run `make sales-report` and you're done! 🎉

---

## 🚀 Quick Commands

### Generate the Report

```bash
make sales-report
```

This will:
1. Query latest data from Snowflake
2. Generate JavaScript data file
3. Create self-contained HTML
4. Open in your browser

**Output:** `outputs/fy27_sales_report_standalone.html`

---

### Share the Report

```bash
# Email or Slack this file to colleagues:
outputs/fy27_sales_report_standalone.html
```

**No setup needed for recipients** - just open the HTML file in a browser!

---

## 📖 What's in the Report?

### 1. Closed Bookings (Purple Card)
- FY27 Q1 total (Feb-Apr 2026)
- Shows data refresh date

### 2. Open Pipeline (Teal Card)
- Total FY27 pipeline (all quarters)

### 3. Q1 Pipeline (Orange Card)
- Pipeline closing by April 30, 2026

### 4. Interactive Filters
- ✅ Region checkboxes (AMER, EMEA, APAC, LATAM)
- ✅ Segment checkboxes (Enterprise, Strategic, Public Sector, Commercial, SMB, Digital)
- All tables and charts update dynamically

### 5. Closed Bookings Section
- Table: Region/Segment breakdown (Feb + Mar + Total)
- Chart: Stacked bar by region

### 6. Open Pipeline Section
- Table: Region/Segment by quarter (Q1, Q2, Q3, Q4)
- Chart: Bar by quarter

### 7. Renewal Accounts Section
- Top 5 accounts per region × segment
- Renewals in Q1/Q2 with no open opportunities
- Bullseye recommendations: AI Agents, Copilot, Seat Upgrade, ES
- Clickable Salesforce links

---

## 🛠️ Behind the Scenes

The report uses:
- **Snowflake queries** (`queries/sales_report/*.sql`)
- **Python data generator** (`outputs/generate_report_data.py`)
- **Shell script** (`scripts/generate_sales_report.sh`)
- **HTML template** (`outputs/fy27_sales_report_interactive.html`)

All orchestrated by `make sales-report`.

---

## ❓ FAQ

**Q: The report shows blank when I share it**
A: Make sure you're sharing `fy27_sales_report_standalone.html` (not the interactive version)

**Q: How do I update to latest data?**
A: Just run `make sales-report` again

**Q: Can I change the date range?**
A: Edit `queries/sales_report/bookings.sql` and change the WHERE clause dates

**Q: How do I add more accounts to the renewal table?**
A: Edit `queries/sales_report/renewals.sql` and change `WHERE rank <= 5` to a higher number

**Q: Can I add a new Bullseye recommendation?**
A: Yes! See `docs/INTERACTIVE_SALES_REPORT.md` → "Example 3: Add a New Bullseye Recommendation"

---

## 🔧 Troubleshooting

**Error: "Snowflake authentication failed"**
```bash
snow login --connection zendesk
```

**Error: "Permission denied: generate_sales_report.sh"**
```bash
chmod +x scripts/generate_sales_report.sh
```

**Report generation is slow (>2 minutes)**
- Normal! Snowflake queries take time
- Watch for progress updates in terminal

---

## 📚 More Documentation

- **Full documentation:** `docs/INTERACTIVE_SALES_REPORT.md`
- **SQL queries:** `queries/sales_report/*.sql`
- **Data generator:** `outputs/generate_report_data.py`
- **Shell script:** `scripts/generate_sales_report.sh`

---

## 💡 Tips

1. **Bookmark the report location:**
   ```
   outputs/fy27_sales_report_standalone.html
   ```

2. **Generate daily/weekly** to keep data fresh

3. **Share with your team** - no special software needed, just a browser

4. **Use filters** to focus on specific regions or segments

5. **Click account names** to jump directly to Salesforce

---

## 🎯 Next Steps

Want to customize? See:
- `docs/INTERACTIVE_SALES_REPORT.md` → "Adding New Features"
- Examples for adding metrics, columns, or filters

---

**Questions?** Check the full docs or ask Claude Code!
