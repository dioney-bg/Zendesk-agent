#!/bin/bash
echo "=================================="
echo "SALES STRATEGY REPORTING AGENT"
echo "Project Structure"
echo "=================================="
echo ""
tree -L 3 -I 'venv|snowflake|__pycache__|*.pyc|.claude' --dirsfirst
