# Claude Code Setup for strategy-agent

## What is Claude Code?

Claude Code is an AI-powered CLI tool that provides an interactive coding assistant. The `strategy-agent` command uses Claude Code to give you a conversational interface for querying Snowflake data.

## Installation

### macOS (Recommended)

```bash
# Install via Homebrew
brew install anthropics/claude/claude-code
```

### Verify Installation

```bash
# Check if installed
claude --version

# Should show: claude version X.X.X
```

## How strategy-agent Uses Claude Code

When you run `strategy-agent`, it:

1. ✅ Launches Claude Code in your project directory
2. ✅ Automatically loads `CLAUDE.md` with all Snowflake context
3. ✅ Gives you an interactive chat interface
4. ✅ Understands your data model, tables, and query patterns
5. ✅ Runs Snowflake queries on your behalf

## Using strategy-agent

```bash
# From anywhere (after setup)
strategy-agent
```

Then ask questions like:
- "Show me AI penetration by leader"
- "Top 10 countries by ARR growth"
- "Compare Q1 to Q4 for AMER"
- "Which industries are growing in EMEA?"

## Troubleshooting

### "claude: command not found"

**Problem:** Claude Code is not installed or not in PATH

**Solution:**
```bash
brew install anthropics/claude/claude-code
```

### "strategy-agent: command not found"

**Problem:** The command hasn't been installed globally

**Solution:**
```bash
cd ~/Zendesk-agent
./bin/install_strategy_agent

# Add to PATH if needed
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### "Could not find project files"

**Problem:** Running from wrong directory

**Solution:** `strategy-agent` should work from ANY directory. If it doesn't, the symlink might be broken:
```bash
cd ~/Zendesk-agent
rm ~/.local/bin/strategy-agent
./bin/install_strategy_agent
```

## Alternative: Run from Project Directory

If you don't want to install globally:

```bash
cd ~/Zendesk-agent
./bin/strategy-agent
```

## More Information

- Claude Code Docs: https://docs.anthropic.com/claude-code
- GitHub: https://github.com/anthropics/claude-code
