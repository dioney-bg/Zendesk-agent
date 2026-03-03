# 📁 File Guide - What's What

Quick reference for understanding what each file does and when to use it.

---

## 🚀 For You (Dioney - Maintainer)

| File | Purpose | When to Use |
|------|---------|-------------|
| **DEPLOYMENT_GUIDE.md** | Complete GitHub deployment checklist | Before pushing to GitHub |
| **CONTRIBUTING.md** | Fork workflow and PR guidelines | When team asks about contributing |
| **README_INTERNAL.md** | Detailed internal documentation | Your personal reference |
| **.github/PULL_REQUEST_TEMPLATE.md** | PR template | Automatic (GitHub uses it) |
| **.github/ISSUE_TEMPLATE/** | Bug/feature templates | Automatic (GitHub uses it) |

---

## 👥 For Team Members

| File | Purpose | When to Use |
|------|---------|-------------|
| **README.md** | Project overview on GitHub | First thing they see |
| **TEAM_SETUP.md** | **START HERE** - Setup guide | Setting up for first time |
| **CONTRIBUTING.md** | How to fork and contribute | When they want to contribute |
| **docs/QUICK_REFERENCE.md** | Common commands | Daily usage reference |
| **docs/PROJECT_OVERVIEW.md** | Architecture and design | Building new reports |
| **docs/GOOGLE_DRIVE_SETUP.md** | Google Drive integration | Optional - if they want Drive |

---

## 🔧 Scripts (Executable)

| Script | Purpose | Who Uses |
|--------|---------|----------|
| **setup_for_new_user.sh** | Interactive 15-min setup | Team members (first time) |
| **validate_setup.sh** | Check if setup is correct | Team members (troubleshooting) |
| **run_agent.sh** | Interactive menu for reports | Team members (daily use) |
| **list_structure.sh** | Show project structure | Anyone (exploring) |

---

## 📝 Configuration

| File | Purpose | Customization |
|------|---------|---------------|
| **config/config.yaml** | Main configuration | ✅ Team members customize (their warehouse) |
| **config/reports/*.yaml** | Per-report configs | ❌ Don't customize (use defaults) |
| **.env.example** | Example environment vars | ✅ Copy to .env and customize |
| **.gitignore** | Prevents committing secrets | ❌ Don't modify |

---

## 🐍 Python Code

| Directory | Purpose | Who Modifies |
|-----------|---------|--------------|
| **scripts/core/** | Shared infrastructure | You (maintainer) |
| **scripts/reports/** | Report implementations | You + team (via PRs) |
| **scripts/utils/** | Helper functions | You + team (via PRs) |

---

## 💾 SQL Queries

| Directory | Purpose | Who Adds |
|-----------|---------|----------|
| **queries/ai_penetration/** | AI report queries | You (maintainer) |
| **queries/my_custom/** | Custom queries | Team members (their forks) |

---

## 📊 Outputs

| Directory | Contents | Committed? |
|-----------|----------|------------|
| **outputs/reports/** | Generated CSV/Excel | ❌ No (.gitignored) |
| **outputs/data/** | Raw data exports | ❌ No (.gitignored) |
| **outputs/logs/** | Application logs | ❌ No (.gitignored) |

---

## 📚 Documentation Order

### For New Team Members:
1. **README.md** (GitHub landing page)
2. **TEAM_SETUP.md** (15-min setup guide)
3. **docs/QUICK_REFERENCE.md** (daily commands)
4. **docs/PROJECT_OVERVIEW.md** (when building reports)

### For Contributors:
1. **CONTRIBUTING.md** (fork workflow)
2. **docs/PROJECT_OVERVIEW.md** (architecture)
3. **.github/PULL_REQUEST_TEMPLATE.md** (PR format)

### For You (Maintainer):
1. **DEPLOYMENT_GUIDE.md** (deployment steps)
2. **README_INTERNAL.md** (detailed docs)
3. **CONTRIBUTING.md** (reviewing PRs)

---

## 🔑 Key Files Explained

### README.md vs README_INTERNAL.md

- **README.md** → GitHub landing page (team sees this)
- **README_INTERNAL.md** → Your detailed internal docs

### TEAM_SETUP.md vs CONTRIBUTING.md

- **TEAM_SETUP.md** → How to set up and use
- **CONTRIBUTING.md** → How to fork and contribute back

### config.yaml vs config/reports/*.yaml

- **config.yaml** → System-wide settings (Snowflake, outputs)
- **reports/*.yaml** → Per-report settings (metrics, breakdowns)

---

## 🎯 Quick Decision Tree

**"I want to..."**

→ **Set up on my laptop**
  Use: `TEAM_SETUP.md` → `setup_for_new_user.sh`

→ **Generate a report**
  Use: `run_agent.sh` or `python scripts/reports/ai_penetration.py`

→ **Build a new report**
  Use: `docs/PROJECT_OVERVIEW.md` → Copy existing report structure

→ **Contribute back**
  Use: `CONTRIBUTING.md` → Follow fork workflow

→ **Deploy to GitHub** (Dioney only)
  Use: `DEPLOYMENT_GUIDE.md`

→ **Troubleshoot setup**
  Use: `validate_setup.sh` → Check logs → `TEAM_SETUP.md` troubleshooting

---

## 📦 What Gets Committed vs Ignored

### ✅ Committed (in Git)
- Python code (.py files)
- SQL queries (.sql files)
- Documentation (.md files)
- Configuration templates
- Shell scripts
- .gitignore

### ❌ Ignored (NOT in Git)
- Virtual environment (venv/)
- Credentials (*.json, .env)
- Generated reports (outputs/)
- Personal configs
- Logs

---

## 🎓 Cheat Sheet

**Common Files by Task:**

| Task | Files to Reference |
|------|-------------------|
| First-time setup | TEAM_SETUP.md, setup_for_new_user.sh |
| Daily report generation | run_agent.sh, docs/QUICK_REFERENCE.md |
| Building new report | docs/PROJECT_OVERVIEW.md, scripts/reports/*.py |
| Contributing | CONTRIBUTING.md, .github/PULL_REQUEST_TEMPLATE.md |
| Troubleshooting | validate_setup.sh, TEAM_SETUP.md, logs/ |
| Syncing fork | CONTRIBUTING.md (sync section) |
| Deploying (Dioney) | DEPLOYMENT_GUIDE.md |

---

**Questions about which file to use?**

Check this guide first, or see the main README.md for project overview.
