# Test Environment Setup Guide

## ⚡ Quick Reference Card

**Status:** ✅ Test environment is SET UP and ready to use

**Commands:**
```bash
strategy-agent        # Production (blue banner)
strategy-agent-test   # Test (yellow banner)
```

**Locations:**
```bash
~/Zendesk-agent/       # Production (main branch)
~/Zendesk-agent-test/  # Test (test-vX.X branch)
```

**Daily Workflow:**
1. Edit files in `~/Zendesk-agent-test/`
2. Test with `strategy-agent-test`
3. When ready: `cd ~/Zendesk-agent && git merge test-vX.X && git push`

---

## 📊 Test Strategy-Agent: Options & Recommendations

This guide covers how to set up a test environment for the Sales Strategy Agent.

---

## Current Architecture

**Main Components:**
1. **CLAUDE.md** (instructions) - In repo: `/Users/dioney.blanco/Zendesk-agent/`
2. **Auto-memory** - Outside repo: `/Users/dioney.blanco/.claude/projects/-Users-dioney-blanco-Zendesk-agent/memory/`
   - MEMORY.md, product-filtering.md, leader-filtering.md, etc.
3. **queries/** (SQL files) - In repo
4. **bin/strategy-agent** (launcher) - In repo

**Key Insight:** Auto-memory path is tied to repo location, so different directories = different auto-memory (automatic isolation).

---

## 🎯 Option 1: Git Branch + Separate Test Directory (RECOMMENDED)

**How it works:**
```bash
Production:
/Users/dioney.blanco/Zendesk-agent/                    (main branch)
└── Auto-memory: ~/.claude/projects/-Users-...-Zendesk-agent/memory/

Test:
/Users/dioney.blanco/Zendesk-agent-test/               (test branch)
└── Auto-memory: ~/.claude/projects/-Users-...-Zendesk-agent-test/memory/
```

**Implementation:**
```bash
# One-time setup
cd ~
git clone ~/Zendesk-agent Zendesk-agent-test
cd Zendesk-agent-test
git checkout -b test-v1.3

# Create test launcher
cp bin/strategy-agent bin/strategy-agent-test
# Update launcher to show "TEST MODE" in banner

# Make changes in test repo
# Test thoroughly
# When ready, merge to main
cd ~/Zendesk-agent
git merge test-v1.3

# Push to origin
git push origin main
```

**Pros:**
- ✅ Complete isolation (separate auto-memory, separate repo directory)
- ✅ Git manages versions properly
- ✅ Production unaffected by test changes
- ✅ Easy to port changes (git merge)
- ✅ Can test as long as needed before promoting

**Cons:**
- ⚠️ Need to maintain two directories on disk (~200MB each)
- ⚠️ Need to manually sync changes (git merge)

**Best for:** You (maintainer) who needs frequent testing

---

## 🎯 Option 2: Git Branches Only (Simpler but Risky)

**How it works:**
```bash
# Same repo, switch branches
cd ~/Zendesk-agent
git checkout -b test-v1.3

# Make changes
# Test with SAME auto-memory

# When ready
git checkout main
git merge test-v1.3
```

**Pros:**
- ✅ Simple git workflow
- ✅ One directory on disk
- ✅ Standard software practice

**Cons:**
- ❌ **Shares auto-memory with production** (test pollution!)
- ❌ Test changes affect production agent
- ❌ Can't run production agent while testing

**Best for:** Quick experiments, not major refactoring

---

## 🎯 Option 3: Separate Test Repo (Maximum Isolation)

**How it works:**
```bash
cd ~
mkdir Zendesk-agent-test
cd Zendesk-agent-test
git init
git remote add origin <github-url>
git fetch
git checkout -b test-main

# Completely independent repo
```

**Pros:**
- ✅ Complete isolation (separate git history, auto-memory, everything)
- ✅ Can diverge significantly without affecting production
- ✅ Good for experimental features

**Cons:**
- ❌ Harder to port changes (manual copy or cherry-pick)
- ❌ Two separate git histories to manage
- ❌ Risk of drift between test and production

**Best for:** Major architectural changes or long-term experiments

---

## 📋 Recommendation: Option 1 (Git Branch + Separate Directory)

**Why this is best for you:**

1. **Complete Isolation**
   - Test auto-memory separate from production
   - Can break things in test without affecting production
   - Team's production agents unaffected

2. **Git Best Practices**
   - Use branches for features/tests
   - Merge when ready
   - Full version control

3. **Clear Testing Process**
   - Make changes in test directory
   - Test with separate auto-memory
   - When 100% sure → merge to main
   - Team pulls latest changes

4. **Maintainable**
   - Standard git workflow
   - No duplicate files
   - Clear separation between test and prod

---

## 🚀 Implementation Guide

### Initial Setup (✅ COMPLETED)

```bash
# 1. Create test directory
cd ~/
git clone Zendesk-agent Zendesk-agent-test

# 2. Create test branch (replace X.X with next version number)
cd Zendesk-agent-test
git checkout -b test-vX.X

# 3. Modify launcher to show TEST MODE
# Change banner color to YELLOW and add "🧪 TEST MODE"
# Edit: bin/strategy-agent

# 4. Commit the banner change
git add bin/strategy-agent
git commit -m "TEST: Update launcher banner to show TEST MODE"

# 5. Create test command alias
echo 'alias strategy-agent-test="cd ~/Zendesk-agent-test && bin/strategy-agent"' >> ~/.zshrc
source ~/.zshrc
```

**Current Setup:**
- ✅ Production: `~/Zendesk-agent/` (main branch)
- ✅ Test: `~/Zendesk-agent-test/` (test-v1.5 branch)
- ✅ Alias: `strategy-agent-test` command available

### Regular Workflow (Daily Use)

**1. Make Changes in Test:**
```bash
cd ~/Zendesk-agent-test

# Make changes to CLAUDE.md, MEMORY.md, queries, etc.
# Save and commit
git add -A
git commit -m "TEST: Description of changes"
```

**2. Test Your Changes:**
```bash
strategy-agent-test
# Agent opens with yellow banner "🧪 TEST MODE"
# Run queries, verify behavior
# Test thoroughly before promoting
```

**3. Promote to Production (when ready):**
```bash
cd ~/Zendesk-agent
git checkout main
git merge test-vX.X  # Replace X.X with your test branch name
git push origin main

# Team members auto-update next time they run strategy-agent
```

**4. Start New Test Cycle (optional):**
```bash
cd ~/Zendesk-agent-test
git checkout main
git pull origin main  # Sync with production
git checkout -b test-vY.Y  # New test branch for next version
```

### What Gets Isolated

**Automatically Separate (by directory):**
- ✅ Auto-memory files (MEMORY.md, product-filtering.md, etc.)
- ✅ Git history/branches
- ✅ Local file changes

**Shared (Both use same):**
- Snowflake connection (same database)
- GitHub remote repository

---

## ⚡ Quick Decision Matrix

| Scenario | Recommended Option |
|----------|-------------------|
| "I want to test new rules without breaking production" | **Option 1** (Separate directory) |
| "Quick experiment for 30 minutes" | **Option 2** (Git branch only) |
| "Complete rewrite of agent logic" | **Option 3** (Separate repo) |
| "Team needs multiple test environments" | **Option 1** + branches |

---

## 🎯 Strong Recommendation

**Use Option 1: Git Branch + Separate Test Directory**

**Setup once:**
```bash
git clone ~/Zendesk-agent ~/Zendesk-agent-test
cd ~/Zendesk-agent-test
git checkout -b test-v1.3
```

**Daily workflow:**
- Make changes in test directory
- Test with test auto-memory
- Merge to main when ready
- Team pulls changes

**This gives you:**
- ✅ Safety (production unaffected)
- ✅ Proper testing (separate auto-memory)
- ✅ Git workflow (branches, merges)
- ✅ Easy promotion (git merge)

**Total cost:** ~200MB disk space for test directory

---

## 📝 Common Scenarios (Quick Copy-Paste)

### Scenario 1: Test a Quick Fix
```bash
cd ~/Zendesk-agent-test
# Edit the file
git add -A && git commit -m "TEST: Quick fix for X"
strategy-agent-test
# Test it
# If good: cd ~/Zendesk-agent && git merge test-vX.X && git push
```

### Scenario 2: Test Major Feature (Take Your Time)
```bash
cd ~/Zendesk-agent-test
# Make multiple changes over days/weeks
git add -A && git commit -m "TEST: Work in progress"
strategy-agent-test
# Keep testing until perfect
# When ready: cd ~/Zendesk-agent && git merge test-vX.X && git push
```

### Scenario 3: Abandon Test and Start Fresh
```bash
cd ~/Zendesk-agent-test
git checkout main
git pull origin main  # Sync with production
git branch -D test-vX.X  # Delete old test branch
git checkout -b test-vY.Y  # Create new test branch
```

### Scenario 4: Check Which Environment You're In
```bash
cd ~/Zendesk-agent-test && git branch  # Shows * test-vX.X
cd ~/Zendesk-agent && git branch       # Shows * main
```

### Scenario 5: See What Changed in Test
```bash
cd ~/Zendesk-agent-test
git diff main  # Shows all changes vs production
```

---

## 🎯 Remember

- **Blue banner** = Production (affects team)
- **Yellow banner** = Test (only affects you)
- **Always test before merging** to main
- **Different directories = separate auto-memory** (automatic isolation)
