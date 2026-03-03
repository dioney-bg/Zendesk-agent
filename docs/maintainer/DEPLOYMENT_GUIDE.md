# 🚀 GitHub Deployment Guide

**For: Dioney Blanco (Maintainer)**

This guide walks you through deploying the Sales Strategy Reporting Agent to GitHub so your team can fork and use it.

---

## ✅ Pre-Deployment Checklist

Before pushing to GitHub, verify:

- [ ] All sensitive data removed (credentials, tokens, personal configs)
- [ ] `.gitignore` is comprehensive
- [ ] All scripts are executable
- [ ] Documentation is complete
- [ ] Setup script tested
- [ ] Sample reports work

### Quick Validation

```bash
# Check for sensitive data
grep -r "password\|secret\|token" config/ --exclude="*.example"

# Validate .gitignore
git status

# Test setup
./validate_setup.sh
```

---

## 📤 Step 1: Create GitHub Repository

### Option A: GitHub.com (Web)

1. Go to https://github.com/new
2. **Repository name:** `Zendesk-agent` (or your preference)
3. **Description:** "Sales Strategy Reporting Agent for Zendesk"
4. **Visibility:**
   - ✅ **Private** (recommended - keeps internal)
   - OR **Internal** (if your org has this option)
5. **Initialize:**
   - ❌ Do NOT add README (you have one)
   - ❌ Do NOT add .gitignore (you have one)
   - ❌ Do NOT add license
6. Click **"Create repository"**

### Option B: GitHub CLI

```bash
# Install GitHub CLI (if not installed)
brew install gh

# Authenticate
gh auth login

# Create private repository
gh repo create Zendesk-agent --private --source=. --remote=origin
```

---

## 📦 Step 2: Prepare Repository

### Initialize Git (if not already)

```bash
cd /Users/dioney.blanco/Zendesk-agent

# Check if already initialized
git status

# If not initialized:
git init
git branch -M main
```

### Replace README.md with GitHub Version

```bash
# Backup current README
mv README.md README_INTERNAL.md

# Use GitHub-focused README
mv GITHUB_README.md README.md

# Or keep both and link them
# (README.md for GitHub, README_INTERNAL.md for detailed docs)
```

### Add Remote

```bash
# Replace YOUR-USERNAME with your GitHub username
git remote add origin https://github.com/YOUR-USERNAME/Zendesk-agent.git

# Verify
git remote -v
```

---

## 🔒 Step 3: Security Check

### Review What Will Be Committed

```bash
git add .
git status

# Look for anything that shouldn't be committed:
# ❌ Credentials files
# ❌ Token files
# ❌ Personal configs
# ❌ Large output files
```

### Check .gitignore

```bash
cat .gitignore

# Verify these are ignored:
# - venv/
# - config/google_credentials.json
# - config/token.json
# - .env
# - outputs/reports/*.csv
# - outputs/reports/*.xlsx
# - outputs/logs/*.log
```

### Test Ignore Rules

```bash
# Create test files that should be ignored
touch .env
touch config/google_credentials.json
touch outputs/reports/test.csv

# Check they're ignored
git status

# They should NOT appear in untracked files
# Clean up test files
rm .env config/google_credentials.json outputs/reports/test.csv
```

---

## 📝 Step 4: Commit and Push

### First Commit

```bash
# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit: Sales Strategy Reporting Agent

- Modular reporting framework
- AI Penetration Report (active)
- Snowflake integration via CLI
- Google Drive upload support
- Team fork workflow
- Comprehensive documentation"

# Push to GitHub
git push -u origin main
```

---

## 🔧 Step 5: Configure Repository Settings

### On GitHub.com

1. Go to your repository
2. Click **"Settings"**

#### General Settings

- **Features:**
  - ✅ Wikis (optional)
  - ✅ Issues
  - ❌ Projects (unless you want)
  - ❌ Discussions (unless you want)

- **Pull Requests:**
  - ✅ Allow squash merging
  - ✅ Allow merge commits
  - ✅ Automatically delete head branches

#### Branch Protection (Important!)

1. Go to **Settings** → **Branches**
2. Click **"Add rule"**
3. **Branch name pattern:** `main`
4. Check:
   - ✅ **Require pull request reviews before merging**
   - ✅ **Dismiss stale pull request approvals**
   - ❌ Require status checks (unless you set up CI)
   - ❌ Require branches to be up to date (can cause issues)
5. Click **"Create"** or **"Save changes"**

**Why?** This prevents you (and team members) from accidentally pushing directly to main.

#### Collaborators (If Private Repo)

1. Go to **Settings** → **Collaborators**
2. Click **"Add people"**
3. Add team members who need **read access**
4. Select **"Read"** permission (they can fork, but not push directly)

---

## 👥 Step 6: Inform Your Team

### Announcement Template

Send this to your team (via Slack, email, etc.):

```markdown
🎉 **New Tool: Sales Strategy Reporting Agent**

Hey team! I've built an automated reporting agent for our Snowflake data.

**What it does:**
- 🤖 Generates AI Penetration reports automatically
- 📊 Exports to CSV, Excel, Slack
- 🔍 Lets you run custom SQL queries
- 📚 More reports coming soon!

**How to get started:**
1. Fork the repo: https://github.com/YOUR-USERNAME/Zendesk-agent
2. Clone your fork to your laptop
3. Run the setup script: `./setup_for_new_user.sh`
4. That's it!

**Documentation:**
- Setup Guide: TEAM_SETUP.md
- Quick Reference: docs/QUICK_REFERENCE.md
- Contributing: CONTRIBUTING.md

**Questions?**
- Open an issue on GitHub
- Slack me
- Check the docs

This is YOUR copy - customize it freely! If you build something useful, contribute it back via Pull Request.

Happy reporting! 📊
```

---

## 📚 Step 7: Documentation for Your Team

### Essential Documents (Already Created)

- ✅ **TEAM_SETUP.md** - First thing team should read
- ✅ **README.md** - Overview on GitHub
- ✅ **CONTRIBUTING.md** - Fork workflow and PR guidelines
- ✅ **docs/QUICK_REFERENCE.md** - Common commands
- ✅ **docs/PROJECT_OVERVIEW.md** - Architecture details

### Create Wiki (Optional)

1. Go to repository → **Wiki**
2. Create pages:
   - **Home** - Link to TEAM_SETUP.md
   - **FAQ** - Common questions
   - **Changelog** - Track updates
   - **Troubleshooting** - Common issues

---

## 🔄 Step 8: Ongoing Maintenance

### When You Add Features

```bash
# Create a branch
git checkout -b feature/new-report

# Make changes, test
python scripts/reports/new_report.py

# Commit
git add scripts/reports/new_report.py
git commit -m "Add new report"

# Push to GitHub
git push origin feature/new-report

# Create PR, review, merge to main
```

### When Team Members Submit PRs

1. **Review the code**
   - Does it work?
   - Is it well-documented?
   - No security issues?

2. **Test locally**
   ```bash
   # Fetch PR
   gh pr checkout PR_NUMBER

   # Test the report
   python scripts/reports/their_report.py
   ```

3. **Provide feedback or merge**
   - Comment on PR
   - Request changes
   - Or approve and merge

4. **Announce new features**
   - Let team know in Slack
   - They can sync their forks

### Versioning (Optional)

Use tags for major releases:

```bash
git tag -a v1.0.0 -m "Initial release with AI Penetration Report"
git push origin v1.0.0

git tag -a v1.1.0 -m "Added Account Health Report"
git push origin v1.1.0
```

---

## 🚨 Troubleshooting

### "Team member pushed directly to main"

If branch protection isn't set up properly:

```bash
# Revert if needed
git revert COMMIT_HASH
git push origin main

# Then set up branch protection (see Step 5)
```

### "Someone committed credentials"

**Act fast:**

```bash
# Remove from history (if just pushed)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config/secrets.json" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all

# Tell team member to:
1. Delete their fork
2. Re-fork
3. Re-setup
```

**Better:** Set up `.gitignore` properly from the start (already done).

### "Fork is out of sync"

Team member asks how to sync:

```bash
# In their local repo
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

Or use GitHub's "Sync fork" button.

---

## ✅ Post-Deployment Checklist

After pushing to GitHub:

- [ ] Repository is private/internal
- [ ] Branch protection is enabled
- [ ] README.md looks good on GitHub
- [ ] Team members have read access
- [ ] Issues and PRs are enabled
- [ ] PR template is working
- [ ] Issue templates are working
- [ ] Announced to team with instructions
- [ ] First team member successfully forked and set up
- [ ] You can receive PRs from team

---

## 📞 Team Support

### Where Team Members Get Help

1. **Documentation:** TEAM_SETUP.md, docs/
2. **Validation:** `./validate_setup.sh`
3. **Issues:** GitHub Issues
4. **Direct:** Slack or email to you

### Your Responsibilities as Maintainer

- ✅ Review PRs within 1-2 days
- ✅ Respond to issues
- ✅ Keep docs updated
- ✅ Add new reports as needed
- ✅ Announce updates to team
- ✅ Help team members with setup

### Time Investment

- **Initial:** 30 min (pushing to GitHub, configuring)
- **Ongoing:** ~1 hour/week (reviewing PRs, adding features)
- **Support:** As needed (hopefully minimal with good docs)

---

## 🎓 Best Practices

### For You (Maintainer)

1. **Always use branches** for new features
2. **Test thoroughly** before merging
3. **Write clear commit messages**
4. **Update docs** when adding features
5. **Announce changes** to team
6. **Review PRs promptly**

### For Team Members (Remind Them)

1. **Fork, don't clone** the main repo
2. **Sync regularly** to get updates
3. **Test before submitting** PRs
4. **Document** new features
5. **Ask questions** via issues

---

## 🎉 Success Metrics

You'll know this is working when:

- ✅ Team members successfully generate reports
- ✅ You receive useful PRs
- ✅ Issues are thoughtful and actionable
- ✅ Team creates custom reports in their forks
- ✅ You spend less time manually generating reports
- ✅ Team has self-service analytics

---

## 📨 Template Messages

### To Team Member Who Just Forked

```markdown
Great! You've forked the repo. Next steps:

1. Clone YOUR fork:
   `git clone https://github.com/YOUR-USERNAME/Zendesk-agent.git`

2. Run setup:
   `cd Zendesk-agent && ./setup_for_new_user.sh`

3. Generate your first report:
   `python scripts/reports/ai_penetration.py`

Need help? See TEAM_SETUP.md or ping me!
```

### When Merging a PR

```markdown
Merged! 🎉

Thanks for contributing! This feature is now in the main repo.

To get this in your fork:
1. Go to your fork on GitHub
2. Click "Sync fork"
3. Pull changes: `git pull origin main`

Great work!
```

---

**You're all set!** 🚀

Your team can now fork, use, and contribute to the Sales Strategy Reporting Agent.

**Questions?** Check this guide or the team documentation.

---

**Last Updated:** March 2026
**Maintainer:** Dioney Blanco
