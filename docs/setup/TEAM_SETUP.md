# 🚀 Team Setup Guide - Sales Strategy Reporting Agent

Welcome! This guide will help you set up your personal copy of the Sales Strategy Reporting Agent.

## 📋 Prerequisites

Before you start, make sure you have:

- [ ] Python 3.8 or higher installed
- [ ] Git installed
- [ ] **Claude Code installed** (for interactive agent - recommended!)
- [ ] Snowflake CLI installed
- [ ] Access to Zendesk Snowflake account (ZENDESK-GLOBAL)
- [ ] Your Snowflake username and warehouse access

### Installing Claude Code (Recommended)

The interactive AI agent requires Claude Code:

**macOS:**
```bash
brew install anthropics/claude/claude-code
```

**Or download from:** https://docs.anthropic.com/claude-code

This enables the `strategy-agent` command for natural language data analysis!

## 🔧 Setup Steps (15 minutes)

### 1. Fork the Repository

1. Go to the main repository on GitHub
2. Click **"Fork"** button (top right)
3. This creates YOUR personal copy

### 2. Clone Your Fork

```bash
# Replace YOUR-USERNAME with your GitHub username
git clone https://github.com/YOUR-USERNAME/Zendesk-agent.git
cd Zendesk-agent
```

### 3. Run the Setup Script

We've created an interactive setup script to make this easy:

```bash
make setup
```

This will:
- ✅ Create your Python virtual environment
- ✅ Install all dependencies
- ✅ Configure your Snowflake connection
- ✅ Test the connection
- ✅ Install the strategy-agent command
- ✅ Generate your first report

**Or follow manual steps below:**

---

## 🛠️ Manual Setup (if script doesn't work)

### Step 1: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Snowflake CLI

```bash
# Test if Snowflake CLI is installed
/Applications/SnowflakeCLI.app/Contents/MacOS/snow --version

# If not installed, download from:
# https://docs.snowflake.com/en/user-guide/snowsql-install-config
```

### Step 4: Authenticate with Snowflake

```bash
/Applications/SnowflakeCLI.app/Contents/MacOS/snow login
```

Follow the browser prompts to authenticate.

**Important:** Make sure you select:
- **Connection name:** `zendesk` (or update `config/config.yaml`)
- **Account:** `ZENDESK-GLOBAL`
- **Warehouse:** Your assigned warehouse (e.g., `COEFFICIENT_WH`)

### Step 5: Update Configuration

Edit `config/config.yaml` with your settings:

```yaml
snowflake:
  connection_name: zendesk  # Your connection name
  warehouse: YOUR_WAREHOUSE_NAME  # Ask your manager
```

### Step 6: Test Your Setup

```bash
# Test Snowflake connection
/Applications/SnowflakeCLI.app/Contents/MacOS/snow sql -q "SELECT CURRENT_USER()"

# Generate your first report
source venv/bin/activate
python scripts/reports/ai_penetration.py
```

If successful, you'll see:
```
✅ Report generated successfully!
Generated files:
  📄 CSV: outputs/reports/ai_penetration/ai_penetration_TIMESTAMP.csv
  📊 Excel: outputs/reports/ai_penetration/ai_penetration_TIMESTAMP.xlsx
  📋 Slack: Copied to clipboard
```

---

## 🔗 Google Drive Setup (Optional)

**Want to automatically upload reports to the team's shared drive?**

This is optional but recommended for team collaboration. Reports will upload to:
**SalesStrategy / Strategy-agent** (shared drive folder)

### Prerequisites

- [ ] Access to SalesStrategy shared drive (ask admin to add you)
- [ ] ~20 minutes for first-time setup

### Quick Setup

```bash
make setup-drive
```

This interactive script will:
1. Guide you through creating your personal OAuth client
2. Help you authenticate with Google
3. Test your shared drive access
4. Verify uploads work

**See full guide:** [docs/GOOGLE_DRIVE_SETUP.md](../GOOGLE_DRIVE_SETUP.md)

### What Gets Created

**Personal credentials (never committed):**
- `config/google_credentials.json` - Your OAuth client ID
- `config/token.json` - Your personal access token

Both files are gitignored for security.

### Test Your Setup

```bash
# Test shared drive connection
make test-drive

# Generate report (auto-uploads to shared drive)
make ai-report
```

### Troubleshooting

**"Shared drive not found"**
- Ask admin to add you to SalesStrategy shared drive
- Verify drive name in `config/config.yaml`

**"Old token doesn't work"**
```bash
rm config/token.json
make setup-drive  # Re-authenticate
```

**Full troubleshooting:** [docs/GOOGLE_DRIVE_SETUP.md#troubleshooting](../GOOGLE_DRIVE_SETUP.md#troubleshooting)

---

## 📊 Using the Agent

### 🤖 Interactive AI Agent (Recommended!)

The easiest way to analyze data - just ask questions in natural language:

```bash
# Start the interactive agent
strategy-agent

# Or
make agent
```

**Then ask questions like:**
- "Show me AI penetration by leader"
- "What's AMER's Strategic segment penetration?"
- "Compare this quarter to last quarter"
- "Break down EMEA by segment"

**No SQL knowledge needed!** See [docs/INTERACTIVE_AGENT.md](../INTERACTIVE_AGENT.md) for full guide.

---

### 📋 Pre-built Reports

**AI Penetration Report:**
```bash
make ai-report
```

**Interactive menu:**
```bash
make run
```

**Validate setup:**
```bash
make validate
```

---

## 🔄 Keeping Your Fork Updated

The maintainer (Dioney) will add new reports and features. To get updates:

### Option 1: Sync via GitHub UI
1. Go to your fork on GitHub
2. Click **"Sync fork"** button
3. Click **"Update branch"**

### Option 2: Sync via Command Line
```bash
# One-time setup: Add upstream remote
git remote add upstream https://github.com/dioney-blanco/Zendesk-agent.git

# Whenever you want updates:
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

**Pro tip:** After syncing, run `pip install -r requirements.txt` in case dependencies changed.

---

## 🎯 Customizing for Your Needs

### Add Your Own Queries

You can create custom queries in your fork without affecting others:

```bash
# Create your folder
mkdir queries/my_analysis

# Add your SQL
vim queries/my_analysis/my_query.sql

# Run it
python scripts/run_custom_query.py queries/my_analysis/my_query.sql
```

### Customize Output Formats

Edit `config/config.yaml` to change defaults:

```yaml
formatting:
  date_format: "%Y-%m-%d"  # Change date format
  number_format:
    decimal_places: 2       # Change decimals
```

---

## ❓ Troubleshooting

### "Snowflake CLI not found"

Install Snowflake CLI:
```bash
# Check installation location
which snow

# If not found, download from:
# https://docs.snowflake.com/en/user-guide/snowsql-install-config
```

### "Authentication failed"

Re-authenticate:
```bash
/Applications/SnowflakeCLI.app/Contents/MacOS/snow login
```

### "ModuleNotFoundError"

Make sure virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Query execution failed"

Check your warehouse access:
```bash
# Test connection
/Applications/SnowflakeCLI.app/Contents/MacOS/snow sql -q "SELECT CURRENT_WAREHOUSE()"

# Ask your manager if you need warehouse access
```

### "Permission denied" on scripts

Make scripts executable:
```bash
chmod +x scripts/*.py
chmod +x scripts/*.sh
chmod +x *.sh
```

---

## 🆘 Getting Help

1. **Check logs:**
   ```bash
   tail -f outputs/logs/sales_strategy_agent.log
   ```

2. **Read documentation:**
   - `README.md` - Main documentation
   - `docs/PROJECT_OVERVIEW.md` - Architecture
   - `docs/QUICK_REFERENCE.md` - Common commands

3. **Contact maintainer:**
   - **Maintainer:** Dioney Blanco
   - **For issues:** Open an issue on GitHub
   - **For questions:** Slack or email

---

## 🔐 Security Notes

### What to NEVER commit:

- ❌ Your Snowflake credentials
- ❌ `config/google_credentials.json`
- ❌ `config/token.json`
- ❌ `.env` file with secrets
- ❌ Personal API keys

The `.gitignore` file protects these automatically, but be careful with `git add .`

### Your Personal Fork

- ✅ Your fork is YOUR workspace
- ✅ You can customize freely
- ✅ Changes stay in your fork
- ✅ You pull updates from main repo
- ✅ You don't push to main repo (unless contributing)

---

## 📢 Contributing Back

If you create a useful report or improvement:

1. Create a branch in your fork
2. Make your changes
3. Test thoroughly
4. Open a Pull Request to the main repo
5. Dioney will review and merge

**Example:**
```bash
git checkout -b feature/account-health-report
# Make changes
git commit -m "Add account health report"
git push origin feature/account-health-report
# Open PR on GitHub
```

---

## ✅ Setup Checklist

Before you're done, verify:

**Required:**
- [ ] Claude Code installed (`claude --version`) - for interactive agent
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list` shows packages)
- [ ] Snowflake CLI working (`snow --version`)
- [ ] Snowflake authenticated (`snow sql -q "SELECT 1"`)
- [ ] Config updated with your settings
- [ ] `strategy-agent` command works from any directory
- [ ] First report generated successfully
- [ ] Output files created in `outputs/reports/`
- [ ] You can read the generated reports

**Optional (Google Drive):**
- [ ] Google Drive OAuth client created
- [ ] Authenticated with Google (`config/token.json` exists)
- [ ] Shared drive access verified (`make test-drive` passes)
- [ ] Test upload successful

---

## 🎉 You're Ready!

You now have your own personal copy of the Sales Strategy Reporting Agent!

**Try the interactive agent first:**
```bash
strategy-agent
```

**Next steps:**
- Ask the agent questions about your data!
- Read [docs/INTERACTIVE_AGENT.md](../INTERACTIVE_AGENT.md) for tips
- Read [docs/QUICK_REFERENCE.md](../QUICK_REFERENCE.md) for common commands
- Explore pre-built reports in `scripts/reports/`
- Generate and share insights with your team

**Questions?** Contact Dioney or check the documentation.

---

**Last Updated:** March 2026
**Maintainer:** Dioney Blanco
**Version:** 1.0.0
