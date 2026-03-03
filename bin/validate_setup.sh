#!/bin/bash

# Sales Strategy Reporting Agent - Setup Validation
# Checks if everything is configured correctly

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "════════════════════════════════════════════════════════════════"
echo "   🔍 Sales Strategy Reporting Agent - Setup Validation"
echo "════════════════════════════════════════════════════════════════"
echo ""

ERRORS=0
WARNINGS=0

# Check 1: Python
echo -n "Checking Python installation... "
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Python $VERSION"
else
    echo -e "${RED}✗${NC} Python not found"
    ((ERRORS++))
fi

# Check 2: Virtual environment
echo -n "Checking virtual environment... "
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Not found (run: python3 -m venv venv)"
    ((ERRORS++))
fi

# Check 3: Dependencies
echo -n "Checking Python dependencies... "
if [ -d "venv" ]; then
    source venv/bin/activate
    if python -c "import pandas, yaml, openpyxl" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Installed"
    else
        echo -e "${RED}✗${NC} Missing (run: pip install -r requirements.txt)"
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}⊘${NC} Skipped (no venv)"
    ((WARNINGS++))
fi

# Check 4: Snowflake CLI
echo -n "Checking Snowflake CLI... "
SNOW_CLI="/Applications/SnowflakeCLI.app/Contents/MacOS/snow"
if [ -f "$SNOW_CLI" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Not found at $SNOW_CLI"
    ((ERRORS++))
fi

# Check 5: Snowflake authentication
echo -n "Checking Snowflake authentication... "
if [ -f "$SNOW_CLI" ]; then
    if $SNOW_CLI sql -q "SELECT 1" &> /dev/null; then
        USER=$($SNOW_CLI sql -q "SELECT CURRENT_USER()" 2>/dev/null | grep "@" | head -1)
        echo -e "${GREEN}✓${NC} Authenticated ($USER)"
    else
        echo -e "${RED}✗${NC} Not authenticated (run: snow login)"
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}⊘${NC} Skipped (no CLI)"
    ((WARNINGS++))
fi

# Check 6: Configuration file
echo -n "Checking configuration file... "
if [ -f "config/config.yaml" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Not found"
    ((ERRORS++))
fi

# Check 7: Output directories
echo -n "Checking output directories... "
if [ -d "outputs/reports" ] && [ -d "outputs/data" ] && [ -d "outputs/logs" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${YELLOW}!${NC} Missing (creating...)"
    mkdir -p outputs/reports outputs/data outputs/logs
    echo -e "${GREEN}✓${NC} Created"
    ((WARNINGS++))
fi

# Check 8: Core scripts
echo -n "Checking core scripts... "
if [ -f "scripts/core/snowflake_client.py" ] && \
   [ -f "scripts/core/report_formatter.py" ] && \
   [ -f "scripts/core/base_report.py" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Missing core scripts"
    ((ERRORS++))
fi

# Check 9: Reports
echo -n "Checking report scripts... "
if [ -f "scripts/reports/ai_penetration.py" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Missing report scripts"
    ((ERRORS++))
fi

# Check 10: Queries
echo -n "Checking SQL queries... "
if [ -d "queries/ai_penetration" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${YELLOW}!${NC} Queries directory missing"
    ((WARNINGS++))
fi

# Check 11: Git configuration
echo -n "Checking Git remotes... "
if git remote -v &> /dev/null; then
    if git remote -v | grep -q "origin"; then
        echo -e "${GREEN}✓${NC} Configured"
    else
        echo -e "${YELLOW}!${NC} No origin remote"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}!${NC} Not a git repository"
    ((WARNINGS++))
fi

# Check 12: Permissions
echo -n "Checking script permissions... "
if [ -x "setup_for_new_user.sh" ] && [ -x "run_agent.sh" ]; then
    echo -e "${GREEN}✓${NC} Executable"
else
    echo -e "${YELLOW}!${NC} Setting permissions..."
    chmod +x *.sh scripts/*.sh 2>/dev/null
    echo -e "${GREEN}✓${NC} Fixed"
    ((WARNINGS++))
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "   Summary"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ Perfect!${NC} Everything is configured correctly."
    echo ""
    echo "You're ready to generate reports!"
    echo "Try: python scripts/reports/ai_penetration.py"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Good!${NC} Setup is working but has $WARNINGS warning(s)."
    echo ""
    echo "You can use the agent, but consider fixing warnings."
else
    echo -e "${RED}✗ Issues Found!${NC} $ERRORS error(s), $WARNINGS warning(s)"
    echo ""
    echo "Please fix the errors above before using the agent."
    echo ""
    echo "Quick fixes:"
    echo "  • Run: ./setup_for_new_user.sh"
    echo "  • Or see: docs/setup/TEAM_SETUP.md"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"

exit $ERRORS
