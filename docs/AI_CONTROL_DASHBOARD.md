# AI Control & Impact Dashboard

## Overview

Interactive waterfall-style dashboard showing product penetration across your customer base. Compare any two AI products and see adoption patterns instantly.

## Quick Start

```bash
make ai-control-dashboard
```

Opens: `outputs/reports/ai_control_impact/YYYY-MM-DD_ai_control_impact.html`

## Features

✅ **Single HTML file** - Self-contained, no dependencies  
✅ **Real-time switching** - Change products instantly (no regeneration)  
✅ **All data embedded** - Works offline  
✅ **7 product options** - AAA, Copilot, Gen AI, Gen Search, AI Agents Essential, QA, Paid AI

## Dashboard Structure

```
Total Customers (83,492)
├─ Penetrated: w/Product A OR Product B
│  ├─ Both: w/Product A AND Product B
│  ├─ Product B only: w/Product B (w/o Product A)
│  └─ Product A only: w/Product A (w/o Product B)
└─ Not Penetrated: w/o Product A AND Product B
```

## Available Products

| Product | Customer Count |
|---------|----------------|
| AI Agents Advanced | 1,253 |
| AI Agents Essential | 6,411 |
| Copilot | 4,227 |
| Generative Search | 17,116 |
| QA (Paid) | 1,318 |
| Gen AI (Any) | 20,887 |
| Paid AI (Any) | 5,715 |

## Usage Examples

### Cross-Sell Analysis
**Question**: "Which customers have Copilot but not AI Agents?"

**Action**: Open dashboard, select AAA + Copilot → Look at "Copilot only" row

### Product Overlap
**Question**: "How many customers use both Gen AI products?"

**Action**: Select Gen AI + Copilot → Look at "Both" row

### Market Opportunity
**Question**: "How many customers haven't adopted any AI?"

**Action**: Select Gen AI + Paid AI → Look at "Not Penetrated" row

## When to Regenerate

Generate weekly for fresh data:
```bash
make ai-control-dashboard
```

You do NOT need to regenerate to try different product combinations - just use the dropdowns!

## Data Sources

- **Customers**: Latest snapshot from CS Reset Dashboard (positive ARR only)
- **Penetration**: AI Combined Daily Snapshot (2 days ago)

## Output

Single file created at: `outputs/reports/ai_control_impact/YYYY-MM-DD_ai_control_impact.html`

Share this file with teammates - it works offline with no dependencies!

## Troubleshooting

**Problem**: Dashboard shows "Loading..."

**Solution**: Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)

**Problem**: Numbers seem wrong

**Solution**: Check if products are subsets (e.g., Copilot ⊂ Gen AI means all Copilot customers also have Gen AI)

---

**Pro Tip**: Generate once per week, share the HTML file via Slack/email, and anyone can explore all product combinations without regenerating!
