#!/bin/bash

# Sales Strategy Reporting Agent - Interactive Menu
# Simple interface for team members to run reports

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found."
    echo "Please run: ./setup_for_new_user.sh"
    exit 1
fi

# Activate venv
source venv/bin/activate

clear

echo "════════════════════════════════════════════════════════════════"
echo "        📊 Sales Strategy Reporting Agent"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Select an option:"
echo ""
echo "  1. 🤖 AI Penetration Report"
echo "  2. 💼 Account Health Dashboard (Coming Soon)"
echo "  3. 💰 Revenue Forecast (Coming Soon)"
echo "  4. 🔍 Run Custom SQL Query"
echo "  5. 📋 List All Available Reports"
echo "  6. ⚙️  Test Snowflake Connection"
echo "  7. 📚 View Documentation"
echo "  8. 🆘 Help & Troubleshooting"
echo "  9. 🚪 Exit"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

read -p "Enter your choice (1-9): " choice

case $choice in
    1)
        echo ""
        echo "🤖 Generating AI Penetration Report..."
        echo ""
        python scripts/reports/ai_penetration.py
        echo ""
        read -p "Press Enter to continue..."
        ;;
    2)
        echo ""
        echo "💼 Account Health Dashboard - Coming Soon!"
        echo ""
        echo "This report is under development."
        echo "Contact Dioney Blanco for updates."
        echo ""
        read -p "Press Enter to continue..."
        ;;
    3)
        echo ""
        echo "💰 Revenue Forecast - Coming Soon!"
        echo ""
        echo "This report is under development."
        echo "Contact Dioney Blanco for updates."
        echo ""
        read -p "Press Enter to continue..."
        ;;
    4)
        echo ""
        echo "🔍 Custom SQL Query"
        echo ""
        echo "Enter your SQL query (end with semicolon on a new line):"
        echo ""

        # Read multiline input
        query=""
        while IFS= read -r line; do
            query+="$line"$'\n'
            if [[ $line == *";" ]]; then
                break
            fi
        done

        echo ""
        echo "Executing query..."
        echo ""

        # Create temp Python script to run query
        python << EOF
from scripts.core.snowflake_client import SnowflakeClient
import pandas as pd

query = """$query"""

sf = SnowflakeClient()
results = sf.execute_query(query.strip())

if results:
    df = pd.DataFrame(results)
    print(df.to_string())
    print(f"\n✅ Query returned {len(results)} rows")
else:
    print("❌ Query failed or returned no results")
EOF
        echo ""
        read -p "Press Enter to continue..."
        ;;
    5)
        echo ""
        echo "📋 Available Reports:"
        echo ""
        python << 'EOF'
import yaml
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    reports = config.get('reports', {})
    for code, info in reports.items():
        status = "✅" if info.get('enabled', False) else "🚧"
        print(f"{status} {info.get('name', code)}")
        print(f"   Description: {info.get('description', 'N/A')}")
        print(f"   Command: python scripts/reports/{code}.py")
        print()
EOF
        read -p "Press Enter to continue..."
        ;;
    6)
        echo ""
        echo "⚙️  Testing Snowflake Connection..."
        echo ""

        /Applications/SnowflakeCLI.app/Contents/MacOS/snow sql -q "
        SELECT
            CURRENT_USER() as user,
            CURRENT_WAREHOUSE() as warehouse,
            CURRENT_DATABASE() as database,
            CURRENT_SCHEMA() as schema,
            CURRENT_DATE() as date
        "

        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Connection successful!"
        else
            echo ""
            echo "❌ Connection failed"
            echo ""
            echo "Troubleshooting:"
            echo "  1. Run: snow login"
            echo "  2. Check config/config.yaml"
            echo "  3. Verify warehouse access"
        fi
        echo ""
        read -p "Press Enter to continue..."
        ;;
    7)
        echo ""
        echo "📚 Documentation"
        echo ""
        echo "Available documentation:"
        echo ""
        echo "  1. README.md - Main documentation"
        echo "  2. docs/setup/TEAM_SETUP.md - Setup guide"
        echo "  3. docs/QUICK_REFERENCE.md - Quick commands"
        echo "  4. docs/PROJECT_OVERVIEW.md - Architecture"
        echo ""
        read -p "Which doc to view? (1-4): " doc_choice

        case $doc_choice in
            1) less README.md ;;
            2) less docs/setup/TEAM_SETUP.md ;;
            3) less docs/QUICK_REFERENCE.md ;;
            4) less docs/PROJECT_OVERVIEW.md ;;
            *) echo "Invalid choice" ;;
        esac
        ;;
    8)
        echo ""
        echo "🆘 Help & Troubleshooting"
        echo ""
        echo "Common Issues:"
        echo ""
        echo "1. ModuleNotFoundError"
        echo "   → Run: source venv/bin/activate && pip install -r requirements.txt"
        echo ""
        echo "2. Snowflake authentication failed"
        echo "   → Run: /Applications/SnowflakeCLI.app/Contents/MacOS/snow login"
        echo ""
        echo "3. Permission denied"
        echo "   → Run: chmod +x scripts/*.py *.sh"
        echo ""
        echo "4. Query execution failed"
        echo "   → Check your warehouse access"
        echo "   → Verify config/config.yaml settings"
        echo ""
        echo "📋 Check logs:"
        echo "   tail -f outputs/logs/sales_strategy_agent.log"
        echo ""
        echo "💬 Contact:"
        echo "   Maintainer: Dioney Blanco"
        echo "   GitHub Issues: [repo-url]"
        echo ""
        read -p "Press Enter to continue..."
        ;;
    9)
        echo ""
        echo "👋 Goodbye!"
        echo ""
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please select 1-9."
        echo ""
        read -p "Press Enter to continue..."
        ;;
esac

# Loop back to menu
exec bash "$0"
