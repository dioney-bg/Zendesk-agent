# 🤖 Interactive AI Agent Guide

The Sales Strategy Agent is an interactive AI assistant that helps you analyze Snowflake data using natural language.

---

## What Is It?

Instead of writing SQL queries or running specific Python scripts, you can **talk to an AI assistant** that:
- Understands your business questions
- Knows your Snowflake tables and data structure
- Follows your reporting conventions automatically
- Generates and runs queries on-demand
- Presents results with insights

---

## Quick Start

### 1. Install Claude Code (One-Time Setup)

**macOS:**
```bash
brew install anthropics/claude/claude-code
```

**Or download from:**
https://docs.anthropic.com/claude-code

### 2. Install the strategy-agent Command

After cloning the repository and running `make setup`:

```bash
# Already done during setup, but if needed:
./bin/install_strategy_agent
```

### 3. Start the Agent

```bash
strategy-agent
```

That's it! You'll see a welcome message and can start asking questions.

---

## Example Sessions

### Session 1: Basic Analysis

```
$ strategy-agent

╔════════════════════════════════════════════════════════════╗
║         📊 Sales Strategy Reporting Agent                 ║
╚════════════════════════════════════════════════════════════╝

👋 Hi! I'm the Sales Strategy Agent.

I can help you with:
- 📊 Snowflake queries and data analysis
- 📈 AI penetration reports and trends
- 🔍 Ad-hoc account analysis
- 📋 Custom reports and insights

What would you like to analyze today?

> Show me AI penetration by leader

[Agent runs query and shows table]

+----------+----------------+-------------+-----------------+
| Leader   | Total Accounts | AI Accounts | Penetration %   |
+----------+----------------+-------------+-----------------+
| AMER     | 6,409          | 706         | 11.02%          |
| EMEA     | 3,245          | 387         | 11.93%          |
| APAC     | 1,876          | 198         | 10.56%          |
| LATAM    | 892            | 84          | 9.42%           |
| SMB      | 4,521          | 312         | 6.90%           |
| Digital  | 2,103          | 156         | 7.42%           |
| TOTAL    | 19,046         | 1,843       | 9.68%           |
+----------+----------------+-------------+-----------------+

Key insights:
- EMEA leads with 11.93% penetration
- Overall penetration is 9.68%
- Strategic segments (AMER, EMEA, APAC) outperform SMB and Digital

> What about AMER specifically by segment?

[Agent runs another query for AMER breakdown]
```

### Session 2: Period Comparison

```
> Compare AI penetration for AMER between now and January 31st

[Agent runs comparison query]

+---------------+-------+--------+--------+
| Segment       | Now   | Jan 31 | Change |
+---------------+-------+--------+--------+
| Enterprise    | 12.30%| 12.10% | +0.20pp|
| Strategic     | 22.22%| 19.73% | +2.49pp|
| Public Sector | 6.00% | 5.77%  | +0.23pp|
| Commercial    | 11.42%| 11.11% | +0.31pp|
| TOTAL         | 11.02%| 10.73% | +0.28pp|
+---------------+-------+--------+--------+

Strategic segment shows strongest growth at +2.49 percentage points!

> Great! Can you show this as net new AI accounts too?

[Agent adds absolute numbers to the comparison]
```

### Session 3: Custom Analysis

```
> I need to analyze Top 3000 Cohort 1 accounts. Show me how many have adopted AI in AMER.

[Agent uses the Top 3K filters and runs analysis]

> Now break that down by segment

[Agent creates segment breakdown for Top 3K Cohort 1 in AMER]

> Can you save this query for future use?

Sure! I'll create a file in queries/top3k_ai_analysis/cohort1_amer.sql
[Agent creates the SQL file]
```

---

## What the Agent Knows

The agent has full context about:

### ✅ Snowflake Setup
- Connection details (`zendesk` via SSO)
- Warehouse configuration
- Authentication process

### ✅ Data Structure
- **Account table**: `PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD`
- **AI penetration table**: `PRESENTATION.PRODUCT_ANALYTICS.AI_COMBINED_CRM_DAILY_SNAPSHOT`
- All column names and meanings
- Required filters to avoid duplicates

### ✅ Business Logic
- **Leader assignment**: SMB/Digital by segment, others by region
- **Fiscal calendar**: February start (not January!)
- **Standard ordering**: AMER, EMEA, APAC, LATAM, SMB, Digital
- **Segment ordering**: Enterprise, Strategic, Public Sector, Commercial, SMB, Digital

### ✅ Reporting Conventions
- Always include TOTAL row in breakdowns
- Show percentage points for changes
- Round percentages to 2 decimals
- Use proper date filtering (latest SERVICE_DATE)

### ✅ Common Patterns
- AI penetration calculations
- Period-over-period comparisons
- Segment and leader breakdowns
- Top 3K cohort analysis

---

## Common Questions You Can Ask

### Account Analysis
- "How many accounts do we have by leader?"
- "What's the distribution of segments in EMEA?"
- "Show me Top 3000 Cohort 1 accounts by region"

### AI Penetration
- "Show me AI penetration by leader"
- "What's AMER's Strategic segment penetration?"
- "Which leader has the highest penetration?"
- "Break down AI adoption for Digital leader"

### Trends & Comparisons
- "Compare this month to last month"
- "Show me Q1 vs Q4 for all leaders"
- "What's the trend over the last 3 months?"
- "How has EMEA changed since January?"

### Specific Segments
- "Show me Strategic accounts in AMER"
- "What's Public Sector penetration across all regions?"
- "Break down Commercial by leader"

### Custom Analysis
- "Find accounts that adopted AI in the last 30 days"
- "Show me the top 10 accounts by ARR in AMER Strategic"
- "Which segment has grown the most this quarter?"

---

## Tips for Best Results

### ✅ Do:
- Ask clear, specific questions
- Use business terms (leader, segment, penetration)
- Request comparisons explicitly ("compare X to Y")
- Ask for breakdowns ("by leader", "by segment")
- Request formats ("show as a table", "include totals")

### ❌ Avoid:
- Very vague questions ("tell me about accounts")
- Asking for credentials or passwords
- Requesting data exports without context
- Mixing multiple unrelated questions

### 💡 Follow-Up Questions Work Great:
```
> Show me AI penetration by leader
[Result shown]

> Now just AMER by segment
[AMER breakdown shown]

> What was this last quarter?
[Q4 comparison shown]

> Can you show the net change in accounts?
[Adds absolute numbers]
```

---

## How It Works

### Behind the Scenes

1. **You ask a question** in natural language
2. **Agent understands** your intent using the project context
3. **Agent builds SQL query** following all conventions
4. **Agent runs query** via Snowflake CLI
5. **Agent presents results** with insights and formatting
6. **You can follow up** with related questions

### Project Context (CLAUDE.md)

The agent loads `CLAUDE.md` automatically, which contains:
- Complete Snowflake schema documentation
- Business logic and conventions
- Common query patterns and examples
- Security guidelines
- Example interactions

This means every session starts with **full project knowledge** - no need to explain the basics!

---

## Advanced Usage

### Save Reusable Queries

```
> Show me AI penetration by segment for AMER

[Results shown]

> This is useful. Can you save this query?

Sure! I'll save it to queries/ai_penetration/amer_by_segment.sql
[Query saved with documentation]
```

### Generate Reports

```
> Run the AI penetration report for all leaders

[Agent executes the report script]

> Upload the results to Google Drive

[Agent uploads via Google Drive integration]
```

### Explore Data

```
> What columns are available in the account table?

[Agent lists all columns with descriptions]

> What's the date range of data available?

[Agent queries date range]
```

---

## Troubleshooting

### Agent Won't Start

**Error:** `Claude Code is not installed`

**Solution:**
```bash
brew install anthropics/claude/claude-code
```

### Snowflake Connection Issues

**Error:** `Snowflake CLI not found`

**Solution:**
- Install Snowflake CLI
- Run `make setup` to configure connection
- Authenticate: `snow login`

### Command Not Found

**Error:** `strategy-agent: command not found`

**Solution:**
```bash
# Reinstall the command
./bin/install_strategy_agent

# Or add to PATH manually
export PATH="$HOME/.local/bin:$PATH"
```

### Query Returns No Results

**Possible causes:**
- Date filters might be too restrictive
- Check if data exists for the requested period
- Verify Snowflake warehouse is running

**Ask the agent:**
```
> Why did that query return no results?
> Can you check what dates are available?
```

---

## Best Practices

### For Daily Work

1. **Start your day with strategy-agent**
   - Quick checks and updates
   - Ad-hoc questions as they arise

2. **Use pre-built reports for regular deliverables**
   - `make ai-report` for standard reports
   - Schedule these via cron for automation

3. **Ask the agent to create new reports**
   - "Can you create a weekly summary report?"
   - "Build a query I can reuse for this analysis"

### For Team Collaboration

1. **Share interesting queries**
   - Ask agent to save queries to `queries/` directory
   - Commit them to git for team reuse

2. **Document discoveries**
   - "Can you explain how this query works?"
   - Save explanations as comments in SQL files

3. **Build on each other's work**
   - Review saved queries in `queries/` directory
   - Ask agent to modify existing queries

---

## Security & Privacy

### ✅ Safe:
- Your Snowflake authentication is personal (SSO)
- Queries run with YOUR permissions only
- No credentials stored in project
- All data stays in your environment

### ❌ Never:
- Share your Snowflake credentials
- Commit personal tokens to git
- Share sensitive query results outside Zendesk
- Use agent to access unauthorized data

The agent respects all Snowflake permissions - you can only access what you're authorized to see.

---

## What's Next?

### Learn More:
- **[Quick Reference](QUICK_REFERENCE.md)** - Common commands and recipes
- **[Project Overview](PROJECT_OVERVIEW.md)** - Architecture and design
- **[CLAUDE.md](../CLAUDE.md)** - Full agent context (what the agent knows)

### Get Help:
- Ask the agent: "How do I...?"
- Check logs: `outputs/logs/`
- Open an issue on GitHub
- Contact Dioney

---

**Ready to start?**

```bash
strategy-agent
```

Ask your first question and see the power of interactive data analysis! 🚀
