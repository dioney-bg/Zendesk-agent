# Quick Reference Guide

## 🤖 Interactive AI Agent (Recommended)

The fastest way to analyze data and answer questions:

```bash
# Start the interactive agent
strategy-agent
```

Then ask questions in natural language:
```
> "Show me AI penetration by leader"
> "What's AMER's Strategic segment penetration?"
> "Compare Q1 to Q4 for EMEA"
> "Break down Digital leader by segment"
> "Show me top 10 accounts that adopted AI this quarter"
```

**Benefits:**
- No need to remember SQL or command syntax
- Instant answers to ad-hoc questions
- Automatic visualizations and insights
- Follows all reporting conventions (ordering, totals, etc.)

**Setup:** Requires Claude Code installed:
```bash
brew install anthropics/claude/claude-code
# or visit: https://docs.anthropic.com/claude-code
```

---

## Daily Workflow (Pre-built Reports)

### 1. Generate Report (All Formats)
```bash
cd /Users/dioney.blanco/Zendesk-agent
source venv/bin/activate
python scripts/run_report_pipeline.py
```

### 2. Generate Report (No Google Drive)
```bash
python scripts/run_report_pipeline.py --no-drive
```

### 3. Generate Only CSV
```bash
python scripts/run_report_pipeline.py --formats csv
```

### 4. Slack Only (Fast)
```bash
./scripts/post_ai_report.sh
```

## File Locations

| What | Where |
|------|-------|
| Generated CSVs | `outputs/reports/ai_penetration_report_*.csv` |
| Generated Excel | `outputs/reports/ai_penetration_report_*.xlsx` |
| Logs | `outputs/logs/zendesk_agent.log` |
| Config | `config/config.yaml` |
| Scripts | `scripts/*.py` |

## Common Tasks

### View Latest Report
```bash
ls -lt outputs/reports/ | head -5
open outputs/reports/$(ls -t outputs/reports/ | head -1)
```

### Upload Existing File to Drive
```python
from scripts.google_drive_uploader import GoogleDriveUploader

uploader = GoogleDriveUploader()
folder_id = uploader.get_folder_id("Zendesk AI Reports")
uploader.upload_file("outputs/reports/my_report.csv", folder_id=folder_id)
```

### Check Snowflake Connection
```bash
/Applications/SnowflakeCLI.app/Contents/MacOS/snow sql -q "SELECT CURRENT_DATE()"
```

### List Google Drive Files
```python
from scripts.google_drive_uploader import GoogleDriveUploader

uploader = GoogleDriveUploader()
folder_id = uploader.get_folder_id("Zendesk AI Reports")
uploader.list_files(folder_id=folder_id)
```

## Automation

### Schedule Daily Report (9 AM)
```bash
crontab -e
```

Add:
```
0 9 * * * cd /Users/dioney.blanco/Zendesk-agent && source venv/bin/activate && python scripts/run_report_pipeline.py >> outputs/logs/cron.log 2>&1
```

### Schedule Weekly Report (Monday 9 AM)
```
0 9 * * 1 cd /Users/dioney.blanco/Zendesk-agent && source venv/bin/activate && python scripts/run_report_pipeline.py >> outputs/logs/cron.log 2>&1
```

## Aliases (Optional)

Add to `~/.zshrc`:

```bash
# Zendesk AI Reports
alias ai-report='cd /Users/dioney.blanco/Zendesk-agent && source venv/bin/activate && python scripts/run_report_pipeline.py'
alias ai-slack='cd /Users/dioney.blanco/Zendesk-agent && ./scripts/post_ai_report.sh'
alias ai-logs='tail -f /Users/dioney.blanco/Zendesk-agent/outputs/logs/zendesk_agent.log'
```

Then:
```bash
source ~/.zshrc
ai-report  # Run full pipeline
```

## Report Contents

### AI Penetration Report Includes:
- Total accounts by leader (AMER, EMEA, APAC, LATAM, SMB, Digital)
- AI penetration % (accounts with Copilot or AI Agents Advanced)
- Change vs previous quarter
- Breakdown by product (Copilot, AAA)
- Account counts

### Output Formats:
1. **CSV** - For analysis in Excel/Google Sheets
2. **Excel** - Formatted with auto-sized columns
3. **Slack** - Markdown formatted, copied to clipboard

## Troubleshooting

### "ModuleNotFoundError: No module named 'X'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Failed to retrieve data from Snowflake"
1. Check Snowflake CLI: `/Applications/SnowflakeCLI.app/Contents/MacOS/snow sql -q "SELECT 1"`
2. Re-authenticate: `snow login`

### "Google credentials not found"
1. Follow [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md)
2. Or skip Drive: `python scripts/run_report_pipeline.py --no-drive`

### "Permission denied" on scripts
```bash
chmod +x scripts/*.py
chmod +x scripts/*.sh
```

## Need Help?

- Check logs: `outputs/logs/zendesk_agent.log`
- Test components individually
- Review README.md for full documentation
