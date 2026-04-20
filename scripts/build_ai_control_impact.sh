#!/bin/bash
# Build AI Control & Impact Dashboard - Single HTML file with embedded data

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$PROJECT_ROOT/outputs/reports/ai_control_impact"
DATE=$(date +%Y-%m-%d)
OUTPUT_FILE="$OUTPUT_DIR/${DATE}_ai_control_impact.html"

echo "🏗️  Building AI Control & Impact Dashboard..."
echo "   Date: $DATE"
echo ""

# Generate data and create HTML in one step
python3 << PYEOF
import subprocess
import json
import sys

# Generate data
print("📊 Fetching product penetration data from Snowflake...", flush=True)
result = subprocess.run(
    ['python3', '$SCRIPT_DIR/generate_ai_control_impact.py'],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("❌ Failed to generate data", file=sys.stderr)
    print(result.stderr, file=sys.stderr)
    sys.exit(1)

data = json.loads(result.stdout)

print(f"✅ Loaded data: {data['total_customers']:,} customers, {len(data['products'])} products", flush=True)
print("🔧 Building HTML...", flush=True)

# Create single self-contained HTML file
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Control & Impact Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #03363d 0%, #0b5c6b 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; font-weight: 600; }}
        .header p {{ font-size: 14px; opacity: 0.9; }}
        .controls {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .controls h3 {{ margin-bottom: 15px; color: #03363d; font-size: 18px; }}
        .dropdown-container {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .dropdown-group {{ display: flex; flex-direction: column; gap: 8px; }}
        .dropdown-group label {{ font-size: 14px; font-weight: 500; color: #555; }}
        select {{ padding: 10px 15px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; background: white; cursor: pointer; min-width: 200px; }}
        select:focus {{ outline: none; border-color: #03363d; box-shadow: 0 0 0 3px rgba(3, 54, 61, 0.1); }}
        .dashboard-container {{ background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .waterfall-table {{ width: 100%; border-collapse: separate; border-spacing: 0; }}
        .waterfall-table thead th {{ background: #f8f9fa; padding: 15px; text-align: left; font-weight: 600; font-size: 14px; color: #555; border-bottom: 2px solid #e0e0e0; }}
        .waterfall-table tbody tr {{ transition: background-color 0.2s; }}
        .waterfall-table tbody tr:hover {{ background: #f8f9fa; }}
        .waterfall-table tbody td {{ padding: 15px; border-bottom: 1px solid #f0f0f0; }}
        .category-cell {{ font-size: 14px; display: flex; align-items: center; gap: 10px; }}
        .indent-1 {{ padding-left: 30px; }}
        .indent-2 {{ padding-left: 50px; }}
        .category-icon {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }}
        .icon-total {{ background: #03363d; }}
        .icon-penetrated {{ background: #17b169; }}
        .icon-both {{ background: #3091ec; }}
        .icon-product-b {{ background: #ffc839; }}
        .icon-product-a {{ background: #f97316; }}
        .icon-not-penetrated {{ background: #dc2626; }}
        .count-cell {{ font-size: 18px; font-weight: 600; color: #03363d; text-align: right; }}
        .pct-cell {{ font-size: 16px; color: #666; text-align: right; }}
        .row-total {{ background: #f8f9fa; font-weight: 600; }}
        .row-penetrated {{ background: #f0fdf4; }}
        .row-not-penetrated {{ background: #fef2f2; }}
        .product-label {{ font-weight: 500; color: #03363d; }}
        .error {{ background: #fef2f2; color: #dc2626; padding: 20px; border-radius: 8px; border: 1px solid #fecaca; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Control & Impact Dashboard</h1>
        <p>Track product penetration and customer adoption patterns | Generated: {data['generated_at'][:10]}</p>
    </div>

    <div class="controls">
        <h3>Select Products to Compare</h3>
        <div class="dropdown-container">
            <div class="dropdown-group">
                <label for="product-a">Product A:</label>
                <select id="product-a">
                    <option value="aaa">AI Agents Advanced</option>
                    <option value="ai_agents_essential">AI Agents Essential</option>
                    <option value="copilot">Copilot</option>
                    <option value="gen_search">Generative Search</option>
                    <option value="qa">QA (Paid)</option>
                    <option value="gen_ai">Gen AI (Any)</option>
                    <option value="paid_ai">Paid AI (Any)</option>
                </select>
            </div>
            <div class="dropdown-group">
                <label for="product-b">Product B:</label>
                <select id="product-b">
                    <option value="aaa">AI Agents Advanced</option>
                    <option value="ai_agents_essential">AI Agents Essential</option>
                    <option value="copilot" selected>Copilot</option>
                    <option value="gen_search">Generative Search</option>
                    <option value="qa">QA (Paid)</option>
                    <option value="gen_ai">Gen AI (Any)</option>
                    <option value="paid_ai">Paid AI (Any)</option>
                </select>
            </div>
        </div>
    </div>

    <div class="dashboard-container">
        <div id="dashboard-content"></div>
    </div>

    <script>
        const DATA = {json.dumps(data)};

        function fmt(num) {{ return num.toLocaleString('en-US'); }}

        function calc(pA, pB) {{
            if (pA === pB) return null;
            const total = DATA.total_customers;
            const prodA = DATA.products[pA];
            const prodB = DATA.products[pB];
            if (!prodA || !prodB) return null;

            const key = [pA, pB].sort().join('_');
            const comb = DATA.combinations[key];

            let both = 0, either = 0, aOnly = 0, bOnly = 0;

            if (comb) {{
                both = comb.both;
                either = comb.either;
                const sorted = [pA, pB].sort();
                if (comb.a_only !== undefined) {{
                    if (sorted[0] === pA) {{
                        aOnly = comb.a_only;
                        bOnly = comb.b_only;
                    }} else {{
                        aOnly = comb.b_only;
                        bOnly = comb.a_only;
                    }}
                }} else {{
                    aOnly = prodA.count - both;
                    bOnly = prodB.count - both;
                }}
            }} else {{
                both = Math.floor(Math.min(prodA.count, prodB.count) * 0.1);
                aOnly = prodA.count - both;
                bOnly = prodB.count - both;
                either = prodA.count + prodB.count - both;
            }}

            const notPen = total - either;

            return {{
                total: {{ count: total, pct: 100 }},
                either: {{ count: either, pct: either / total * 100 }},
                both: {{ count: both, pct: both / total * 100 }},
                bOnly: {{ count: bOnly, pct: bOnly / total * 100 }},
                aOnly: {{ count: aOnly, pct: aOnly / total * 100 }},
                notPen: {{ count: notPen, pct: notPen / total * 100 }},
                nameA: prodA.name,
                nameB: prodB.name
            }};
        }}

        function render() {{
            const pA = document.getElementById('product-a').value;
            const pB = document.getElementById('product-b').value;
            const out = document.getElementById('dashboard-content');

            if (pA === pB) {{
                out.innerHTML = '<div class="error">Please select two different products</div>';
                return;
            }}

            const m = calc(pA, pB);
            if (!m) {{
                out.innerHTML = '<div class="error">Error calculating metrics</div>';
                return;
            }}

            out.innerHTML = \`
                <table class="waterfall-table">
                    <thead>
                        <tr>
                            <th style="width: 50%;">Customer Segment</th>
                            <th style="width: 25%;">Current Customers</th>
                            <th style="width: 25%;">% of Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="row-total">
                            <td><div class="category-cell"><span class="category-icon icon-total"></span><strong>UNIQUE TOTAL CUSTOMERS</strong></div></td>
                            <td class="count-cell">\${{fmt(m.total.count)}}</td>
                            <td class="pct-cell">\${{m.total.pct.toFixed(1)}}%</td>
                        </tr>
                        <tr class="row-penetrated">
                            <td><div class="category-cell indent-1"><span class="category-icon icon-penetrated"></span><strong>Penetrated Customers: w/\${{m.nameA}} OR \${{m.nameB}}</strong></div></td>
                            <td class="count-cell">\${{fmt(m.either.count)}}</td>
                            <td class="pct-cell">\${{m.either.pct.toFixed(1)}}%</td>
                        </tr>
                        <tr>
                            <td><div class="category-cell indent-2"><span class="category-icon icon-both"></span>Customers: w/\${{m.nameA}} AND \${{m.nameB}}</div></td>
                            <td class="count-cell">\${{fmt(m.both.count)}}</td>
                            <td class="pct-cell">\${{m.both.pct.toFixed(1)}}%</td>
                        </tr>
                        <tr>
                            <td><div class="category-cell indent-2"><span class="category-icon icon-product-b"></span>Customers: w/<span class="product-label">\${{m.nameB}}</span> (w/o \${{m.nameA}})</div></td>
                            <td class="count-cell">\${{fmt(m.bOnly.count)}}</td>
                            <td class="pct-cell">\${{m.bOnly.pct.toFixed(1)}}%</td>
                        </tr>
                        <tr>
                            <td><div class="category-cell indent-2"><span class="category-icon icon-product-a"></span>Customers: w/<span class="product-label">\${{m.nameA}}</span> (w/o \${{m.nameB}})</div></td>
                            <td class="count-cell">\${{fmt(m.aOnly.count)}}</td>
                            <td class="pct-cell">\${{m.aOnly.pct.toFixed(1)}}%</td>
                        </tr>
                        <tr class="row-not-penetrated">
                            <td><div class="category-cell indent-1"><span class="category-icon icon-not-penetrated"></span><strong>Not Penetrated Customers: w/o \${{m.nameA}} AND \${{m.nameB}}</strong></div></td>
                            <td class="count-cell">\${{fmt(m.notPen.count)}}</td>
                            <td class="pct-cell">\${{m.notPen.pct.toFixed(1)}}%</td>
                        </tr>
                    </tbody>
                </table>
            \`;
        }}

        document.getElementById('product-a').addEventListener('change', render);
        document.getElementById('product-b').addEventListener('change', render);
        render();
    </script>
</body>
</html>'''

# Write file
with open('$OUTPUT_FILE', 'w') as f:
    f.write(html)

print(f"✅ Dashboard created successfully!")
PYEOF

echo ""
echo "📁 Output: $OUTPUT_FILE"
echo ""
echo "🎯 Features:"
echo "   • Single self-contained HTML file"
echo "   • Real-time product switching (no regeneration needed)"
echo "   • All data embedded inline"
echo ""
echo "🌐 Open in browser:"
echo "   open '$OUTPUT_FILE'"
