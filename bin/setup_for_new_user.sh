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

# Check Python (MUST match exact version for consistency)
REQUIRED_PYTHON_VERSION="3.13.5"
print_status "Checking Python installation..."
echo ""
print_status "⚠️  REQUIRED: Python ${REQUIRED_PYTHON_VERSION} (exact match for team consistency)"
echo ""

PYTHON_CMD=""

# First, check if pyenv is available
if command -v pyenv &> /dev/null; then
    print_success "Found pyenv"

    # Check if Python 3.13.5 is already installed in pyenv
    if pyenv versions --bare | grep -q "^${REQUIRED_PYTHON_VERSION}$"; then
        print_success "Python ${REQUIRED_PYTHON_VERSION} already installed via pyenv"
        PYTHON_CMD="$HOME/.pyenv/versions/${REQUIRED_PYTHON_VERSION}/bin/python"
    else
        print_warning "Python ${REQUIRED_PYTHON_VERSION} not found in pyenv"
        echo ""
        read -p "Install Python ${REQUIRED_PYTHON_VERSION} via pyenv automatically? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Installing Python ${REQUIRED_PYTHON_VERSION}..."
            echo "  (This may take 3-5 minutes - downloading and compiling)"
            pyenv install ${REQUIRED_PYTHON_VERSION}
            PYTHON_CMD="$HOME/.pyenv/versions/${REQUIRED_PYTHON_VERSION}/bin/python"
            print_success "Python ${REQUIRED_PYTHON_VERSION} installed!"
        fi
    fi
else
    # pyenv not found - offer to install everything automatically
    print_warning "pyenv not found (best tool for managing Python versions)"
    echo ""
    echo "📦 What we'll install:"
    echo "  1. pyenv (Python version manager via Homebrew)"
    echo "  2. Python ${REQUIRED_PYTHON_VERSION} (via pyenv)"
    echo ""
    echo "Why pyenv? It allows multiple Python versions without conflicts."
    echo ""
    read -p "Install pyenv + Python ${REQUIRED_PYTHON_VERSION} automatically? (y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Install pyenv
        print_status "Installing pyenv via Homebrew..."
        brew install pyenv

        # Add pyenv to shell config
        print_status "Configuring pyenv in ~/.zshrc..."
        if ! grep -q 'PYENV_ROOT' ~/.zshrc; then
            echo '' >> ~/.zshrc
            echo '# pyenv configuration' >> ~/.zshrc
            echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
            echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
            echo 'eval "$(pyenv init -)"' >> ~/.zshrc
        fi

        # Source it for current session
        export PYENV_ROOT="$HOME/.pyenv"
        export PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init -)"

        print_success "pyenv installed and configured"

        # Install Python 3.13.5
        print_status "Installing Python ${REQUIRED_PYTHON_VERSION}..."
        echo "  (This may take 3-5 minutes - downloading and compiling)"
        pyenv install ${REQUIRED_PYTHON_VERSION}
        PYTHON_CMD="$HOME/.pyenv/versions/${REQUIRED_PYTHON_VERSION}/bin/python"
        print_success "Python ${REQUIRED_PYTHON_VERSION} installed!"
    fi
fi

# If automatic installation was declined, check system Python
if [ -z "$PYTHON_CMD" ]; then
    print_status "Checking system Python installations..."

    for cmd in python${REQUIRED_PYTHON_VERSION} python3.13 python3; do
        if command -v $cmd &> /dev/null; then
            ACTUAL_VERSION=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
            if [ "$ACTUAL_VERSION" = "$REQUIRED_PYTHON_VERSION" ]; then
                PYTHON_CMD=$cmd
                print_success "Found matching Python: $cmd ($ACTUAL_VERSION)"
                break
            fi
        fi
    done
fi

# If still not found, show manual instructions
if [ -z "$PYTHON_CMD" ]; then
    print_error "Python ${REQUIRED_PYTHON_VERSION} is required but not found!"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "📥 Manual Installation Options:"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Option 1 (Recommended): Install via pyenv manually"
    echo "  brew install pyenv"
    echo "  echo 'export PYENV_ROOT=\"\$HOME/.pyenv\"' >> ~/.zshrc"
    echo "  echo 'export PATH=\"\$PYENV_ROOT/bin:\$PATH\"' >> ~/.zshrc"
    echo "  echo 'eval \"\$(pyenv init -)\"' >> ~/.zshrc"
    echo "  source ~/.zshrc"
    echo "  pyenv install ${REQUIRED_PYTHON_VERSION}"
    echo ""
    echo "Option 2: Install via Homebrew"
    echo "  brew install python@3.13"
    echo ""
    echo "Then run: make setup"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    exit 1
fi

print_success "✓ Using Python ${REQUIRED_PYTHON_VERSION}"
echo "  Command: $PYTHON_CMD"

# Check Git
print_status "Checking Git installation..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    print_success "Git found: $GIT_VERSION"
else
    print_error "Git not found. Please install Git."
    exit 1
fi

# Check Snowflake CLI (check common paths)
print_status "Checking Snowflake CLI..."
SNOW_CLI=""
COMMON_PATHS=(
    "/opt/homebrew/bin/snow"                           # Homebrew (Apple Silicon)
    "/usr/local/bin/snow"                              # Homebrew (Intel Mac)
    "/Applications/SnowflakeCLI.app/Contents/MacOS/snow"  # GUI installer
    "$HOME/.local/bin/snow"                            # Manual install
)

for path in "${COMMON_PATHS[@]}"; do
    if [ -f "$path" ]; then
        SNOW_CLI="$path"
        print_success "Snowflake CLI found at: $path"
        break
    fi
done

if [ -z "$SNOW_CLI" ]; then
    print_warning "Snowflake CLI not found in common locations."
    echo ""
    echo "Checked paths:"
    for path in "${COMMON_PATHS[@]}"; do
        echo "  - $path"
    done
    echo ""
    echo "📥 To install Snowflake CLI:"
    echo "  brew install snowflake-cli"
    echo ""
    read -p "Or enter custom path (or press Enter to exit): " CUSTOM_SNOW_PATH
    if [ ! -z "$CUSTOM_SNOW_PATH" ] && [ -f "$CUSTOM_SNOW_PATH" ]; then
        SNOW_CLI="$CUSTOM_SNOW_PATH"
        print_success "Using custom path: $SNOW_CLI"
    else
        print_error "Snowflake CLI is required to continue."
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
        print_status "Creating new virtual environment with $PYTHON_CMD..."
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    fi
else
    print_status "Creating new virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
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

print_status "Upgrading pip to latest version..."
python -m pip install --upgrade pip --quiet
print_success "pip upgraded"

print_status "Installing Python packages from requirements.txt..."
echo "  (This may take 3-5 minutes - installing data science libraries)"
if [ -f "requirements.txt" ]; then
    python -m pip install -r requirements.txt --upgrade 2>&1 | grep -v "already satisfied" || true
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Verify critical installations
print_status "Verifying installations..."
if python -c "import pandas, numpy, yaml, openpyxl, matplotlib, snowflake.connector" 2>/dev/null; then
    print_success "All required packages installed correctly"

    # Show versions for troubleshooting
    echo ""
    print_status "Installed versions:"
    python -c "
import pandas, numpy, matplotlib, snowflake.connector
print('  pandas:', pandas.__version__)
print('  numpy:', numpy.__version__)
print('  matplotlib:', matplotlib.__version__)
print('  snowflake-connector:', snowflake.connector.__version__)
    "
else
    print_error "Some critical packages failed to install!"
    echo ""
    echo "Missing packages. Try running manually:"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 4: Configuring Snowflake Connection"
echo "════════════════════════════════════════════════════════════════"
echo ""

print_status "Let's set up your Snowflake connection..."
echo ""
echo "📋 Snowflake Account: ZENDESK-GLOBAL (configured for all team members)"
echo "🔐 Authentication: SSO (browser-based)"
echo ""

# Get user email
read -p "Enter your Zendesk email (e.g., yourname@zendesk.com): " USER_EMAIL

# Validate email format
if [[ ! "$USER_EMAIL" =~ @zendesk\.com$ ]]; then
    print_warning "Email should end with @zendesk.com"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Setup cancelled. Please run again with correct email."
        exit 1
    fi
fi

# Use default warehouse
WAREHOUSE="COEFFICIENT_WH"
echo ""
print_success "Using warehouse: $WAREHOUSE"

# Update config.yaml
print_status "Updating configuration..."
cat > config/config.yaml.tmp << EOF
# Sales Strategy Reporting Agent - Configuration
# User: $USER_EMAIL
# Setup Date: $(date)

# Snowflake Connection
snowflake:
  connection_name: zendesk
  account: ZENDESK-GLOBAL
  user: $USER_EMAIL
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
echo "Step 7: Installing Claude Code (Required for strategy-agent)"
echo "════════════════════════════════════════════════════════════════"
echo ""

if command -v claude &> /dev/null; then
    print_success "Claude Code is already installed!"
else
    print_warning "Claude Code is NOT installed"
    echo ""
    echo "Claude Code is required to use the 'strategy-agent' command."
    echo ""
    echo "📥 To install Claude Code:"
    echo "  brew install anthropics/claude/claude-code"
    echo ""
    echo "Or visit: https://docs.anthropic.com/claude-code"
    echo ""
    read -p "Install Claude Code via Homebrew now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing Claude Code..."
        brew tap anthropics/claude
        brew install claude-code
        print_success "Claude Code installed!"
    else
        print_warning "Skipping Claude Code installation"
        echo "Note: You'll need to install it later to use strategy-agent"
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 8: Installing strategy-agent Command"
echo "════════════════════════════════════════════════════════════════"
echo ""

print_status "Installing strategy-agent globally..."
./bin/install_strategy_agent

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    print_warning "$HOME/.local/bin is not in your PATH"
    echo ""
    echo "Add this to your ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    read -p "Add to ~/.zshrc automatically? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        print_success "Added to ~/.zshrc - restart terminal or run: source ~/.zshrc"
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Step 9: Testing strategy-agent (Optional)"
echo "════════════════════════════════════════════════════════════════"
echo ""

if command -v claude &> /dev/null && command -v strategy-agent &> /dev/null; then
    print_success "Ready to use strategy-agent!"
    echo ""
    read -p "Launch strategy-agent now to test? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Launching strategy-agent..."
        echo ""
        strategy-agent
    fi
else
    print_warning "strategy-agent not ready yet"
    echo ""
    if ! command -v claude &> /dev/null; then
        echo "❌ Missing: Claude Code (install: brew install anthropics/claude/claude-code)"
    fi
    if ! command -v strategy-agent &> /dev/null; then
        echo "❌ Missing: strategy-agent in PATH (restart terminal or: source ~/.zshrc)"
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Setup Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🎉 You're all set! Here's what you can do:"
echo ""
echo "  1. 🤖 Start interactive agent (RECOMMENDED):"
echo "     strategy-agent"
echo ""
echo "  2. 📊 Generate reports:"
echo "     source venv/bin/activate"
echo "     make ai-report"
echo ""
echo "  3. 📚 View documentation:"
echo "     cat docs/QUICK_REFERENCE.md"
echo ""
echo "  4. ✅ Validate your setup:"
echo "     make validate"
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
