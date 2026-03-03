# Sales Strategy Reporting Agent - Makefile
# Convenient commands for common tasks

.PHONY: help setup install test clean run validate docs

# Default target
help:
	@echo "Sales Strategy Reporting Agent - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup        Run interactive setup for new users"
	@echo "  make install      Install Python dependencies"
	@echo "  make validate     Validate your setup"
	@echo ""
	@echo "Running Reports:"
	@echo "  make run          Launch interactive menu"
	@echo "  make ai-report    Generate AI Penetration Report"
	@echo ""
	@echo "Development:"
	@echo "  make test         Run tests (when available)"
	@echo "  make clean        Clean generated files"
	@echo "  make docs         Open documentation"
	@echo ""
	@echo "For more help, see: docs/setup/TEAM_SETUP.md"

# Setup for new users
setup:
	@./bin/setup_for_new_user.sh

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
