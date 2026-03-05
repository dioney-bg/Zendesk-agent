# Changelog

All notable changes to the Sales Strategy Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.4.0] - 2026-03-05

### 🎨 Major: Beautiful Markdown Table Display

**The Big Change:** Switched from ASCII tables to beautiful markdown tables with enhanced formatting.

#### Added
- **Markdown Table Rendering**: Agent now outputs results as markdown tables (rendered beautifully by Claude Code UI)
- **Smart Number Formatting**:
  - ARR scales automatically: ≥$1B → $X.XB, ≥$1M → $X.XM, ≥$1K → $XK
  - Thousand separators (commas) on all numbers
  - Automatic % signs on percentage columns
- **Column Type Detection**: Auto-detects ARR, percentage, and count columns for proper formatting

#### Changed
- **Query format**: Changed from `--format=table` to `--format=csv` (parsed internally)
- **Display method**: CSV parsed silently, only formatted markdown table shown to user
- **User experience**: Raw CSV output no longer visible to users

#### Technical
- Updated all query commands across CLAUDE.md, MEMORY.md, and Makefile
- Agent now converts CSV to markdown table automatically
- Maintains all existing data quality rules and formatting standards

---

## [1.3.0] - 2026-03-05

### 🔧 Critical Display Fixes & Output Improvements

Multiple iterations to solve table display issues and improve user experience.

#### Fixed
- **Table Display Issue**: Tables were not showing due to missing `--format=table` flag
- **"Be Concise" Misinterpretation**: Agent was skipping table display thinking "be concise" meant no tables
- **UI Collapse**: Fixed display method to prevent Claude Code from collapsing output
- **Copy from Tool Results**: Added explicit instruction to copy ASCII table from Bash tool results

#### Changed
- **Output Thresholds**: Adjusted from ≤50 rows to ≤25 rows AND <8 columns for terminal display
- **Preview Size**: Changed from 10-15 rows to 5 rows for large dataset previews
- **Insights Placement**: Clarified insights should appear AFTER table, not instead of it
- **Number Formatting**: Added thousand separators (commas) to all numbers for readability

#### Added
- **Timing Display**: Added `⚡ Completed in X.Xs` to show total response time
- **Command Template**: Prominent command template at top of CLAUDE.md with visual emphasis
- **P0 Priority**: Made table display the #1 critical rule

---

## [1.2.0] - 2026-03-05

### 🎯 Multi-Product Support & Enhanced Capabilities

**Major Feature:** Full support for ALL Zendesk products, not just AI products.

#### Added - Product Support
- **Multi-Product Analysis**: Support for all products:
  - AI Agents (Ultimate, Ultimate_AR)
  - Copilot
  - Employee Service (ES)
  - Quality Assurance (QA)
  - Workforce Engagement (WEM, WFM)
  - Automated Resolutions (Zendesk_AR)
  - Suite, Contact Center, ADPP
- **Product Filtering Rules**: Clear taxonomy and filtering logic for each product category
- **Total Booking Pattern**: Use `PRODUCT='Total Booking'` for consolidated totals

#### Added - New Business vs Expansion
- **Opportunity Type Analysis**: Support for `OPPORTUNITY_TYPE` field
- **Breakdown by Type**: Can now analyze New Business vs Expansion deals
- **Multi-dimensional**: Works across all products, leaders, and segments

#### Added - Pipeline & Bookings Enhancements
- **GTM Team Tracking**: Added `gtm_team` column for sourcing attribution
- **Stage Tracking**: Added `STAGE_NAME` column for opportunity stages
- **ES Department Cleaning**: Handle multi-department ES opportunities
- **AE/Manager Columns**:
  - `CORRECT_OWNER_NAME` for AE/sales rep
  - `OPPORTUNITY_OWNER_MANAGER_NAME` for manager/FLM

#### Added - Data Quality Rules
- **Region Conversion**: NA = AMER (handles synonyms: NA, AMER, North America)
- **Opportunity Lists**: Must include `CRM_OPPORTUNITY_ID` + Total Booking value (P0 rule)
- **No Extra Columns**: Only include required + requested columns (P0 rule)
- **Critical Filters**: Enforced data quality filters for pipeline/bookings queries:
  - `DATE_LABEL='today'`
  - `opportunity_is_commissionable=TRUE`
  - `stage_2_plus_date_c IS NOT NULL`
  - `PRODUCT_BOOKING_ARR_USD > 0` (for bookings) or `PRODUCT_ARR_USD > 0` (for pipeline)

#### Added - Documentation
- **MEMORY_AUDIT_2026-03-05.md**: Comprehensive audit of all rules and standards
- **TEST_ENVIRONMENT_GUIDE.md**: Guide for setting up test environments
- **Instruction Hierarchy**: CLAUDE.md always overrides auto-memory

#### Changed
- **Product Terminology**:
  - "AI Agents" (specific) = Ultimate + Ultimate_AR only
  - "AI products" (broad) = Ultimate + Ultimate_AR + Copilot
  - "Copilot" (specific) = Copilot only
- **ES Product Name**: Changed from "Enterprise Support" to "Employee Service"
- **Opportunity Pattern**: Generic pattern works for ALL products, not just Copilot

---

## [1.1.0] - 2026-03-04

### Initial Release

#### Added
- Interactive AI agent for Snowflake data analysis
- Pattern-based query system with reusable templates
- Leader assignment logic (regional vs segment leaders)
- AI penetration analysis queries
- Geographic and industry analysis patterns
- Competitive analysis (bot competitors)
- P0/P1/P2 priority system for rules
- Decision tree workflow
- Auto-update feature for launcher
- Security settings and deny rules

#### Features
- Natural language query interface
- Pre-built query library
- CSV export functionality
- Fiscal calendar support (FY starts February)
- Standard ordering (AMER→EMEA→APAC→LATAM→SMB→Digital)
- ARR formatting with $ signs and K/M notation
- NULL handling with COALESCE
- TOTAL row validation

---

## Version Numbering

- **1.x.0**: Major features, breaking changes, or significant improvements
- **1.0.x**: Bug fixes, minor improvements, documentation updates

---

## Key Contributors

- Dioney Blanco (dioney.blanco@zendesk.com) - Project maintainer
- Claude Sonnet 4.5 (noreply@anthropic.com) - AI assistant

---

## Links

- **Repository**: Internal Zendesk repository
- **Documentation**: See `docs/` directory
- **Quick Start**: See `docs/QUICK_REFERENCE.md`
- **Team Setup**: See `docs/setup/TEAM_SETUP.md`
