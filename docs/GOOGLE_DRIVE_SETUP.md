# Google Drive Setup Guide

Follow these steps to set up Google Drive integration for automated report uploads.

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

## Security Notes

- ✅ `google_credentials.json` and `token.json` are in `.gitignore`
- ✅ Never commit these files to version control
- ✅ OAuth tokens are stored locally and encrypted
- ✅ Only you have access to files uploaded by this app

## Next Steps

Once authenticated, you can:

1. **Manual upload:**
   ```bash
   python scripts/google_drive_uploader.py
   ```

2. **Full pipeline (generate + upload):**
   ```bash
   python scripts/run_report_pipeline.py
   ```

3. **Skip upload (local only):**
   ```bash
   python scripts/run_report_pipeline.py --no-drive
   ```

## Folder Structure in Google Drive

The script will create this structure:

```
My Drive/
└── Zendesk AI Reports/
    ├── ai_penetration_report_20260303_100000.csv
    ├── ai_penetration_report_20260303_100000.xlsx
    └── ... (timestamped reports)
```

You can organize into subfolders manually if needed. The script will always use the main "Zendesk AI Reports" folder.

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
