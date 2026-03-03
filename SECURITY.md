# 🔐 Security Guide

**Important:** This agent is designed for each team member to have **their own credentials**. No shared credentials are used.

---

## 🎯 Security Principles

### 1. Personal Credentials Only

**✅ Each team member has their own:**
- Snowflake authentication (SSO via browser)
- Google Drive OAuth credentials (if using Drive)
- Slack authentication (if using Slack CLI)

**❌ Never share:**
- Your `config/google_credentials.json`
- Your `config/token.json`
- Your Snowflake login
- Your `.env` file

### 2. Fork Workflow Security

**How it protects you:**
- Each person forks the repository (personal copy)
- Personal credentials stay in their fork only
- `.gitignore` prevents accidental commits
- You can't push directly to main repo

---

## 🔒 What's Protected (gitignored)

### Snowflake
```
snowflake/               # Snowflake CLI data
**/snow.toml            # Connection configs
**/snowflake.yml        # Settings
**/.snowsql/            # CLI cache
```

**How it works:**
- Each person authenticates via `snow login`
- Credentials stored locally by Snowflake CLI
- Never in git repository

### Google Drive
```
config/google_credentials.json   # YOUR OAuth client
config/token.json                 # YOUR access token
credentials.json                  # Alt location
token.json                        # Alt location
client_secret*.json              # Downloaded credentials
```

**How it works:**
1. Each person downloads OAuth credentials from Google Cloud Console
2. Saves as `config/google_credentials.json` in THEIR fork
3. First run generates `config/token.json` (personal access token)
4. Both files gitignored - never shared

### Environment Variables
```
.env                    # YOUR personal settings
.env.local             # Local overrides
config/config.yaml.personal
```

### API Keys & Tokens
```
*.key                  # Any key files
*.pem                  # Certificate files
*.token               # Token files
.credentials          # Credential stores
```

---

## ⚠️ Common Security Mistakes

### ❌ Don't Do This

```bash
# DON'T: Commit credentials
git add config/google_credentials.json
git commit -m "Add my credentials"  # BAD!

# DON'T: Share credential files
slack send config/token.json  # BAD!
email config/google_credentials.json  # BAD!

# DON'T: Use git add .
git add .  # Might accidentally add credentials

# DON'T: Disable .gitignore
git add -f config/token.json  # BAD! Forces ignored file
```

### ✅ Do This Instead

```bash
# DO: Let .gitignore protect you
git add scripts/
git add queries/
git commit -m "Add new report"

# DO: Each person sets up their own
# Person A: Downloads their own google_credentials.json
# Person B: Downloads their own google_credentials.json
# Never share between people

# DO: Keep credentials local
# Your credentials stay in YOUR fork only
```

---

## 🔍 Verification

### Check What Will Be Committed

Before any commit:

```bash
# See what git will commit
git status

# If you see these, STOP:
# ❌ config/google_credentials.json
# ❌ config/token.json
# ❌ .env
# ❌ snow.toml

# These should be untracked (not showing in git status)
```

### Validate .gitignore

```bash
# Create test credential file
touch config/google_credentials.json

# Check if it's ignored
git status

# Should NOT appear in "Untracked files"
# Clean up test
rm config/google_credentials.json
```

### Scan for Accidentally Committed Secrets

```bash
# Check if any secrets were committed
git log --all --full-history -- config/google_credentials.json
git log --all --full-history -- config/token.json

# Should return nothing
```

---

## 🛡️ How Each Service Handles Security

### Snowflake

**Authentication Method:** SSO via browser

**Where credentials stored:**
- Managed by Snowflake CLI
- In `~/.snowsql/` (outside repository)
- Uses your Zendesk SSO

**Setup per person:**
```bash
/Applications/SnowflakeCLI.app/Contents/MacOS/snow login
# Opens browser → Zendesk SSO → Authenticates
# Credentials stored in ~/.snowsql/ (not in repo)
```

**Security:**
✅ Each person uses their own Zendesk account
✅ SSO authentication (no passwords in code)
✅ Session tokens managed by Snowflake
✅ IT can see who ran what queries

### Google Drive

**Authentication Method:** OAuth 2.0

**Where credentials stored:**
- `config/google_credentials.json` - OAuth client (from Google Cloud)
- `config/token.json` - Your personal access token (auto-generated)
- Both in your fork only (gitignored)

**Setup per person:**
1. Each person goes to Google Cloud Console
2. Creates/downloads OAuth credentials
3. Saves to their local `config/google_credentials.json`
4. Runs authentication (generates `token.json`)
5. Both files stay local, never committed

**Security:**
✅ Each person has their own Google Cloud project (optional)
✅ OR shares organization project but gets own token
✅ OAuth flow ensures no password sharing
✅ Token refresh handled automatically
✅ Can revoke access anytime

**IMPORTANT:** Two options for Google Drive:

**Option A: Shared OAuth Client (Simpler)**
- Dioney creates one OAuth client in Google Cloud
- Shares the `google_credentials.json` file with team (via secure channel)
- Each person authenticates and gets their own `token.json`
- Result: Shared OAuth app, but personal access tokens

**Option B: Personal OAuth Clients (More Secure)**
- Each person creates their own Google Cloud project
- Downloads their own `google_credentials.json`
- Gets their own `token.json`
- Result: Completely isolated credentials

**Recommendation:** Option A is fine for internal team. Option B if paranoid about security.

### Google Drive - Shared Drives (Team Drives)

**NEW: Shared drive support for team collaboration**

**How shared drives work with OAuth:**
- Each person still has their own OAuth credentials (Option A or B above)
- Each person still gets their own personal `token.json`
- The difference: files upload to a centralized shared drive location
- Everyone with shared drive access can see/download the reports

**Shared Drive Permissions Model:**
```
Personal OAuth     Personal Token     Shared Drive Access
    (you)      →      (you)       →   (managed by admin)
                                            ↓
                                      All team can see
```

**Key Points:**
- ✅ Your OAuth credentials are still yours alone
- ✅ Your token is still personal (never shared)
- ✅ Shared drive access is separate (Google Drive permissions)
- ✅ Admin controls who has shared drive access
- ⚠️ Files uploaded to shared drive are visible to all members

**Privacy isolation:**
- You can only upload to folders you have permission to access
- You can't access other team members' personal OAuth tokens
- Your authentication is separate from file sharing permissions
- Shared drive membership ≠ shared OAuth credentials

**Configuration:**
```yaml
google_drive:
  use_shared_drive: true              # Enable shared drive mode
  shared_drive_name: "SalesStrategy"  # Name of the shared drive
  target_folder_name: "Strategy-agent" # Folder for uploads
```

**To enable:**
1. Admin adds you to "SalesStrategy" shared drive
2. You run `make setup-drive` (creates YOUR credentials)
3. You authenticate with YOUR Google account
4. Your reports upload to shared location
5. Everyone with shared drive access can see the reports

**Security considerations:**
- ✅ Each person's OAuth setup is independent
- ✅ No shared tokens between team members
- ✅ Shared drive access controlled by Google Drive admin
- ⚠️ Reports in shared drive are visible to all members
- ⚠️ Make sure you trust everyone with shared drive access

### Slack

**Authentication Method:** OAuth or CLI auth

**Where credentials stored:**
- `~/.slack/credentials.json` (outside repository)

**Setup per person:**
```bash
slack login
# Authenticates via browser
# Credentials stored in ~/.slack/ (not in repo)
```

**Security:**
✅ Personal Slack authentication
✅ Stored outside repository
✅ Can revoke anytime via Slack settings

---

## 🚨 If Credentials Are Accidentally Committed

### Immediate Actions

**1. Remove from history (if just pushed):**
```bash
# Remove file from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config/google_credentials.json" \
  --prune-empty --tag-name-filter cat -- --all

# Force push to your fork
git push origin --force --all
```

**2. Revoke the credentials:**
- **Google Drive:** Go to Google Cloud Console → Credentials → Delete OAuth client
- **Snowflake:** Change password / revoke session
- **Slack:** Revoke app authorization

**3. Create new credentials:**
- Download new OAuth credentials
- Re-authenticate
- Never commit again

### Prevention

**Use pre-commit hooks (optional):**

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check for credential files
if git diff --cached --name-only | grep -E "credentials|token|\.env"; then
    echo "❌ Error: Attempting to commit credentials!"
    echo "Files blocked:"
    git diff --cached --name-only | grep -E "credentials|token|\.env"
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## ✅ Security Checklist

### For Team Members (Setting Up)

- [ ] Forked the repository (not cloned main repo directly)
- [ ] Ran `./setup_for_new_user.sh`
- [ ] Authenticated with Snowflake using YOUR account
- [ ] (Optional) Set up Google Drive with YOUR credentials
- [ ] Verified `config/google_credentials.json` is not in git status
- [ ] Verified `config/token.json` is not in git status
- [ ] Never shared credential files with anyone

### For Dioney (Maintaining)

- [ ] Branch protection enabled (require PR reviews)
- [ ] `.gitignore` comprehensive (all credential patterns)
- [ ] No credentials in repository history
- [ ] Team knows to use personal credentials
- [ ] Review PRs for accidental credential commits
- [ ] Team knows to never use `git add .` carelessly

---

## 📋 What If Someone Asks For Your Credentials?

### ❌ Never Share

- Your `config/google_credentials.json`
- Your `config/token.json`
- Your `.env` file
- Your Snowflake password
- Your Slack tokens

### ✅ Share Instead

- How to set up their own (point to `TEAM_SETUP.md`)
- How to create their own Google OAuth credentials
- The public documentation
- The setup scripts

---

## 🎓 Best Practices Summary

1. **Personal Credentials**
   - Each person sets up their own
   - Never share credential files
   - Use fork workflow (not direct clones)

2. **Trust .gitignore**
   - Comprehensive patterns already set
   - Prevents accidents
   - Review before any `git add`

3. **Verify Before Commit**
   - Run `git status` before committing
   - Look for credential files
   - If you see any, DON'T commit

4. **Use Secure Channels**
   - If sharing OAuth client (Option A), use Slack DM or email
   - Never commit to repository
   - Never post in public channels

5. **Audit Regularly**
   - Check repository history for leaks
   - Review `.gitignore` updates
   - Ensure team follows practices

---

## 🆘 Questions?

**Q: Can I share the OAuth client credentials (`google_credentials.json`)?**
A: With team members only, via secure channel (Slack DM). They still get their own `token.json`. OR better: each person creates their own.

**Q: What if I accidentally committed credentials?**
A: Follow "If Credentials Are Accidentally Committed" section above. Act fast!

**Q: How do I know my credentials are safe?**
A: Run `git status`. If credential files don't appear, they're gitignored (safe).

**Q: Can I use the same Google account as someone else?**
A: No. Each person authenticates with their own Google account. Shared OAuth client is OK, but personal tokens are unique.

**Q: Should we create one Google Cloud project or multiple?**
A: One is fine for internal team (Dioney creates, shares OAuth client). Multiple is more secure but more admin work.

---

## 📞 Security Contact

**For security issues or questions:**
- **Maintainer:** Dioney Blanco
- **Type:** Open a private issue on GitHub
- **Urgent:** Slack DM

**If you discover a security vulnerability:**
1. Don't open a public issue
2. Contact Dioney directly
3. Include details of the vulnerability
4. We'll fix and notify team

---

**Security is everyone's responsibility!**

Follow these guidelines and your credentials stay safe.

---

**Last Updated:** March 2026
**Maintainer:** Dioney Blanco
