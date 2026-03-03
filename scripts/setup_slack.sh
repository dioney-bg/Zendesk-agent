#!/bin/bash

echo "========================================="
echo "Slack CLI Authentication Setup"
echo "========================================="
echo ""
echo "This script will help you authenticate the Slack CLI."
echo ""
echo "Press Enter to start the authentication process..."
read

# Run slack login
~/.local/bin/slack login

# Check if authentication was successful
if ~/.local/bin/slack auth list | grep -q "zendesk.slack.com"; then
    echo ""
    echo "✅ Successfully authenticated!"
    echo ""
    echo "You can now close this and let Claude know the authentication worked."
else
    echo ""
    echo "❌ Authentication failed or incomplete"
    echo ""
    echo "Please try running: ~/.local/bin/slack login"
fi
