#!/bin/bash
#
# Generate FY27 Interactive Sales Report
# This script queries Snowflake, generates JavaScript data, and creates a self-contained HTML file
#
# Usage: ./scripts/generate_sales_report.sh
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║         📊 FY27 Sales Report Generator                     ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Start timer
START_TIME=$(date +%s.%N)

# Get current date for filename
REPORT_DATE=$(date +%Y-%m-%d)

# Create sales_report directory if it doesn't exist
mkdir -p outputs/sales_report

# Step 1: Get latest snapshot date
echo -e "${BLUE}[1/7]${NC} Getting latest data snapshot date..."
LATEST_DATE=$(snow sql -q "SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD" --format=csv | tail -1)
echo -e "${GREEN}      Latest data: ${LATEST_DATE}${NC}"
echo "$LATEST_DATE" > /tmp/data_refresh_date.txt

# Step 2: Query bookings data
echo -e "${BLUE}[2/7]${NC} Querying closed bookings (FY27 Q1)..."
snow sql -f queries/sales_report/bookings.sql --format=csv > /tmp/bookings_data.csv
BOOKINGS_COUNT=$(tail -n +2 /tmp/bookings_data.csv | wc -l | tr -d ' ')
echo -e "${GREEN}      Found ${BOOKINGS_COUNT} region/segment combinations${NC}"

# Step 3: Query pipeline data
echo -e "${BLUE}[3/7]${NC} Querying open pipeline (FY27 Q1-Q4)..."
snow sql -f queries/sales_report/pipeline.sql --format=csv > /tmp/pipeline_data.csv
PIPELINE_COUNT=$(tail -n +2 /tmp/pipeline_data.csv | wc -l | tr -d ' ')
echo -e "${GREEN}      Found ${PIPELINE_COUNT} pipeline records${NC}"

# Step 4: Query renewal accounts
echo -e "${BLUE}[4/7]${NC} Querying renewal accounts (top 5 per region × segment)..."
snow sql -f queries/sales_report/renewals.sql --format=csv > /tmp/renewal_data.csv
RENEWAL_COUNT=$(tail -n +2 /tmp/renewal_data.csv | wc -l | tr -d ' ')
echo -e "${GREEN}      Found ${RENEWAL_COUNT} renewal accounts${NC}"

# Step 5: Generate JavaScript
echo -e "${BLUE}[5/7]${NC} Generating JavaScript data file..."
python3 outputs/generate_report_data.py > /dev/null

# Step 6: Create self-contained HTML
echo -e "${BLUE}[6/7]${NC} Creating self-contained HTML report..."
python3 scripts/embed_report_js.py

# Rename with date at the beginning and move to sales_report folder
mv outputs/fy27_sales_report_standalone.html outputs/sales_report/${REPORT_DATE}_fy27_sales_report.html

# Zip the report
echo -e "${BLUE}[7/7]${NC} Compressing report..."
cd outputs/sales_report
zip -q ${REPORT_DATE}_fy27_sales_report.html.zip ${REPORT_DATE}_fy27_sales_report.html
# Remove the unzipped HTML file, keep only the zip
rm ${REPORT_DATE}_fy27_sales_report.html
cd ../..

# Cleanup
rm /tmp/bookings_data.csv /tmp/pipeline_data.csv /tmp/renewal_data.csv /tmp/data_refresh_date.txt

# Calculate elapsed time
END_TIME=$(date +%s.%N)
ELAPSED=$(printf "%.1f" $(echo "$END_TIME - $START_TIME" | bc))

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║  ✅ Report Generated Successfully!                         ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📦 Report ZIP:  ${BLUE}outputs/sales_report/${REPORT_DATE}_fy27_sales_report.html.zip${NC}"
echo -e "📅 Data as of: ${BLUE}${LATEST_DATE}${NC}"
echo -e "⚡ Generated in: ${BLUE}${ELAPSED}s${NC}"
echo ""
echo -e "${YELLOW}💡 To share with colleagues:${NC}"
echo -e "   Send them: outputs/sales_report/${REPORT_DATE}_fy27_sales_report.html.zip"
echo ""
echo -e "${YELLOW}💡 To view latest report:${NC}"
echo -e "   unzip outputs/sales_report/\$(ls -t outputs/sales_report/*.zip | head -1 | xargs basename) -d /tmp && open /tmp/${REPORT_DATE}_fy27_sales_report.html"
echo ""
echo -e "${YELLOW}💡 List all reports (newest first):${NC}"
echo -e "   ls -lt outputs/sales_report/"
echo ""
