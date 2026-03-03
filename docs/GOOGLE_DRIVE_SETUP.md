# Google Drive Setup Guide

Follow these steps to set up Google Drive integration for automated report uploads.

## 🚀 Quick Start (Recommended)

**For most users, use the automated setup script:**

```bash
make setup-drive
```

This interactive script will:
1. Guide you through OAuth client creation
2. Help you download credentials
3. Run authentication flow
4. Test shared drive access
5. Verify everything works

**Time:** ~15-20 minutes (first time)

Continue reading below for manual setup or troubleshooting.

## 🆕 Shared Drive (Team Drive) vs Personal Drive

**The Sales Strategy Agent supports both Personal Google Drive and Shared Drives (Team Drives).**

### Shared Drive Mode (Recommended for Teams)

**Use this when:**
- You want all reports in one centralized location
- Multiple team members need access to reports
- You want easy collaboration and file sharing
- You have access to a SalesStrategy shared drive

**How it works:**
- Reports upload to **SalesStrategy / Strategy-agent** folder
- Everyone with shared drive access can view/download reports
- Each person still uses their own OAuth credentials
- Configured in `config/config.yaml` with `use_shared_drive: true`

### Personal Drive Mode

**Use this when:**
- You want reports in your personal Google Drive
- You're testing or doing personal analysis
- You don't have access to the shared drive yet
- Configured in `config/config.yaml` with `use_shared_drive: false`

**How it works:**
- Reports upload to **My Drive / Sales Strategy Reports**
- Only you can see these reports
- Still uses your personal OAuth credentials

### Switching Between Modes

Edit `config/config.yaml`:
```yaml
google_drive:
  use_shared_drive: true  # or false for personal drive
  shared_drive_name: "SalesStrategy"
  target_folder_name: "Strategy-agent"
```

---

## 🔑 OAuth Scopes for Shared Drives

**IMPORTANT:** Shared drive access requires the full `drive` scope, not `drive.file`.

**What this means:**
- **Old scope (`drive.file`):** Only access files created by the app
- **New scope (`drive`):** Access all files in your Drive and shared drives

**Security implications:**
- ✅ You control which shared drives you grant access to
- ✅ Your OAuth token is still personal and never shared
- ✅ Each person authenticates with their own Google account
- ⚠️ The app can see/modify files you have access to

**If you previously set up Google Drive:**
1. Delete `config/token.json`
2. Re-run setup script: `make setup-drive`
3. Re-authenticate with the new scope

---

## 🔐 Security First

**IMPORTANT:** Each team member needs **their own Google Drive authentication**. This guide explains two options:

- **Option A (Shared OAuth Client):** Dioney creates OAuth client, team uses their own Google accounts to authenticate
- **Option B (Personal OAuth Clients):** Each person creates their own OAuth client

Both options are secure - you'll have your own `token.json` that **never gets shared or committed to git**.

## Prerequisites

- Google account with access to Google Drive
- Admin rights to create Google Cloud projects (or ask your IT admin)
- **Note:** Your `google_credentials.json` and `token.json` will be **gitignored** (never committed)

## 🎯 Choose Your Setup Option

### Option A: Shared OAuth Client (Recommended for Teams)

**How it works:**
1. **Dioney creates** one OAuth client in Google Cloud
2. **Dioney shares** the `google_credentials.json` file with team (via Slack DM/email - **NOT via git**)
3. **Each person authenticates** using their own Google account
4. **Each person gets** their own `token.json` (personal access token)

**Pros:**
- ✅ One-time setup by Dioney
- ✅ Easy for team (just authenticate)
- ✅ Still secure (personal tokens)

**Cons:**
- ⚠️ Requires secure distribution of OAuth client file

**Security:** Each person still has their own access token. The OAuth client is just the "app" identity.

---

### Option B: Personal OAuth Clients (Maximum Security)

**How it works:**
1. **Each person creates** their own Google Cloud project
2. **Each person downloads** their own `google_credentials.json`
3. **Each person authenticates** and gets their own `token.json`

**Pros:**
- ✅ Completely isolated credentials
- ✅ No sharing of any files
- ✅ Maximum security

**Cons:**
- ⚠️ More setup work per person
- ⚠️ Each person needs Google Cloud access

---

**Recommendation:** Use **Option A** for internal teams. Use **Option B** if you need complete isolation.

---

## Step-by-Step Setup

### For Option A (Shared OAuth Client)

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top
3. Click "New Project"
4. Enter project name: **"Zendesk AI Reports"**
5. Click "Create"

### 2. Enable Required APIs

1. In the left menu, go to **"APIs & Services" > "Library"**
2. Search for and enable:
   - **Google Drive API**
   - **Google Sheets API** (optional, for future features)

### 3. Create OAuth 2.0 Credentials

1. Go to **"APIs & Services" > "Credentials"**
2. Click **"+ CREATE CREDENTIALS"**
3. Select **"OAuth client ID"**
4. If prompted to configure consent screen:
   - Choose **"Internal"** (for Zendesk organization)
   - Fill in:
     - App name: "Zendesk AI Reports"
     - User support email: your email
     - Developer contact: your email
   - Click **"Save and Continue"**
   - Click **"Save and Continue"** on Scopes (leave empty)
   - Click **"Save and Continue"** on Test users
   - Click **"Back to Dashboard"**

5. Back at Create OAuth client ID:
   - Application type: **"Desktop app"**
   - Name: "Zendesk AI Reports CLI"
   - Click **"Create"**

6. Click **"Download JSON"** on the popup
7. Save the file as `google_credentials.json`

### 4. Add Credentials to Project

Move the downloaded file to the config directory:

```bash
mv ~/Downloads/client_secret_*.json /Users/dioney.blanco/Zendesk-agent/config/google_credentials.json
```

Or manually:
1. Open the downloaded JSON file
2. Copy all content
3. Create file: `config/google_credentials.json`
4. Paste the content
5. Save

### 5. Run First Authentication

Activate the virtual environment and run the uploader:

```bash
cd /Users/dioney.blanco/Zendesk-agent
source venv/bin/activate
python scripts/google_drive_uploader.py
```

**What happens:**
1. A browser window will open
2. Sign in with your Zendesk Google account
3. Click **"Allow"** to grant permissions
4. Browser will show "The authentication flow has completed"
5. Return to terminal - authentication is complete!

### 6. Verify Setup

After authentication, you should see:

```
✅ Successfully authenticated with Google Drive
📁 Found folder: Zendesk AI Reports (ID: ...)
✅ Ready to upload files to folder ID: ...
```

The credentials are now saved in `config/token.json` and will be reused automatically.

## Troubleshooting

### "Credentials file not found"
- Make sure `google_credentials.json` is in the `config/` directory
- Check the filename matches exactly

### "Access blocked: This app's request is invalid"
- Make sure you selected "Desktop app" not "Web application"
- Ensure both Drive and Sheets APIs are enabled

### "This app hasn't been verified"
- This is normal for internal apps
- Click "Advanced" → "Go to Zendesk AI Reports (unsafe)"
- This only appears the first time

### Permission Denied
- Contact your IT admin if you can't create Google Cloud projects
- They may need to enable API access for your organization

### Authentication Expired
- Delete `config/token.json`
- Run the uploader script again to re-authenticate

### Shared Drive Issues

#### "Shared drive not found"
**Symptoms:**
- Can't find "SalesStrategy" shared drive
- Script shows "Available drives: None"

**Solutions:**
1. Verify shared drive name in `config/config.yaml` matches exactly
2. Ask admin to add you to the SalesStrategy shared drive
3. Check you're using the correct Google account
4. Make sure you re-authenticated with the `drive` scope (not `drive.file`)

**How to check:**
```bash
make test-drive
# Should show: ✅ Connected to shared drive: SalesStrategy
```

#### "Cannot access Strategy-agent folder"
**Symptoms:**
- Connected to shared drive but can't find folder
- Permission denied on folder access

**Solutions:**
- The folder will be created automatically on first upload
- If it exists, verify you have access permissions
- Check with team if folder was renamed/moved

#### "Old token doesn't work with shared drive"
**Symptoms:**
- Previously worked with personal drive
- Now getting permission errors

**Solution:**
```bash
# Delete old token (had old scope)
rm config/token.json

# Re-authenticate with new scope
make setup-drive
```

#### "Wrong shared drive"
**Symptoms:**
- Connected to wrong shared drive
- Multiple drives with similar names

**Solution:**
- Update exact drive name in `config/config.yaml`
- Drive names are case-sensitive
- Use `make test-drive` to verify

## Security Notes

- ✅ `google_credentials.json` and `token.json` are in `.gitignore`
- ✅ Never commit these files to version control
- ✅ OAuth tokens are stored locally and encrypted
- ✅ Each person uses their own authentication (no shared tokens)

### Shared Drive Permissions Model

**Personal OAuth Client + Personal Token:**
- Each person creates their own OAuth client (or uses shared client via Option A)
- Each person authenticates with their own Google account
- Each person gets their own access token (`token.json`)
- No tokens are shared between team members

**File Access in Shared Drive:**
- Files uploaded to shared drive are accessible to all drive members
- This is controlled by Google Drive sharing settings, not OAuth
- Team members can see files uploaded by others (if they have shared drive access)
- Each person's `token.json` only grants access to what THAT person can access in Google

**Privacy Isolation:**
- Your OAuth credentials = Your personal app identity
- Your token = Your personal access to YOUR Google account
- Sharing OAuth client ≠ sharing file access
- File access determined by shared drive membership (managed by admin)

## Next Steps

Once authenticated, you can:

1. **Test your connection:**
   ```bash
   make test-drive
   ```

2. **Generate AI report (with auto-upload):**
   ```bash
   make ai-report
   ```

3. **Validate full setup:**
   ```bash
   make validate
   ```

4. **Manual test upload:**
   ```bash
   python scripts/core/google_drive_uploader.py
   ```

## Folder Structure in Google Drive

### Shared Drive Mode (Recommended)

```
Shared drives/
└── SalesStrategy/
    └── Strategy-agent/
        ├── ai_penetration_20260303_100000.csv
        ├── ai_penetration_20260303_100000.xlsx
        └── ... (timestamped reports)
```

All team members with shared drive access can view these reports.

### Personal Drive Mode

```
My Drive/
└── Sales Strategy Reports/
    ├── ai_penetration_20260303_100000.csv
    ├── ai_penetration_20260303_100000.xlsx
    └── ... (timestamped reports)
```

Only you can see these reports in your personal drive.

---

## 📤 For Team Members (Option A - Using Shared OAuth Client)

**If Dioney has shared the OAuth client with you:**

### 1. Receive the OAuth Client File

Dioney will send you `google_credentials.json` via:
- Slack DM (secure)
- Email (secure)
- **NOT via GitHub** (never committed)

### 2. Save to Your Config Directory

```bash
# Save the file Dioney sent you
mv ~/Downloads/google_credentials.json config/google_credentials.json

# Verify it's there
ls -la config/google_credentials.json

# ✅ This file is gitignored - will never be committed
```

### 3. Run Authentication

```bash
cd /Users/YOUR-NAME/Zendesk-agent
source venv/bin/activate
python scripts/core/google_drive_uploader.py
```

This will:
1. Open your browser
2. Ask you to sign in with **YOUR Google account**
3. Ask for permissions (Drive access)
4. Generate **YOUR** personal `token.json`

**Important:**
- You sign in with YOUR Google account (not Dioney's)
- You get YOUR own `token.json` (personal access token)
- Your `token.json` stays in YOUR fork only (gitignored)

### 4. Verify Setup

After authentication, you should see:
```
✅ Successfully authenticated with Google Drive
📁 Found folder: Sales Strategy Reports (ID: ...)
✅ Ready to upload files to folder ID: ...
```

Your `config/` directory should now have:
```
config/
├── google_credentials.json  # OAuth client (from Dioney)
└── token.json               # YOUR personal token (auto-generated)
```

Both files are gitignored - safe!

### 5. Test Upload

```bash
# Generate a report with Google Drive upload
python scripts/run_pipeline.py
```

Files will upload to the shared "Sales Strategy Reports" folder in Google Drive.

---

## 🔧 For Team Members (Option B - Personal OAuth Client)

**If you want completely isolated credentials:**

Follow the "Step-by-Step Setup" instructions above (steps 1-7), but:
- Create **your own** Google Cloud project
- Use **your name** in project/app names
- Download **your own** `google_credentials.json`
- Complete authentication (generates **your** `token.json`)

Everything stays in YOUR fork only.

---

## 🔐 Security Summary

### What's Gitignored (Safe)

✅ `config/google_credentials.json` - OAuth client
✅ `config/token.json` - Your personal access token
✅ Both files stay local, never committed

### What Each File Is

**`google_credentials.json` (OAuth Client):**
- The "app" identity
- Safe to share with team (Option A) via secure channel
- Like an app ID - not a password

**`token.json` (Access Token):**
- **YOUR personal access** to YOUR Google account
- Generated during authentication
- **NEVER share this** - it's your Google access
- Stays in your fork only

### Verification

Check what git sees:
```bash
git status

# You should NOT see:
# ❌ config/google_credentials.json
# ❌ config/token.json

# They're gitignored - good!
```

---

## 🔄 Token Refresh

Google tokens expire. Don't worry:

**Automatic refresh:**
- The script automatically refreshes tokens
- No action needed from you
- New token saved to `config/token.json`

**Manual re-authentication (if needed):**
```bash
# If token expires or you have issues
rm config/token.json
python scripts/core/google_drive_uploader.py
# Re-authenticate in browser
```

---

## 🚨 If You Accidentally Commit Credentials

**Never commit these files!** But if you do:

### Immediate Actions

1. **Remove from git:**
   ```bash
   git rm --cached config/google_credentials.json
   git rm --cached config/token.json
   git commit -m "Remove credentials"
   ```

2. **Revoke token:**
   - Go to: https://myaccount.google.com/permissions
   - Find "Zendesk AI Reports"
   - Click "Remove Access"

3. **For OAuth client (if committed):**
   - Ask Dioney to delete and recreate OAuth client
   - Get new `google_credentials.json`

4. **Re-authenticate:**
   ```bash
   python scripts/core/google_drive_uploader.py
   ```

### Prevention

- `.gitignore` already protects you
- Always run `git status` before committing
- Never use `git add .` carelessly
- Use `git add` with specific files

---

## ❓ FAQ

**Q: Is it safe to share the OAuth client (`google_credentials.json`)?**
A: With team members via secure channel (not git), yes. It's like an app ID. But each person still gets their own personal token.

**Q: What's the difference between the two files?**
A:
- `google_credentials.json` = App identity (safe to share with team)
- `token.json` = YOUR Google access (never share!)

**Q: Can two people use the same OAuth client?**
A: Yes (Option A). They each authenticate with their own Google account and get their own personal tokens.

**Q: Which option is more secure?**
A: Option B (personal OAuth clients) is slightly more secure, but Option A is fine for internal teams.

**Q: What if my token expires?**
A: It refreshes automatically. If issues, delete `config/token.json` and re-authenticate.

**Q: Can I see who uploaded what?**
A: Yes! In Google Drive, file metadata shows who uploaded each file.

**Q: Do I need my own Google Cloud project?**
A: Not for Option A (shared). Yes for Option B (personal).

---

## 📞 Need Help?

**Setup issues:**
- Check `SECURITY.md` for security guidelines
- Check logs: `outputs/logs/`
- Contact Dioney

**Permission errors:**
- Re-authenticate: `python scripts/core/google_drive_uploader.py`
- Check you used correct Google account

**Token expired:**
- Delete `config/token.json`
- Re-run authentication

---

**Security is important! Follow these guidelines and your credentials stay safe.**

---

**Last Updated:** March 2026
**Maintainer:** Dioney Blanco
