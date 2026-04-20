#!/usr/bin/env python3
"""
Embed JavaScript data into HTML to create self-contained report
This allows the report to be shared as a single file
"""

import os

# Paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(PROJECT_DIR, 'outputs', 'fy27_sales_report_interactive.html')
JS_PATH = os.path.join(PROJECT_DIR, 'outputs', 'report-data.js')
OUTPUT_PATH = os.path.join(PROJECT_DIR, 'outputs', 'fy27_sales_report_standalone.html')

# Read HTML template
with open(HTML_PATH, 'r') as f:
    html_content = f.read()

# Read JavaScript data
with open(JS_PATH, 'r') as f:
    js_content = f.read()

# Replace external script reference with embedded script
html_content = html_content.replace(
    '<script src="report-data.js"></script>',
    f'<script>\n{js_content}\n    </script>'
)

# Write self-contained HTML
with open(OUTPUT_PATH, 'w') as f:
    f.write(html_content)

# Get file size
file_size = len(html_content)
file_size_kb = file_size / 1024

print(f"✅ Self-contained HTML created")
print(f"   Location: {OUTPUT_PATH}")
print(f"   Size: {file_size_kb:.1f} KB")
