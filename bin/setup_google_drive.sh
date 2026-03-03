#!/bin/bash

# Sales Strategy Reporting Agent - Google Drive Setup
# Interactive setup for Google Drive shared drive integration

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "════════════════════════════════════════════════════════════════"
echo "   📊 Google Drive Setup - Sales Strategy Reporting Agent"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This script will set up your personal Google Drive connection."
echo "Estimated time: 15-20 minutes"
echo ""
echo "You will need:"
echo "  • Access to Google Cloud Console"
echo "  • Access to SalesStrategy shared drive"
echo "  • ~15 minutes for OAuth client setup"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Ask for confirmation to continue
read -p "Ready to start? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 1: Prerequisites"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check Python
print_status "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check virtual environment
print_status "Checking virtual environment..."
if [ -d "venv" ]; then
    print_success "Virtual environment found"
else
    print_error "Virtual environment not found."
    echo ""
    echo "Please run: make setup"
    echo "Or: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Check config directory
print_status "Checking config directory..."
if [ -d "config" ]; then
    print_success "Config directory found"
else
    print_error "Config directory not found. Are you in the project root?"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 2: Create Google Cloud OAuth Client"
echo "════════════════════════════════════════════════════════════════"
echo ""

print_warning "IMPORTANT: You need to create your own OAuth 2.0 Client ID"
echo ""
echo "This ensures maximum privacy - your credentials are yours alone."
echo ""
echo "Follow these steps:"
echo ""
echo "1. Go to: https://console.cloud.google.com/"
echo "2. Create a new project (or select existing)"
echo "   Name: 'Sales Strategy Agent - [Your Name]'"
echo ""
echo "3. Enable Google Drive API:"
echo "   • Search for 'Google Drive API'"
echo "   • Click 'Enable'"
echo ""
echo "4. Configure OAuth Consent Screen:"
echo "   • Go to 'APIs & Services' > 'OAuth consent screen'"
echo "   • User Type: Internal (for Zendesk account)"
echo "   • App name: 'Sales Strategy Agent'"
echo "   • User support email: Your Zendesk email"
echo "   • Scopes: Add 'Google Drive API' scopes"
echo "   • Save and continue"
echo ""
echo "5. Create OAuth 2.0 Credentials:"
echo "   • Go to 'APIs & Services' > 'Credentials'"
echo "   • Click '+ CREATE CREDENTIALS' > 'OAuth client ID'"
echo "   • Application type: 'Desktop app'"
echo "   • Name: 'Sales Strategy CLI'"
echo "   • Click 'Create'"
echo ""
echo "6. Download Credentials:"
echo "   • Click the download icon (⬇) next to your new OAuth client"
echo "   • Save as 'google_credentials.json'"
echo ""

read -p "Press Enter when you've downloaded google_credentials.json..."
echo ""

# Prompt for credentials file location
print_status "Locating credentials file..."
echo ""
echo "Where did you save google_credentials.json?"
read -p "Enter full path (or drag file here): " CREDS_PATH

# Clean up path (remove quotes if dragged)
CREDS_PATH="${CREDS_PATH//\'/}"
CREDS_PATH="${CREDS_PATH//\"/}"

# Check if file exists
if [ ! -f "$CREDS_PATH" ]; then
    print_error "File not found: $CREDS_PATH"
    exit 1
fi

# Validate JSON structure
print_status "Validating credentials file..."
if python3 -c "import json; json.load(open('$CREDS_PATH'))" 2>/dev/null; then
    print_success "Valid JSON format"
else
    print_error "Invalid JSON file. Please download again from Google Cloud Console."
    exit 1
fi

# Copy to config directory
print_status "Installing credentials..."
cp "$CREDS_PATH" config/google_credentials.json
chmod 600 config/google_credentials.json  # Secure permissions
print_success "Credentials installed to config/google_credentials.json"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 3: Authenticate with Google"
echo "════════════════════════════════════════════════════════════════"
echo ""

print_status "Starting OAuth authentication flow..."
echo ""
echo "A browser window will open for you to:"
echo "  1. Select your Zendesk Google account"
echo "  2. Grant permissions to the app"
echo "  3. Allow access to Google Drive"
echo ""
read -p "Press Enter to open browser..."

# Activate venv and run authentication
source venv/bin/activate

print_status "Launching browser for authentication..."

# Create a simple test script to trigger auth
cat > /tmp/test_google_auth.py << 'EOF'
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scripts.core.google_drive_uploader import GoogleDriveUploader

try:
    uploader = GoogleDriveUploader()
    print("\n✅ Authentication successful!")
    print(f"Token saved to: config/token.json")
except Exception as e:
    print(f"\n❌ Authentication failed: {e}")
    sys.exit(1)
EOF

python /tmp/test_google_auth.py

if [ $? -eq 0 ]; then
    print_success "Google authentication completed"
else
    print_error "Authentication failed"
    exit 1
fi

rm /tmp/test_google_auth.py

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 4: Verify Shared Drive Access"
echo "════════════════════════════════════════════════════════════════"
echo ""

print_status "Testing shared drive access..."

# Create test script for shared drive
cat > /tmp/test_shared_drive.py << 'EOF'
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scripts.core.google_drive_uploader import GoogleDriveUploader

try:
    # Test shared drive connection
    uploader = GoogleDriveUploader(shared_drive_name="SalesStrategy")

    if uploader.shared_drive_id:
        print("✅ Successfully connected to SalesStrategy shared drive")

        # Test finding Strategy-agent folder
        folder_id = uploader.get_folder_id("Strategy-agent", create_if_not_exists=False)

        if folder_id:
            print("✅ Found 'Strategy-agent' folder")
        else:
            print("⚠️  'Strategy-agent' folder not found in shared drive")
            print("   The folder will be created on first upload")
    else:
        print("❌ Could not connect to SalesStrategy shared drive")
        print("   Please verify you have access to the shared drive")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

python /tmp/test_shared_drive.py

if [ $? -eq 0 ]; then
    print_success "Shared drive access verified"
else
    print_error "Could not access shared drive"
    echo ""
    echo "Possible issues:"
    echo "  • You don't have access to 'SalesStrategy' shared drive"
    echo "  • Ask admin to add you to the shared drive"
    echo "  • Check drive name in config/config.yaml"
    exit 1
fi

rm /tmp/test_shared_drive.py

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 5: Test Upload"
echo "════════════════════════════════════════════════════════════════"
echo ""

read -p "Would you like to test uploading a file? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Creating test file..."

    # Create test file
    TEST_FILE="/tmp/strategy_agent_test_$(date +%Y%m%d_%H%M%S).txt"
    echo "Test upload from Sales Strategy Agent" > "$TEST_FILE"
    echo "Generated: $(date)" >> "$TEST_FILE"
    echo "User: $(whoami)" >> "$TEST_FILE"

    print_status "Uploading test file..."

    # Create upload test script
    cat > /tmp/test_upload.py << EOF
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scripts.core.google_drive_uploader import GoogleDriveUploader

try:
    uploader = GoogleDriveUploader(shared_drive_name="SalesStrategy")

    # Get Strategy-agent folder
    folder_id = uploader.get_folder_id("Strategy-agent", create_if_not_exists=True)

    if folder_id:
        # Upload test file
        result = uploader.upload_file("$TEST_FILE", folder_id=folder_id)

        if result:
            print("✅ Test upload successful!")
            print(f"   View file: {result['link']}")
        else:
            print("❌ Upload failed")
            sys.exit(1)
    else:
        print("❌ Could not find/create folder")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

    python /tmp/test_upload.py

    if [ $? -eq 0 ]; then
        print_success "Test upload completed"
        echo ""
        print_warning "Note: You can delete the test file from the shared drive"
    else
        print_error "Upload failed"
    fi

    rm /tmp/test_upload.py
    rm "$TEST_FILE"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Google Drive Setup Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 What's been set up:"
echo ""
echo "  ✓ OAuth 2.0 client credentials installed"
echo "  ✓ Authenticated with your Google account"
echo "  ✓ Connected to SalesStrategy shared drive"
echo "  ✓ Access to Strategy-agent folder verified"
echo ""
echo "🔒 Your credentials (personal to you):"
echo "  • config/google_credentials.json - OAuth client ID"
echo "  • config/token.json - Your access token"
echo ""
echo "  ⚠️  NEVER commit these files to git!"
echo "  ⚠️  They are already in .gitignore"
echo ""
echo "📊 Next steps:"
echo ""
echo "  1. Generate a report with Drive upload:"
echo "     make ai-report"
echo ""
echo "  2. Reports will automatically upload to:"
echo "     SalesStrategy / Strategy-agent / [report-type]"
echo ""
echo "  3. To test Drive connection:"
echo "     make test-drive"
echo ""
echo "  4. To validate full setup:"
echo "     make validate"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📚 Helpful Resources:"
echo ""
echo "  • Google Drive docs: docs/GOOGLE_DRIVE_SETUP.md"
echo "  • Troubleshooting:   docs/GOOGLE_DRIVE_SETUP.md#troubleshooting"
echo "  • Security info:     SECURITY.md"
echo ""
echo "❓ Need Help?"
echo "  • Check: tail -f outputs/logs/sales_strategy_agent.log"
echo "  • Contact: Dioney Blanco"
echo ""
echo "Happy reporting! 📊"
echo "════════════════════════════════════════════════════════════════"
