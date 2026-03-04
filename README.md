# 📊 Sales Strategy Reporting Agent

> **Automated reporting system for Zendesk Sales Strategy Team**

Generate reports, analyze Snowflake data, and distribute insights across CSV, Excel, and Slack.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Internal](https://img.shields.io/badge/license-Internal-red.svg)](LICENSE)

---

## 🚀 Quick Start

### For Team Members (First Time)

```bash
# 1. Fork this repository (click Fork button on GitHub)

# 2. Clone YOUR fork
git clone https://github.com/YOUR-USERNAME/Zendesk-agent.git
cd Zendesk-agent

# 3. Run setup (15 minutes)
make setup

# 4. Generate your first report
make ai-report
```

**📚 Detailed guide:** [docs/setup/TEAM_SETUP.md](docs/setup/TEAM_SETUP.md)

---

## ⚡ Quick Commands

### Interactive Agent (Recommended)
```bash
strategy-agent   # 🤖 Launch interactive AI assistant
                 # Ask questions, run queries, analyze data
```

### Pre-built Reports & Queries
```bash
make setup          # Interactive setup for new users
make run            # Launch interactive menu
make ai-report      # Generate AI Penetration Report
make country-report # Top 5 countries by ARR and accounts
make validate       # Validate your configuration
make docs           # Show documentation links
make help           # Show all commands
```

---

## 🤖 Interactive AI Agent

The **Sales Strategy Agent** is an interactive AI assistant that helps you analyze data on-demand.

### What You Can Do:

```bash
# Start the agent
strategy-agent

# Then ask questions like:
> "Show me AI penetration by leader"
> "What's AMER Strategic segment penetration?"
> "Compare this quarter to last quarter for EMEA"
> "Create a breakdown by segment for Digital leader"
```

**Benefits:**
- 💬 Natural language queries - no SQL knowledge needed
- 📊 Instant data analysis and insights
- 🎯 Ad-hoc questions answered on-the-spot
- 🧠 Full context of Snowflake tables and conventions
- 📈 Automatic trend comparisons and visualizations

**Setup:** Requires Claude Code installed. See [docs/setup/TEAM_SETUP.md](docs/setup/TEAM_SETUP.md) for installation.

---

## 📊 Available Reports & Queries

### Active Reports

🤖 **AI Penetration Report**
- Track Copilot & AI Agents Advanced adoption
- Breakdown by leader (AMER, EMEA, APAC, LATAM, SMB, Digital)
- Quarter-over-quarter comparisons
- **Run:** `make ai-report`

### Ad-hoc Queries

**Primary Way:** Ask the interactive agent in natural language (e.g., "Show me top 10 countries by growth")

**Convenience Commands:** Pre-built SQL queries can also be run directly:

🌎 **Geographic Analysis**
- **Top Countries by ARR & Accounts** - Current snapshot of top 5 countries
  - **Run:** `make country-report`
- **Country Growth YoY** - Top 5 countries by YoY growth (ARR and accounts)
  - **Run:** `make country-growth-report`
- **Countries with Account Decreases** - Countries losing accounts YoY
  - **Run:** `make country-decreases-report`

🏭 **Industry Analysis**
- **AMER Industry Growth YoY** - Top 5 industries by growth for AMER leader
  - **Run:** `make amer-industry-growth`
  - **Or ask agent:** "Show me EMEA industry growth" (adapts for any leader)

**💡 Tip:** The agent can adapt these patterns for any leader, time period, or top N without needing new commands. Just ask in natural language!

### Coming Soon

- 💼 Account Health Dashboard
- 💰 Revenue Forecast
- 📈 Regional Performance

---

## 📁 Project Structure

```
Zendesk-agent/
├── bin/                    # Executable scripts
│   ├── setup_for_new_user.sh
│   ├── validate_setup.sh
│   └── run_agent.sh
├── config/                 # Configuration
│   ├── config.yaml
│   └── reports/
├── docs/                   # Documentation
│   ├── setup/             # Setup guides
│   ├── maintainer/        # Maintainer docs
│   └── reference/         # Reference guides
├── scripts/                # Python code
│   ├── core/              # Infrastructure
│   └── reports/           # Report implementations
├── queries/                # SQL library
├── outputs/                # Generated files
│   ├── reports/
│   ├── data/
│   └── logs/
├── Makefile               # Convenience commands
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[Setup Guide](docs/setup/TEAM_SETUP.md)** | **Start here!** Complete setup instructions |
| **[Quick Reference](docs/QUICK_REFERENCE.md)** | Daily commands and examples |
| **[Project Overview](docs/PROJECT_OVERVIEW.md)** | Architecture and design |
| **[Contributing](CONTRIBUTING.md)** | How to contribute |
| **[Security](SECURITY.md)** | Security guidelines |
| **[All Docs](docs/)** | Complete documentation index |

---

## 🔄 Fork Workflow

This project uses a **fork workflow** for team collaboration:

1. **Dioney** maintains the main repository
   - Creates all queries and reports
   - Reviews and merges contributions
   - Ensures quality and consistency

2. **Team members** fork to get personal copies
   - Configure their own Snowflake/Google credentials
   - Run existing queries and reports
   - Request new analyses from Dioney

3. **Creating New Reports/Queries**
   - Team members: Request from Dioney via Slack/email
   - Dioney creates in main repo
   - Team members sync to get updates: `make sync`

4. **Other Contributions** (bug fixes, docs, improvements)
   - Create branch in your fork
   - Submit Pull Request to main repo
   - Dioney reviews and merges

**Learn more:** [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🔐 Security

### Each team member has their own:
- ✅ Snowflake authentication (personal SSO)
- ✅ Google Drive credentials (personal OAuth)
- ✅ Configuration settings

### Never shared:
- ❌ Credentials
- ❌ API tokens
- ❌ Personal configs

**Full details:** [SECURITY.md](SECURITY.md)

---

## 🛠️ Development

### Adding a New Report (Maintainer Only)

**Note:** Only the repository maintainer (Dioney) creates new queries and reports. Team members should request new reports by contacting Dioney directly.

**For Dioney:**
```bash
# 1. Create SQL query
mkdir queries/my_report
vim queries/my_report/main.sql

# 2. Create report class (if complex)
vim scripts/reports/my_report.py

# 3. Add Makefile command
vim Makefile

# 4. Update documentation
vim docs/QUICK_REFERENCE.md
vim README.md
vim CLAUDE.md

# 5. Test and commit
make validate
python scripts/reports/my_report.py
git add -A && git commit -m "Add [report_name] report"
```

**For Team Members:**
- ✅ Use existing queries: `make [query-name]`
- ✅ Request new reports from Dioney
- ✅ Sync fork to get new reports: `make sync`
- ❌ Do not create new queries/reports directly

**Detailed guide:** [docs/PROJECT_OVERVIEW.md#adding-new-reports](docs/PROJECT_OVERVIEW.md)

### Running Tests

```bash
make test        # Run all tests
make validate    # Validate setup
```

---

## 🆘 Troubleshooting

### Common Issues

```bash
# Setup validation
make validate

# Check Snowflake connection
make check-snowflake

# View logs
tail -f outputs/logs/sales_strategy_agent.log
```

**More help:** [docs/setup/TEAM_SETUP.md#troubleshooting](docs/setup/TEAM_SETUP.md#troubleshooting)

---

## 👥 Team

**Maintainer:** Dioney Blanco
**Team:** Zendesk Sales Strategy
**Support:** Open an issue or contact maintainer

---

## 📄 License

Internal use only - Zendesk. See [LICENSE](LICENSE) for details.

---

## 🎯 Getting Started Checklist

**For team members setting up:**

- [ ] Fork this repository
- [ ] Clone your fork: `git clone https://github.com/YOUR-USERNAME/Zendesk-agent.git`
- [ ] Run setup: `make setup`
- [ ] Authenticate with Snowflake
- [ ] Generate first report: `make ai-report`
- [ ] Read [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)

**Questions?** See [docs/setup/TEAM_SETUP.md](docs/setup/TEAM_SETUP.md) or open an issue.

---

<div align="center">

**[📖 Setup Guide](docs/setup/TEAM_SETUP.md)** • **[🤝 Contributing](CONTRIBUTING.md)** • **[📚 Docs](docs/)** • **[🔐 Security](SECURITY.md)**

Made with ❤️ for the Sales Strategy Team

</div>
