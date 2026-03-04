# Contributing to Sales Strategy Reporting Agent

Thank you for using the Sales Strategy Reporting Agent! This guide explains how the fork workflow works and how you can contribute improvements back to the main repository.

## 🔄 Understanding the Fork Workflow

### Main Repository (Dioney's)
- **Owner:** Dioney Blanco
- **Purpose:** Core codebase, shared reports, infrastructure
- **Permissions:** Only Dioney can merge changes
- **Updates:** New features, bug fixes, new reports

### Your Fork (Team Member)
- **Owner:** You
- **Purpose:** Your personal workspace
- **Permissions:** Full control over your copy
- **Customizations:** Personal configs, custom queries, local experiments

## 📋 Fork Workflow Overview

```
┌─────────────────────────────────────┐
│   Main Repository (Dioney)          │
│   - Core codebase                   │
│   - Shared reports                  │
│   - Official releases                │
└────────────┬────────────────────────┘
             │
             │ Fork (one-time)
             ↓
┌─────────────────────────────────────┐
│   Your Fork (You)                   │
│   - Your personal copy              │
│   - Custom configurations           │
│   - Local experiments               │
└────────────┬────────────────────────┘
             │
             │ Clone to laptop
             ↓
┌─────────────────────────────────────┐
│   Local Copy (Your Laptop)          │
│   - Where you work                  │
│   - Run reports                     │
│   - Make changes                    │
└─────────────────────────────────────┘
```

## 🚀 Getting Started

### 1. Initial Setup

```bash
# Fork the repository on GitHub (click Fork button)

# Clone YOUR fork (replace YOUR-USERNAME)
git clone https://github.com/YOUR-USERNAME/Zendesk-agent.git
cd Zendesk-agent

# Add main repo as upstream (for getting updates)
git remote add upstream https://github.com/dioney-blanco/Zendesk-agent.git

# Verify remotes
git remote -v
# Should show:
# origin    https://github.com/YOUR-USERNAME/Zendesk-agent.git
# upstream  https://github.com/dioney-blanco/Zendesk-agent.git
```

### 2. Run Setup

```bash
./setup_for_new_user.sh
```

## 📊 Requesting New Reports or Queries

**Important:** Only Dioney (the repository maintainer) creates new reports and queries for the team.

### Why This Approach?

- ✅ Ensures quality and consistency across all reports
- ✅ Maintains clear ownership and maintenance
- ✅ Follows team conventions and standards
- ✅ Centralizes documentation and discovery

### How to Request a New Report

1. **Contact Dioney directly:**
   - Slack/email with your request
   - Describe what analysis you need
   - Explain the business value
   - Provide any specific requirements

2. **Dioney will:**
   - Assess feasibility and priority
   - Create the query/report in main repo
   - Add documentation and commands
   - Notify you when it's ready

3. **You sync your fork:**
   ```bash
   make sync  # Get the new report
   make country-report  # Example: use the new command
   ```

### What You CAN Create

✅ **Personal queries in your fork** (not submitted back):
```bash
mkdir queries/my_personal_analysis
vim queries/my_personal_analysis/custom.sql
```

✅ **Local experiments** (not submitted back):
```bash
# Try things locally, keep in your fork
```

### What You Should Request from Dioney

❌ **New shared queries** (in `queries/` directory)
❌ **New reports** (in `scripts/reports/`)
❌ **New Makefile targets** for team use

**Remember:** You own your fork and can do anything locally. But for SHARED queries/reports that the team will use, request from Dioney.

## 🔄 Keeping Your Fork Updated

Dioney will periodically add new features and reports. Here's how to get them:

### Option A: GitHub UI (Easiest)

1. Go to your fork on GitHub
2. You'll see: "This branch is X commits behind dioney-blanco:main"
3. Click **"Sync fork"**
4. Click **"Update branch"**
5. Pull changes to your laptop:
   ```bash
   git pull origin main
   pip install -r requirements.txt  # Update dependencies if needed
   ```

### Option B: Command Line

```bash
# Get latest changes from main repo
git fetch upstream

# Make sure you're on main branch
git checkout main

# Merge updates from main repo
git merge upstream/main

# Push to your fork on GitHub
git push origin main

# Update dependencies if needed
pip install -r requirements.txt
```

**When to sync:**
- Weekly (if you use the agent regularly)
- When you hear about new features
- Before creating custom reports (to start with latest)
- If something breaks (might be fixed in latest)

## 🎨 Making Personal Customizations

### What You Can Customize Freely

✅ **Personal configurations:**
```yaml
# config/config.yaml
snowflake:
  warehouse: YOUR_WAREHOUSE  # Your warehouse
  connection_name: your_name  # Your connection
```

✅ **Custom queries:**
```bash
# Create personal queries
mkdir queries/my_analysis
vim queries/my_analysis/my_query.sql
```

✅ **Local experiments:**
```bash
# Try new features locally
# Changes stay in your fork
```

✅ **Output preferences:**
```yaml
# config/config.yaml
formatting:
  date_format: "%d/%m/%Y"  # Your preferred format
```

### What to Avoid Changing

❌ **Core infrastructure** (unless contributing back):
- `scripts/core/*.py`
- `config/config.yaml` structure

❌ **Shared SQL queries** (unless fixing bugs):
- `queries/ai_penetration/*.sql`

**Why?** These changes will conflict when you sync updates from main repo.

## 🤝 Contributing Back to Main Repository

Found a bug or want to improve existing functionality? You can contribute!

### What You CAN Contribute via PR

- ✅ **Bug fixes** in existing reports or queries
- ✅ **Performance improvements** to existing queries
- ✅ **Documentation improvements** (typos, clarity, examples)
- ✅ **Infrastructure improvements** (setup scripts, tooling)
- ✅ **Code refactoring** (better organization, cleaner code)

### What You Should REQUEST Instead (Not PR)

- ❌ **New reports** → Request from Dioney
- ❌ **New queries** → Request from Dioney
- ❌ **New analyses** → Request from Dioney

**Why?** Dioney maintains ownership of all team queries/reports to ensure quality, consistency, and proper documentation.

### How to Contribute

#### Step 1: Create a Feature Branch

```bash
# Make sure you're up to date
git checkout main
git pull upstream main

# Create a branch for your contribution
git checkout -b fix/ai-penetration-calculation
# Or: git checkout -b docs/improve-setup-guide
# Or: git checkout -b perf/optimize-country-query
```

#### Step 2: Make Your Changes

**Example: Bug Fix**
```bash
# Fix bug in existing report
vim scripts/reports/ai_penetration.py

# Test thoroughly
python scripts/reports/ai_penetration.py
```

**Example: Documentation Improvement**
```bash
# Improve setup documentation
vim docs/setup/TEAM_SETUP.md

# Fix typos in README
vim README.md
```

**Example: Performance Optimization**
```bash
# Optimize existing query
vim queries/geographic/top_countries_by_arr_and_accounts.sql

# Test performance improvement
make country-report
```

#### Step 3: Test Everything

```bash
# Run your report multiple times
python scripts/reports/account_health.py

# Check different scenarios
# Verify outputs
# Review SQL query performance
```

#### Step 4: Commit Your Changes

```bash
# Stage your changes
git add scripts/reports/ai_penetration.py

# Commit with clear message
git commit -m "Fix AI penetration calculation for SMB segment

- Corrected leader assignment logic for SMB
- Added validation for TOTAL row
- Updated test cases
- Fixes #123"
```

#### Step 5: Push to Your Fork

```bash
# Push your branch to YOUR fork on GitHub
git push origin fix/ai-penetration-calculation
```

#### Step 6: Open a Pull Request

1. Go to your fork on GitHub
2. You'll see: "Compare & pull request" button
3. Click it
4. Fill in the PR description:
   - **What** does this add/fix?
   - **Why** is it useful?
   - **How** to test it?
   - Screenshots or example outputs
5. Click "Create pull request"
6. Dioney will review and provide feedback

### Pull Request Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] Performance improvement
- [ ] Documentation improvement
- [ ] Code refactoring
- [ ] Infrastructure improvement
- [ ] Other (describe)

**Note:** New reports/queries should be requested from Dioney, not submitted via PR.

## Testing
- [ ] Report runs successfully
- [ ] Output files generated correctly
- [ ] SQL query optimized
- [ ] Documentation updated

## Screenshots/Examples
[Add screenshots of output or example data]

## Additional Context
Any other context about the PR
```

## 🔍 Code Review Process

### What Dioney Will Review

1. **Functionality:** Does it work as intended?
2. **Code Quality:** Is it clean and maintainable?
3. **Performance:** Are queries optimized?
4. **Documentation:** Is it well-documented?
5. **Testing:** Has it been tested thoroughly?
6. **Compatibility:** Does it work with existing code?

### Possible Outcomes

- ✅ **Approved & Merged:** Your contribution is added to main repo!
- 💬 **Comments:** Dioney suggests improvements
- ❌ **Changes Requested:** Needs modifications before merging
- 🚫 **Closed:** Not suitable for main repo (rare)

## 📝 Best Practices

### For Personal Use

- ✅ Sync your fork regularly
- ✅ Keep personal configs in your fork
- ✅ Document your custom queries
- ✅ Back up important customizations

### For Contributing

- ✅ Start with latest main branch
- ✅ One feature per PR
- ✅ Clear, descriptive commit messages
- ✅ Test thoroughly before submitting
- ✅ Update documentation
- ✅ Follow existing code style

### Commit Message Guidelines

**Good:**
```
Add revenue forecast report

- Quarterly and yearly projections
- Pipeline analysis included
- Optimized query performance
```

**Bad:**
```
updates
```

## ❓ FAQ

### "Can I push directly to the main repository?"

**No.** Only Dioney can merge changes. You must:
1. Make changes in your fork
2. Open a Pull Request
3. Wait for review and approval

### "What if my fork gets out of sync?"

No problem! Just sync it:
```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

### "Can I use this for my own projects?"

Your fork is yours! But:
- ✅ Use for Zendesk sales strategy work
- ✅ Customize for your needs
- ✅ Experiment freely
- ❌ Don't share outside Zendesk
- ❌ Don't use for personal/side projects

### "What if I break something?"

In your fork, you can always:
```bash
# Reset to match main repo
git fetch upstream
git reset --hard upstream/main
git push origin main --force
```

Then re-run setup: `./setup_for_new_user.sh`

### "Can I create private custom queries for my own use?"

Yes! In your fork:
```bash
mkdir queries/my_private_analysis
vim queries/my_private_analysis/custom_query.sql
# These stay in YOUR fork only, for your personal use
```

These are for YOUR use only. If you think the analysis would benefit the team, request Dioney to create an official shared version.

## 🎯 Summary

### Your Fork = Your Workspace
- Personal configs
- Custom queries
- Experiments
- Local changes

### Main Repo = Team Resource
- Shared reports
- Core infrastructure
- Official releases
- Maintained by Dioney

### Contributing = Sharing Back
- Open PR when you build something useful
- Dioney reviews and merges
- Everyone benefits!

---

**Questions?** Contact Dioney Blanco

**Happy contributing!** 🚀
