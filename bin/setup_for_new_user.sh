#!/bin/bash

# Sales Strategy Reporting Agent - New User Setup
# Interactive setup script for team members

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "════════════════════════════════════════════════════════════════"
echo "   📊 Sales Strategy Reporting Agent - Team Member Setup"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This script will set up your personal environment."
echo "Estimated time: 10-15 minutes"
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
echo "Step 1: Checking Prerequisites"
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

# Check Git
print_status "Checking Git installation..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    print_success "Git found: $GIT_VERSION"
else
    print_error "Git not found. Please install Git."
    exit 1
fi

# Check Snowflake CLI
print_status "Checking Snowflake CLI..."
SNOW_CLI="/Applications/SnowflakeCLI.app/Contents/MacOS/snow"
if [ -f "$SNOW_CLI" ]; then
    print_success "Snowflake CLI found"
else
    print_warning "Snowflake CLI not found at expected location."
    read -p "Enter path to your Snowflake CLI (or press Enter to skip): " CUSTOM_SNOW_PATH
    if [ ! -z "$CUSTOM_SNOW_PATH" ]; then
        SNOW_CLI="$CUSTOM_SNOW_PATH"
    else
        print_error "Snowflake CLI is required. Please install from:"
        echo "https://docs.snowflake.com/en/user-guide/snowsql-install-config"
        exit 1
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 2: Creating Virtual Environment"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ -d "venv" ]; then
    print_warning "Virtual environment already exists."
    read -p "Recreate it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        print_status "Creating new virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
else
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 3: Installing Dependencies"
echo "════════════════════════════════════════════════════════════════"
echo ""

print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

print_status "Installing Python packages (this may take a few minutes)..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
print_success "Dependencies installed"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 4: Configuring Snowflake Connection"
echo "════════════════════════════════════════════════════════════════"
echo ""

print_status "Let's set up your Snowflake connection..."
echo ""

# Get user inputs
read -p "What is your Snowflake connection name? [default: zendesk]: " CONN_NAME
CONN_NAME=${CONN_NAME:-zendesk}

read -p "What warehouse do you have access to? [default: COEFFICIENT_WH]: " WAREHOUSE
WAREHOUSE=${WAREHOUSE:-COEFFICIENT_WH}

# Update config.yaml
print_status "Updating configuration..."
cat > config/config.yaml.tmp << EOF
# Sales Strategy Reporting Agent - Configuration
# User: $(whoami)
# Setup Date: $(date)

# Snowflake Connection
snowflake:
  connection_name: $CONN_NAME
  account: ZENDESK-GLOBAL
  warehouse: $WAREHOUSE
  default_database: PRESENTATION
  default_schema: CUSTOMER_EXPERIENCE

$(tail -n +10 config/config.yaml)
EOF

mv config/config.yaml.tmp config/config.yaml
print_success "Configuration updated"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 5: Testing Snowflake Connection"
echo "════════════════════════════════════════════════════════════════"
echo ""

print_status "Checking if you're already authenticated..."
if $SNOW_CLI sql -q "SELECT CURRENT_USER()" 2>/dev/null | grep -q "@"; then
    CURRENT_USER=$($SNOW_CLI sql -q "SELECT CURRENT_USER()" 2>/dev/null | grep "@")
    print_success "Already authenticated as: $CURRENT_USER"
else
    print_warning "Not authenticated with Snowflake."
    echo ""
    echo "Opening browser for authentication..."
    echo "Please complete the authentication in your browser."
    echo ""
    $SNOW_CLI login
fi

# Test connection
print_status "Testing connection..."
if $SNOW_CLI sql -q "SELECT CURRENT_DATE()" > /dev/null 2>&1; then
    print_success "Snowflake connection works!"
else
    print_error "Snowflake connection test failed."
    echo ""
    echo "Please check:"
    echo "  1. You completed authentication"
    echo "  2. You have access to warehouse: $WAREHOUSE"
    echo "  3. Your account has necessary permissions"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 6: Creating Output Directories"
echo "════════════════════════════════════════════════════════════════"
echo ""

print_status "Setting up directories..."
mkdir -p outputs/reports/ai_penetration
mkdir -p outputs/data
mkdir -p outputs/logs
print_success "Directories created"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 7: Generating Your First Report (Optional)"
echo "════════════════════════════════════════════════════════════════"
echo ""

read -p "Generate a test AI Penetration Report now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Generating AI Penetration Report..."
    echo ""
    python scripts/reports/ai_penetration.py
    echo ""
    print_success "Report generated! Check outputs/reports/ai_penetration/"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Setup Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 What you can do now:"
echo ""
echo "  1. Generate reports:"
echo "     source venv/bin/activate"
echo "     python scripts/reports/ai_penetration.py"
echo ""
echo "  2. Run interactive menu:"
echo "     ./run_agent.sh"
echo ""
echo "  3. View documentation:"
echo "     cat README.md"
echo "     cat docs/QUICK_REFERENCE.md"
echo ""
echo "  4. Check your configuration:"
echo "     cat config/config.yaml"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📚 Helpful Resources:"
echo ""
echo "  • Team Setup Guide: docs/setup/TEAM_SETUP.md"
echo "  • Quick Reference:  docs/QUICK_REFERENCE.md"
echo "  • Project Overview: docs/PROJECT_OVERVIEW.md"
echo ""
echo "❓ Need Help?"
echo "  • Check logs: tail -f outputs/logs/sales_strategy_agent.log"
echo "  • Contact: Dioney Blanco"
echo ""
echo "Happy reporting! 📊"
echo "════════════════════════════════════════════════════════════════"
