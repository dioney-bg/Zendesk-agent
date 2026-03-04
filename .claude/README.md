# Claude Code Settings

## Auto-Approved Commands

This project is configured to auto-approve safe Bash commands used for:
- Running Snowflake queries
- Executing SQL analysis
- Reading query results
- Validating data
- Searching files

These are safe, read-only operations that speed up the strategy-agent workflow.

## Settings Files

- **settings.json**: Shared with teammates (in git)
  - Auto-approves safe query operations
  - Can be customized per project needs

- **settings.local.json**: Personal settings (gitignored)
  - Override project settings if needed
  - Won't be pushed to GitHub

## Destructive Operations

The agent will STILL ask for confirmation on:
- File modifications (Edit, Write)
- Git operations (commit, push)
- Deleting files
- Any other potentially destructive action

This gives you speed without sacrificing safety.
