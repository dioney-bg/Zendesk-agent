#!/usr/bin/env python3
"""Build complete dashboard with embedded data - simplified"""

import subprocess
import json
import sys
from datetime import datetime

# Generate data
print("📊 Fetching data...", flush=True)
result = subprocess.run(
    ['python3', 'scripts/generate_ai_control_fast.py'],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("❌ Data generation failed", file=sys.stderr)
    sys.exit(1)

# Parse data (skip stderr lines)
lines = result.stdout.strip().split('\n')
json_start = None
for i, line in enumerate(lines):
    if line.strip().startswith('{'):
        json_start = i
        break

if json_start is None:
    print("❌ Could not find JSON data", file=sys.stderr)
    sys.exit(1)

json_text = '\n'.join(lines[json_start:])
data = json.loads(json_text)

print(f"✅ Loaded: {data['totals']['current']:,} current, {data['totals']['last_quarter']:,} LQ", flush=True)

# Build HTML with embedded data
date_str = datetime.now().strftime('%Y-%m-%d')
output_file = f'outputs/reports/ai_control_impact/{date_str}_ai_control_impact.html'

html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Control & Impact Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #1e293b; padding: 24px; font-size: 13px; }
        .container { max-width: 1800px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%); color: white; padding: 32px 40px; border-radius: 12px; margin-bottom: 24px; }
        .header h1 { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
        .header .subtitle { font-size: 14px; opacity: 0.9; }
        .controls-section { background: white; padding: 24px 32px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); }
        .controls-title { font-size: 16px; font-weight: 600; color: #0f172a; margin-bottom: 16px; }
        .dropdown-row { display: flex; gap: 24px; flex-wrap: wrap; }
        .dropdown-wrapper { display: flex; flex-direction: column; gap: 8px; }
        .dropdown-wrapper label { font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; }
        select { padding: 10px 14px; border: 1.5px solid #e2e8f0; border-radius: 8px; font-size: 14px; background: white; cursor: pointer; min-width: 220px; }
        select:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
        .dashboard-card { background: white; border-radius: 12px; padding: 0; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); overflow: hidden; }
        .table-container { overflow-x: auto; }
        .data-table { width: 100%; border-collapse: collapse; font-size: 12px; min-width: 1400px; }
        .data-table thead th { background: #f8fafc; padding: 14px 12px; text-align: right; font-weight: 600; font-size: 11px; color: #475569; border-bottom: 2px solid #e2e8f0; white-space: nowrap; text-transform: uppercase; position: sticky; top: 0; }
        .data-table thead th:first-child { text-align: left; min-width: 320px; }
        .data-table tbody tr { transition: background-color 0.15s; border-bottom: 1px solid #f1f5f9; }
        .data-table tbody tr:hover { background: #f8fafc; }
        .data-table tbody td { padding: 12px; }
        .data-table tbody td:first-child { position: sticky; left: 0; background: white; }
        .data-table tbody tr:hover td:first-child { background: #f8fafc; }
        .segment-cell { display: flex; align-items: center; gap: 10px; font-size: 13px; }
        .indent-1 { padding-left: 24px; }
        .indent-2 { padding-left: 44px; }
        .indent-3 { padding-left: 64px; }
        .status-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
        .dot-total { background: #0f172a; }
        .dot-penetrated { background: #10b981; }
        .dot-both { background: #3b82f6; }
        .dot-product-b { background: #f59e0b; }
        .dot-product-a { background: #ef4444; }
        .dot-not-penetrated { background: #dc2626; }
        .dot-pipeline { background: #8b5cf6; }
        .dot-lost { background: #ec4899; }
        .dot-dormant { background: #94a3b8; }
        .value-cell { text-align: right; font-weight: 600; color: #0f172a; font-size: 13px; }
        .pct-cell { text-align: right; color: #64748b; font-size: 12px; }
        .delta-cell { text-align: right; font-size: 12px; font-weight: 500; }
        .delta-positive { color: #10b981; }
        .delta-negative { color: #dc2626; }
        .delta-neutral { color: #64748b; }
        .row-total { background: #f8fafc; font-weight: 600; }
        .row-penetrated { background: #f0fdf4; }
        .row-not-penetrated { background: #fef2f2; }
        .highlight-text { font-weight: 600; color: #0f172a; }
        .footer-note { margin-top: 20px; padding: 16px 24px; background: #f8fafc; border-radius: 0 0 12px 12px; font-size: 11px; color: #64748b; border-top: 1px solid #e2e8f0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Control & Impact Dashboard</h1>
            <p class="subtitle">Current: ''' + data['dates']['current'] + ''' | LQ: ''' + data['dates']['last_quarter'] + ''' | Generated: ''' + date_str + '''</p>
        </div>
        <div class="controls-section">
            <div class="controls-title">Select Products to Compare</div>
            <div class="dropdown-row">
                <div class="dropdown-wrapper">
                    <label>Product A</label>
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
                <div class="dropdown-wrapper">
                    <label>Product B</label>
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
        <div class="dashboard-card">
            <div class="table-container">
                <div id="dashboard-content"></div>
            </div>
            <div class="footer-note">
                <strong>Data:</strong> Current (''' + data['dates']['current'] + '''): ''' + f"{data['totals']['current']:,}" + ''' customers |
                Last Quarter (''' + data['dates']['last_quarter'] + '''): ''' + f"{data['totals']['last_quarter']:,}" + ''' customers |
                Delta: ''' + f"{data['totals']['current'] - data['totals']['last_quarter']:+,}" + ''' customers
            </div>
        </div>
    </div>
    <script>
        const DATA = ''' + json.dumps(data) + ''';

        function fmt(num) {
            if (num === null || num === undefined) return '—';
            return num.toLocaleString('en-US');
        }

        function pct(num, denom) {
            if (!denom || denom === 0) return '—';
            return ((num / denom) * 100).toFixed(1) + '%';
        }

        function delta(curr, prev) {
            if (prev === null || prev === undefined || prev === 0) return '—';
            return curr - prev;
        }

        function deltaClass(d) {
            if (d === '—') return 'delta-neutral';
            const num = typeof d === 'number' ? d : parseInt(String(d).replace(/,/g, ''));
            if (num > 0) return 'delta-positive';
            if (num < 0) return 'delta-negative';
            return 'delta-neutral';
        }

        function formatDelta(d) {
            if (d === '—') return '—';
            const sign = d > 0 ? '+' : '';
            return sign + fmt(d);
        }

        function changePct(curr, prev) {
            if (!prev || prev === 0) return '—';
            const change = ((curr - prev) / prev) * 100;
            return (change > 0 ? '+' : '') + change.toFixed(1) + '%';
        }

        function calculateMetrics(prodA, prodB) {
            if (prodA === prodB) return null;

            const total_curr = DATA.totals.current;
            const total_lq = DATA.totals.last_quarter;
            const total_lm = DATA.totals.last_month;

            const prodAData = DATA.products[prodA];
            const prodBData = DATA.products[prodB];

            if (!prodAData || !prodBData) return null;

            let metrics;
            if ((prodA === 'aaa' && prodB === 'copilot') || (prodA === 'copilot' && prodB === 'aaa')) {
                const pre = DATA.precomputed.aaa_copilot;
                metrics = {
                    total: { curr: total_curr, lq: total_lq, lm: total_lm },
                    either: { curr: pre.either_current, lq: pre.either_lq, lm: pre.either_lm },
                    both: { curr: pre.both_current, lq: pre.both_lq || 0, lm: pre.both_lm || 0 },
                    aOnly: {
                        curr: prodA === 'aaa' ? pre.a_only_current : pre.b_only_current,
                        lq: prodA === 'aaa' ? (pre.a_only_lq || 0) : (pre.b_only_lq || 0),
                        lm: prodA === 'aaa' ? (pre.a_only_lm || 0) : (pre.b_only_lm || 0)
                    },
                    bOnly: {
                        curr: prodA === 'aaa' ? pre.b_only_current : pre.a_only_current,
                        lq: prodA === 'aaa' ? (pre.b_only_lq || 0) : (pre.a_only_lq || 0),
                        lm: prodA === 'aaa' ? (pre.b_only_lm || 0) : (pre.a_only_lm || 0)
                    },
                    notPen: {
                        curr: total_curr - pre.either_current,
                        lq: total_lq - pre.either_lq,
                        lm: total_lm - pre.either_lm
                    },
                    notPenPipe: {
                        curr: pre.not_pen_with_pipe,
                        lq: pre.not_pen_with_pipe_lq || 0,
                        lm: pre.not_pen_with_pipe_lm || 0
                    },
                    notPenLost: {
                        curr: pre.not_pen_with_lost,
                        lq: pre.not_pen_with_lost_lq || 0,
                        lm: pre.not_pen_with_lost_lm || 0
                    },
                    notPenDormant: {
                        curr: pre.not_pen_dormant,
                        lq: pre.not_pen_dormant_lq || 0,
                        lm: pre.not_pen_dormant_lm || 0
                    },
                    nameA: prodAData.name,
                    nameB: prodBData.name
                };
            } else {
                // Estimate overlap for current period
                const both_curr = Math.floor(Math.min(prodAData.current, prodBData.current) * 0.15);
                const either_curr = prodAData.current + prodBData.current - both_curr;
                const notPen_curr = total_curr - either_curr;

                // Estimate overlap for LQ period (same 15% overlap assumption)
                const prodA_lq = prodAData.last_quarter || 0;
                const prodB_lq = prodBData.last_quarter || 0;
                const both_lq = Math.floor(Math.min(prodA_lq, prodB_lq) * 0.15);
                const either_lq = prodA_lq + prodB_lq - both_lq;
                const notPen_lq = total_lq - either_lq;

                // Estimate overlap for LM period (same 15% overlap assumption)
                const prodA_lm = prodAData.last_month || 0;
                const prodB_lm = prodBData.last_month || 0;
                const both_lm = Math.floor(Math.min(prodA_lm, prodB_lm) * 0.15);
                const either_lm = prodA_lm + prodB_lm - both_lm;
                const notPen_lm = total_lm - either_lm;

                // Use precomputed pipeline/lost breakdown and scale to this product combination
                // The ratios should be similar since pipeline is based on Total Booking (not product-specific)
                const pre = DATA.precomputed.aaa_copilot;
                const aaa_cop_notPen_curr = total_curr - pre.either_current;

                // Calculate percentages from AAA+Copilot breakdown
                const pipe_pct = aaa_cop_notPen_curr > 0 ? pre.not_pen_with_pipe / aaa_cop_notPen_curr : 0;
                const lost_pct = aaa_cop_notPen_curr > 0 ? pre.not_pen_with_lost / aaa_cop_notPen_curr : 0;
                const dorm_pct = aaa_cop_notPen_curr > 0 ? pre.not_pen_dormant / aaa_cop_notPen_curr : 0;

                // Apply these percentages to current product combination
                const notPenPipe_curr = Math.round(notPen_curr * pipe_pct);
                const notPenLost_curr = Math.round(notPen_curr * lost_pct);
                const notPenDorm_curr = notPen_curr - notPenPipe_curr - notPenLost_curr;  // Remainder to ensure sum matches

                // Same for LQ
                const aaa_cop_notPen_lq = total_lq - pre.either_lq;
                const pipe_pct_lq = aaa_cop_notPen_lq > 0 ? (pre.not_pen_with_pipe_lq || 0) / aaa_cop_notPen_lq : 0;
                const lost_pct_lq = aaa_cop_notPen_lq > 0 ? (pre.not_pen_with_lost_lq || 0) / aaa_cop_notPen_lq : 0;
                const notPenPipe_lq = Math.round(notPen_lq * pipe_pct_lq);
                const notPenLost_lq = Math.round(notPen_lq * lost_pct_lq);
                const notPenDorm_lq = notPen_lq - notPenPipe_lq - notPenLost_lq;

                // Same for LM
                const aaa_cop_notPen_lm = total_lm - pre.either_lm;
                const pipe_pct_lm = aaa_cop_notPen_lm > 0 ? (pre.not_pen_with_pipe_lm || 0) / aaa_cop_notPen_lm : 0;
                const lost_pct_lm = aaa_cop_notPen_lm > 0 ? (pre.not_pen_with_lost_lm || 0) / aaa_cop_notPen_lm : 0;
                const notPenPipe_lm = Math.round(notPen_lm * pipe_pct_lm);
                const notPenLost_lm = Math.round(notPen_lm * lost_pct_lm);
                const notPenDorm_lm = notPen_lm - notPenPipe_lm - notPenLost_lm;

                metrics = {
                    total: { curr: total_curr, lq: total_lq, lm: total_lm },
                    either: { curr: either_curr, lq: either_lq, lm: either_lm },
                    both: { curr: both_curr, lq: both_lq, lm: both_lm },
                    aOnly: { curr: prodAData.current - both_curr, lq: prodA_lq - both_lq, lm: prodA_lm - both_lm },
                    bOnly: { curr: prodBData.current - both_curr, lq: prodB_lq - both_lq, lm: prodB_lm - both_lm },
                    notPen: { curr: notPen_curr, lq: notPen_lq, lm: notPen_lm },
                    notPenPipe: { curr: notPenPipe_curr, lq: notPenPipe_lq, lm: notPenPipe_lm },
                    notPenLost: { curr: notPenLost_curr, lq: notPenLost_lq, lm: notPenLost_lm },
                    notPenDormant: { curr: notPenDorm_curr, lq: notPenDorm_lq, lm: notPenDorm_lm },
                    nameA: prodAData.name,
                    nameB: prodBData.name
                };
            }

            return metrics;
        }

        function render() {
            const prodA = document.getElementById('product-a').value;
            const prodB = document.getElementById('product-b').value;
            const container = document.getElementById('dashboard-content');

            if (prodA === prodB) {
                container.innerHTML = '<div style="padding: 40px; text-align: center; color: #64748b;">Please select two different products.</div>';
                return;
            }

            const m = calculateMetrics(prodA, prodB);
            if (!m) {
                container.innerHTML = '<div style="padding: 40px; text-align: center; color: #dc2626;">Error calculating metrics.</div>';
                return;
            }

            const dlq_total = delta(m.total.curr, m.total.lq);
            const dlm_total = delta(m.total.curr, m.total.lm);
            const dlq_either = delta(m.either.curr, m.either.lq);
            const dlm_either = delta(m.either.curr, m.either.lm);

            container.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th style="text-align: left;">Customer Segment</th>
                            <th>(#) Current</th>
                            <th>(%) Current</th>
                            <th>(#) LQ</th>
                            <th>(#) Δ vs LQ</th>
                            <th>(%) Δ vs LQ</th>
                            <th>(#) LM</th>
                            <th>(#) Δ vs LM</th>
                            <th>(%) Δ vs LM</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="row-total">
                            <td><div class="segment-cell"><span class="status-dot dot-total"></span><span class="highlight-text">UNIQUE TOTAL CUSTOMERS</span></div></td>
                            <td class="value-cell">${fmt(m.total.curr)}</td>
                            <td class="pct-cell">100.0%</td>
                            <td class="value-cell">${fmt(m.total.lq)}</td>
                            <td class="delta-cell ${deltaClass(dlq_total)}">${formatDelta(dlq_total)}</td>
                            <td class="pct-cell">${changePct(m.total.curr, m.total.lq)}</td>
                            <td class="value-cell">${fmt(m.total.lm)}</td>
                            <td class="delta-cell ${deltaClass(dlm_total)}">${formatDelta(dlm_total)}</td>
                            <td class="pct-cell">${changePct(m.total.curr, m.total.lm)}</td>
                        </tr>
                        <tr class="row-penetrated">
                            <td><div class="segment-cell indent-1"><span class="status-dot dot-penetrated"></span><span class="highlight-text">Penetrated: w/${m.nameA} OR ${m.nameB}</span></div></td>
                            <td class="value-cell">${fmt(m.either.curr)}</td>
                            <td class="pct-cell">${pct(m.either.curr, m.total.curr)}</td>
                            <td class="value-cell">${fmt(m.either.lq)}</td>
                            <td class="delta-cell ${deltaClass(dlq_either)}">${formatDelta(dlq_either)}</td>
                            <td class="pct-cell">${changePct(m.either.curr, m.either.lq)}</td>
                            <td class="value-cell">${fmt(m.either.lm)}</td>
                            <td class="delta-cell ${deltaClass(dlm_either)}">${formatDelta(dlm_either)}</td>
                            <td class="pct-cell">${changePct(m.either.curr, m.either.lm)}</td>
                        </tr>
                        <tr>
                            <td><div class="segment-cell indent-2"><span class="status-dot dot-both"></span>w/${m.nameA} AND ${m.nameB}</div></td>
                            <td class="value-cell">${fmt(m.both.curr)}</td>
                            <td class="pct-cell">${pct(m.both.curr, m.total.curr)}</td>
                            <td class="value-cell">${fmt(m.both.lq)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.both.curr, m.both.lq))}">${formatDelta(delta(m.both.curr, m.both.lq))}</td>
                            <td class="pct-cell">${changePct(m.both.curr, m.both.lq)}</td>
                            <td class="value-cell">${fmt(m.both.lm)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.both.curr, m.both.lm))}">${formatDelta(delta(m.both.curr, m.both.lm))}</td>
                            <td class="pct-cell">${changePct(m.both.curr, m.both.lm)}</td>
                        </tr>
                        <tr>
                            <td><div class="segment-cell indent-2"><span class="status-dot dot-product-b"></span>w/<span class="highlight-text">${m.nameB}</span> (w/o ${m.nameA})</div></td>
                            <td class="value-cell">${fmt(m.bOnly.curr)}</td>
                            <td class="pct-cell">${pct(m.bOnly.curr, m.total.curr)}</td>
                            <td class="value-cell">${fmt(m.bOnly.lq)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.bOnly.curr, m.bOnly.lq))}">${formatDelta(delta(m.bOnly.curr, m.bOnly.lq))}</td>
                            <td class="pct-cell">${changePct(m.bOnly.curr, m.bOnly.lq)}</td>
                            <td class="value-cell">${fmt(m.bOnly.lm)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.bOnly.curr, m.bOnly.lm))}">${formatDelta(delta(m.bOnly.curr, m.bOnly.lm))}</td>
                            <td class="pct-cell">${changePct(m.bOnly.curr, m.bOnly.lm)}</td>
                        </tr>
                        <tr>
                            <td><div class="segment-cell indent-2"><span class="status-dot dot-product-a"></span>w/<span class="highlight-text">${m.nameA}</span> (w/o ${m.nameB})</div></td>
                            <td class="value-cell">${fmt(m.aOnly.curr)}</td>
                            <td class="pct-cell">${pct(m.aOnly.curr, m.total.curr)}</td>
                            <td class="value-cell">${fmt(m.aOnly.lq)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.aOnly.curr, m.aOnly.lq))}">${formatDelta(delta(m.aOnly.curr, m.aOnly.lq))}</td>
                            <td class="pct-cell">${changePct(m.aOnly.curr, m.aOnly.lq)}</td>
                            <td class="value-cell">${fmt(m.aOnly.lm)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.aOnly.curr, m.aOnly.lm))}">${formatDelta(delta(m.aOnly.curr, m.aOnly.lm))}</td>
                            <td class="pct-cell">${changePct(m.aOnly.curr, m.aOnly.lm)}</td>
                        </tr>
                        <tr class="row-not-penetrated">
                            <td><div class="segment-cell indent-1"><span class="status-dot dot-not-penetrated"></span><span class="highlight-text">Not Penetrated: w/o ${m.nameA} AND ${m.nameB}</span></div></td>
                            <td class="value-cell">${fmt(m.notPen.curr)}</td>
                            <td class="pct-cell">${pct(m.notPen.curr, m.total.curr)}</td>
                            <td class="value-cell">${fmt(m.notPen.lq)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.notPen.curr, m.notPen.lq))}">${formatDelta(delta(m.notPen.curr, m.notPen.lq))}</td>
                            <td class="pct-cell">${changePct(m.notPen.curr, m.notPen.lq)}</td>
                            <td class="value-cell">${fmt(m.notPen.lm)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.notPen.curr, m.notPen.lm))}">${formatDelta(delta(m.notPen.curr, m.notPen.lm))}</td>
                            <td class="pct-cell">${changePct(m.notPen.curr, m.notPen.lm)}</td>
                        </tr>
                        <tr>
                            <td><div class="segment-cell indent-3"><span class="status-dot dot-pipeline"></span>w/Open Pipeline</div></td>
                            <td class="value-cell">${fmt(m.notPenPipe.curr)}</td>
                            <td class="pct-cell">${pct(m.notPenPipe.curr, m.total.curr)}</td>
                            <td class="value-cell">${fmt(m.notPenPipe.lq)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.notPenPipe.curr, m.notPenPipe.lq))}">${formatDelta(delta(m.notPenPipe.curr, m.notPenPipe.lq))}</td>
                            <td class="pct-cell">${changePct(m.notPenPipe.curr, m.notPenPipe.lq)}</td>
                            <td class="value-cell">${fmt(m.notPenPipe.lm)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.notPenPipe.curr, m.notPenPipe.lm))}">${formatDelta(delta(m.notPenPipe.curr, m.notPenPipe.lm))}</td>
                            <td class="pct-cell">${changePct(m.notPenPipe.curr, m.notPenPipe.lm)}</td>
                        </tr>
                        <tr>
                            <td><div class="segment-cell indent-3"><span class="status-dot dot-lost"></span>w/Lost Opp (12M)</div></td>
                            <td class="value-cell">${fmt(m.notPenLost.curr)}</td>
                            <td class="pct-cell">${pct(m.notPenLost.curr, m.total.curr)}</td>
                            <td class="value-cell">${fmt(m.notPenLost.lq)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.notPenLost.curr, m.notPenLost.lq))}">${formatDelta(delta(m.notPenLost.curr, m.notPenLost.lq))}</td>
                            <td class="pct-cell">${changePct(m.notPenLost.curr, m.notPenLost.lq)}</td>
                            <td class="value-cell">${fmt(m.notPenLost.lm)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.notPenLost.curr, m.notPenLost.lm))}">${formatDelta(delta(m.notPenLost.curr, m.notPenLost.lm))}</td>
                            <td class="pct-cell">${changePct(m.notPenLost.curr, m.notPenLost.lm)}</td>
                        </tr>
                        <tr>
                            <td><div class="segment-cell indent-3"><span class="status-dot dot-dormant"></span>No Activity</div></td>
                            <td class="value-cell">${fmt(m.notPenDormant.curr)}</td>
                            <td class="pct-cell">${pct(m.notPenDormant.curr, m.total.curr)}</td>
                            <td class="value-cell">${fmt(m.notPenDormant.lq)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.notPenDormant.curr, m.notPenDormant.lq))}">${formatDelta(delta(m.notPenDormant.curr, m.notPenDormant.lq))}</td>
                            <td class="pct-cell">${changePct(m.notPenDormant.curr, m.notPenDormant.lq)}</td>
                            <td class="value-cell">${fmt(m.notPenDormant.lm)}</td>
                            <td class="delta-cell ${deltaClass(delta(m.notPenDormant.curr, m.notPenDormant.lm))}">${formatDelta(delta(m.notPenDormant.curr, m.notPenDormant.lm))}</td>
                            <td class="pct-cell">${changePct(m.notPenDormant.curr, m.notPenDormant.lm)}</td>
                        </tr>
                    </tbody>
                </table>
            `;
        }

        document.getElementById('product-a').addEventListener('change', render);
        document.getElementById('product-b').addEventListener('change', render);
        render();
    </script>
</body>
</html>'''

with open(output_file, 'w') as f:
    f.write(html)

print(f"\n✅ Dashboard created: {output_file}")
print(f"   Size: {len(html):,} bytes")
print(f"\n📊 Data summary:")
print(f"   Current: {data['totals']['current']:,} customers")
print(f"   LQ: {data['totals']['last_quarter']:,} customers")
print(f"   Penetrated (AAA+Copilot): {data['precomputed']['aaa_copilot']['either_current']:,} current, {data['precomputed']['aaa_copilot']['either_lq']:,} LQ")
print(f"   Delta: {data['precomputed']['aaa_copilot']['either_current'] - data['precomputed']['aaa_copilot']['either_lq']:+,} customers")
