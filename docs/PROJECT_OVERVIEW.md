# Sales Strategy Reporting Agent - Project Overview

## 🎯 Purpose

This is a **Sales Strategy Reporting Agent** for the Zendesk Sales Strategy Team. It automates the generation, formatting, and distribution of various sales and customer success reports from Snowflake data.

## 📋 Current Reports

### Active Reports
1. **AI Penetration Report** - Copilot and AI Agents Advanced adoption metrics by leader

### Planned Reports
2. **Account Health Dashboard** - Customer health scores and risk indicators
3. **Revenue Forecast** - ARR projections and pipeline analysis
4. **Regional Performance** - Sales metrics by region
5. **Top 3K Analysis** - Deep dive into top accounts

## 🏗️ Architecture

### Modular Design

The agent follows a modular architecture where:
- **Core modules** provide shared functionality (database, formatting, uploads)
- **Report classes** inherit from `BaseReport` and implement specific logic
- **SQL queries** are stored separately for version control and reusability
- **Configurations** are YAML-based for easy customization

### Data Flow

```
┌─────────────┐
│  Snowflake  │
│   Database  │
└──────┬──────┘
       │
       ↓ (SQL Query)
┌──────────────────┐
│ SnowflakeClient  │
│  (Core Module)   │
└──────┬───────────┘
       │
       ↓ (Raw Data)
┌──────────────────┐
│  Report Class    │
│ - Process Data   │
│ - Calculate      │
└──────┬───────────┘
       │
       ↓ (Processed Data)
┌──────────────────┐
│ ReportFormatter  │
│  (Core Module)   │
└──────┬───────────┘
       │
       ├─→ CSV File
       ├─→ Excel File
       ├─→ Slack Message
       └─→ Google Drive

```

### Directory Organization

```
Zendesk-agent/
│
├── config/                      # All configuration
│   ├── config.yaml             # Main settings
│   └── reports/                # Per-report configs
│
├── scripts/                     # All code
│   ├── core/                   # Reusable infrastructure
│   │   ├── snowflake_client.py      # Database access
│   │   ├── google_drive_uploader.py # Cloud storage
│   │   ├── report_formatter.py      # Output formatting
│   │   └── base_report.py           # Report template
│   │
│   ├── reports/                # Report implementations
│   │   ├── ai_penetration.py        # AI metrics
│   │   ├── account_health.py        # (future)
│   │   └── revenue_forecast.py      # (future)
│   │
│   └── utils/                  # Helper functions
│
├── queries/                     # SQL query library
│   ├── ai_penetration/
│   ├── account_health/
│   └── revenue/
│
├── templates/                   # Output templates
│   ├── slack/                  # Markdown templates
│   ├── excel/                  # Formatting rules
│   └── email/                  # HTML templates (future)
│
└── outputs/                     # Generated files
    ├── reports/                # By report type
    │   ├── ai_penetration/
    │   └── ...
    ├── data/                   # Raw exports
    └── logs/                   # Application logs
```

## 🔄 Adding New Reports

### Step-by-Step Guide

1. **Create SQL Query**
   ```bash
   mkdir queries/my_report
   vim queries/my_report/main_query.sql
   ```

2. **Create Report Config**
   ```bash
   cp config/reports/ai_penetration.yaml config/reports/my_report.yaml
   # Edit as needed
   ```

3. **Implement Report Class**
   ```python
   # scripts/reports/my_report.py
   from scripts.core.base_report import BaseReport

   class MyReport(BaseReport):
       def __init__(self):
           super().__init__(report_code='my_report')

       def generate_query(self) -> str:
           query_file = Path('queries/my_report/main_query.sql')
           with open(query_file, 'r') as f:
               return f.read()

       def process_data(self, data):
           # Optional: transform data
           return data

       def format_slack(self, data):
           # Optional: custom Slack formatting
           return super().format_slack(data)
   ```

4. **Register in Config**
   ```yaml
   # config/config.yaml
   reports:
     my_report:
       name: "My Report"
       enabled: true
       outputs: [csv, excel, slack]
   ```

5. **Test**
   ```bash
   python scripts/reports/my_report.py
   ```

## 🎨 Report Outputs

### CSV
- Raw data export
- For analysis in Excel/Sheets
- Saved to `outputs/reports/{report}/`

### Excel
- Formatted workbook
- Auto-sized columns
- Frozen headers
- Professional presentation

### Slack
- Markdown formatted
- Emoji indicators
- Summary + details
- Auto-copied to clipboard

### Google Drive (Optional)
- Organized folder structure
- Timestamped uploads
- Shareable links

## 🔧 Configuration System

### Three-Level Configuration

1. **System Config** (`config/config.yaml`)
   - Snowflake connection
   - Google Drive settings
   - Default formats
   - Logging preferences

2. **Report Config** (`config/reports/{report}.yaml`)
   - Report-specific settings
   - Data sources
   - Metrics definitions
   - Output preferences

3. **Environment Variables** (`.env`)
   - Sensitive credentials
   - API tokens
   - Personal preferences

### Example Config Flow

```yaml
# config/config.yaml
reports:
  ai_penetration:
    config_file: "config/reports/ai_penetration.yaml"
    outputs: [csv, excel, slack]

# config/reports/ai_penetration.yaml
report:
  name: "AI Penetration Report"

metrics:
  - name: "penetration_pct"
    format: "percentage"

output:
  slack:
    emoji: "🤖"
```

## 📊 Standard Breakdowns

All reports use consistent breakdowns:

### By Leader
1. AMER
2. EMEA
3. APAC
4. LATAM
5. SMB
6. Digital

### By Segment
1. Enterprise
2. Strategic
3. Public Sector
4. Commercial
5. SMB
6. Digital

### By Region
1. AMER
2. EMEA
3. APAC
4. LATAM

### Fiscal Calendar
- **Q1:** Feb, Mar, Apr
- **Q2:** May, Jun, Jul
- **Q3:** Aug, Sep, Oct
- **Q4:** Nov, Dec, Jan

(Fiscal year starts in February)

## 🚀 Usage Patterns

### Ad-Hoc Report
```bash
cd /Users/dioney.blanco/Zendesk-agent
source venv/bin/activate
python scripts/reports/ai_penetration.py
```

### Scheduled Report (Cron)
```cron
0 9 * * * cd ~/Zendesk-agent && source venv/bin/activate && python scripts/reports/ai_penetration.py >> outputs/logs/cron.log 2>&1
```

### Custom Formats
```bash
# CSV only
python scripts/reports/ai_penetration.py --formats csv

# Excel + Slack
python scripts/reports/ai_penetration.py --formats excel slack
```

### With Google Drive Upload
Automatic if `google_drive.enabled: true` in config

## 🔐 Security Model

### Credentials
- Snowflake: CLI-based SSO (no stored passwords)
- Google Drive: OAuth 2.0 (token stored locally)
- Slack: CLI authentication (credentials in `~/.slack/`)

### Data Protection
- All credentials in `.gitignore`
- No hardcoded secrets
- Local-only token storage
- API calls use HTTPS

### Access Control
- Reports use service accounts when available
- Minimum required permissions
- Audit logs in `outputs/logs/`

## 📈 Extensibility

### Adding Output Formats

Add to `ReportFormatter`:
```python
def save_powerpoint(self, data, filepath):
    # Implementation
    pass
```

Update report config:
```yaml
outputs: [csv, excel, slack, powerpoint]
```

### Adding Data Sources

Beyond Snowflake:
```python
from scripts.core.postgres_client import PostgresClient
from scripts.core.salesforce_client import SalesforceClient
```

### Adding Distribution Channels

Beyond Slack and Google Drive:
```python
from scripts.core.email_sender import EmailSender
from scripts.core.teams_messenger import TeamsMessenger
```

## 🛠️ Maintenance

### Regular Tasks
- Monitor logs: `outputs/logs/`
- Review old reports: `outputs/reports/`
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Refresh Google token: Automatically handled

### Troubleshooting
- Check Snowflake connection: `snow sql -q "SELECT 1"`
- Verify Python environment: `which python`
- View report logs: `tail -f outputs/logs/sales_strategy_agent.log`

### Performance
- Query optimization: Review `queries/` SQL files
- Caching: Add intermediate data storage
- Parallel execution: Run multiple reports concurrently

## 📞 Support

### For Issues
1. Check logs in `outputs/logs/`
2. Review configuration in `config/`
3. Test Snowflake connection
4. Verify Python dependencies

### For Questions
- Architecture: See this document
- Usage: See `docs/QUICK_REFERENCE.md`
- Google Drive: See `docs/GOOGLE_DRIVE_SETUP.md`
- Code: Inline documentation in scripts

## 🎓 Best Practices

### When Adding Reports
1. ✅ Use descriptive report codes (snake_case)
2. ✅ Store SQL in `queries/` (version controlled)
3. ✅ Add comprehensive config in `config/reports/`
4. ✅ Test with sample data first
5. ✅ Document metrics and assumptions

### When Writing Queries
1. ✅ Comment complex logic
2. ✅ Use CTEs for readability
3. ✅ Add report header comments
4. ✅ Follow leader/segment ordering
5. ✅ Include fiscal calendar logic

### When Configuring Outputs
1. ✅ Match team's existing formats
2. ✅ Use consistent emoji in Slack
3. ✅ Include context in subtitles
4. ✅ Format numbers appropriately
5. ✅ Add generation timestamps

## 🗺️ Roadmap

### Short Term
- [ ] Add Account Health Dashboard
- [ ] Add Revenue Forecast Report
- [ ] Implement email distribution
- [ ] Add report scheduling UI

### Medium Term
- [ ] Add interactive dashboards
- [ ] Implement data caching
- [ ] Add unit tests
- [ ] Create report templates library

### Long Term
- [ ] Self-service report builder
- [ ] ML-powered insights
- [ ] Real-time streaming reports
- [ ] Mobile app integration

---

**Last Updated:** March 3, 2026
**Maintainer:** Sales Strategy Team
**Version:** 1.0.0
