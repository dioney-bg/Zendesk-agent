# Sales Strategy Reporting Agent - Makefile
# Convenient commands for common tasks

.PHONY: help setup install test clean run validate docs setup-drive ask-chatgpt

# Default target
help:
	@echo "Sales Strategy Reporting Agent - Available Commands"
	@echo ""
	@echo "🤖 Interactive Agent (Recommended):"
	@echo "  make agent        Launch interactive AI assistant"
	@echo "  strategy-agent    (same as above, works from any directory)"
	@echo "  make ask-chatgpt  Chat with ChatGPT in terminal"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup        Run interactive setup for new users"
	@echo "  make setup-drive  Set up Google Drive integration (optional)"
	@echo "  make install      Install Python dependencies"
	@echo "  make validate     Validate your setup"
	@echo ""
	@echo "Running Reports:"
	@echo "  make run                    Launch interactive menu"
	@echo "  make ai-report              Generate AI Penetration Report"
	@echo "  make sales-report           Generate interactive FY27 sales report (HTML)"
	@echo "  make ai-control-dashboard   Generate AI Control & Impact Dashboard (HTML)"
	@echo ""
	@echo "Ad-hoc Queries (Geographic):"
	@echo "  make country-report             Top 5 countries by ARR and accounts"
	@echo "  make country-growth-report      Top 5 countries by YoY growth"
	@echo "  make country-decreases-report   Countries with biggest account losses"
	@echo ""
	@echo "Ad-hoc Queries (Industry):"
	@echo "  make amer-industry-growth       Top 5 industries YoY growth for AMER"
	@echo ""
	@echo "Ad-hoc Queries (Competitive):"
	@echo "  make bot-competitor-wins        Top 20 AI Agent wins vs bot competitors"
	@echo "  make bot-competitor-pipeline    Top 20 AI Agent pipeline vs bot competitors"
	@echo ""
	@echo "Development:"
	@echo "  make test         Run tests (when available)"
	@echo "  make clean        Clean generated files"
	@echo "  make docs         Open documentation"
	@echo ""
	@echo "For more help, see: docs/setup/TEAM_SETUP.md"

# Launch interactive AI agent
agent:
	@./bin/strategy-agent

# Chat with ChatGPT in terminal
ask-chatgpt:
	@. venv/bin/activate && python scripts/core/chatgpt_terminal.py

# Setup for new users
setup:
	@./bin/setup_for_new_user.sh

# Setup Google Drive integration
setup-drive:
	@./bin/setup_google_drive.sh

# Install dependencies
install:
	@echo "Installing dependencies..."
	@python3 -m venv venv
	@. venv/bin/activate && pip install --upgrade pip
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Validate setup
validate:
	@./bin/validate_setup.sh

# Run interactive menu
run:
	@./bin/run_agent.sh

# Generate AI Penetration Report
ai-report:
	@. venv/bin/activate && python scripts/reports/ai_penetration.py

# Ad-hoc Queries - Geographic
country-report:
	@/Applications/SnowflakeCLI.app/Contents/MacOS/snow sql -f queries/geographic/top_countries_by_arr_and_accounts.sql --format=csv

country-growth-report:
	@/Applications/SnowflakeCLI.app/Contents/MacOS/snow sql -f queries/geographic/country_growth_yoy.sql --format=csv

country-decreases-report:
	@/Applications/SnowflakeCLI.app/Contents/MacOS/snow sql -f queries/geographic/country_decreases_yoy.sql --format=csv

# Ad-hoc Queries - Industry
amer-industry-growth:
	@/Applications/SnowflakeCLI.app/Contents/MacOS/snow sql -f queries/industry/amer_industry_growth_yoy.sql --format=csv

# Ad-hoc Queries - Competitive Analysis
bot-competitor-wins:
	@/Applications/SnowflakeCLI.app/Contents/MacOS/snow sql -f queries/competitive/bot_competitor_wins.sql --format=csv

bot-competitor-pipeline:
	@/Applications/SnowflakeCLI.app/Contents/MacOS/snow sql -f queries/competitive/bot_competitor_pipeline.sql --format=csv

# Run tests (placeholder)
test:
	@echo "Tests not yet implemented"
	@echo "Run: pytest tests/ (when tests are added)"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned"

# Open documentation
docs:
	@echo "📚 Documentation:"
	@echo ""
	@echo "  Setup Guide:      docs/setup/TEAM_SETUP.md"
	@echo "  Quick Reference:  docs/QUICK_REFERENCE.md"
	@echo "  Project Overview: docs/PROJECT_OVERVIEW.md"
	@echo "  Security:         SECURITY.md"
	@echo "  Contributing:     CONTRIBUTING.md"
	@echo ""
	@echo "Open with: less docs/setup/TEAM_SETUP.md"

# Check Snowflake connection
check-snowflake:
	@echo "Testing Snowflake connection..."
	@/Applications/SnowflakeCLI.app/Contents/MacOS/snow sql -q "SELECT CURRENT_USER(), CURRENT_WAREHOUSE(), CURRENT_DATE()"

# Show project structure
structure:
	@./bin/list_structure.sh 2>/dev/null || tree -L 3 -I 'venv|__pycache__|*.pyc' --dirsfirst

# Sync fork with upstream (for team members)
sync:
	@echo "Syncing fork with upstream..."
	@git fetch upstream
	@git checkout main
	@git merge upstream/main
	@git push origin main
	@echo "✅ Fork synced"
	@echo "💡 Run: make install (to update dependencies)"

# Generate interactive FY27 sales report
sales-report:
	@echo "📊 Generating interactive FY27 sales report..."
	@bash scripts/generate_sales_report.sh

# AI Control & Impact Dashboard (Complete Production Version)
ai-control-dashboard:
	@echo "📊 Generating AI Control & Impact Dashboard..."
	@echo "   ✅ All 7 products with dynamic switching"
	@echo "   ✅ Time comparisons (LQ, LM)"
	@echo "   ✅ Pipeline and lost opportunity breakdown"
	@echo ""
	@bash scripts/build_ai_control_complete.sh
