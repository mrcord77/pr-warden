#!/usr/bin/env python3
"""PR Warden drift dashboard — render verdict_log.jsonl as a self-contained HTML page.

Usage:
    python scripts/build_drift_dashboard.py [--log verdict_log.jsonl] [--out warden_dashboard.html]

Shows every verdict the operator has issued, newest first, plus a drift-score
trend chart against the PIVOT and HALT thresholds — so you can see a project
drifting toward the halt line before it crosses it.
"""
import argparse
import html
import json
import os
import re

COLORS = {
    "PASS": "#3fb950",
    "RE-ANCHOR": "#d29922",
    "NEEDS-PROVENANCE": "#58a6ff",
    "BLOCK": "#f85149",
}


def thresholds():
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.md")
    pivot, halt = 0.35, 0.55
    if os.path.exists(cfg_path):
        txt = open(cfg_path).read()
        m = re.search(r"reanchor_threshold\s*\|\s*([0-9.]+)", txt)
        if m: pivot = float(m.group(1))
        m = re.search(r"block_threshold\s*\|\s*([0-9.]+)", txt)
        if m: halt = float(m.group(1))
    return pivot, halt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="verdict_log.jsonl")
    ap.add_argument("--out", default="warden_dashboard.html")
    args = ap.parse_args()

    entries = []
    if os.path.exists(args.log):
        for line in open(args.log, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    pivot, halt = thresholds()

    # Trend chart (chronological order)
    w, h, pad = 720, 200, 30
    pts, dots = [], []
    n = max(len(entries), 1)
    for i, e in enumerate(entries):
        x = pad + (w - 2 * pad) * (i / max(n - 1, 1))
        tds_val = e.get("tds")
        y = h - pad - (h - 2 * pad) * min(float(tds_val if tds_val is not None else 1.0), 1.0)  # escalations (null scores) plot at the top line
        pts.append(f"{x:.0f},{y:.0f}")
        c = COLORS.get(e.get("directive", ""), "#8b949e")
        dots.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="{c}"><title>{html.escape(str(e.get("pr","")))} — CDS {e.get("cds")}</title></circle>')
    ty_p = h - pad - (h - 2 * pad) * pivot
    ty_h = h - pad - (h - 2 * pad) * halt
    polyline = f'<polyline points="{" ".join(pts)}" fill="none" stroke="#8b949e" stroke-width="2"/>' if len(pts) > 1 else ""
    chart = f"""<svg viewBox="0 0 {w} {h}" style="width:100%;max-width:{w}px;background:#0d1117;border:1px solid #30363d;border-radius:8px">
<line x1="{pad}" y1="{ty_p:.0f}" x2="{w-pad}" y2="{ty_p:.0f}" stroke="#d29922" stroke-dasharray="6 4"/>
<text x="{w-pad+2}" y="{ty_p:.0f}" fill="#d29922" font-size="11" dominant-baseline="middle">RE-ANCHOR {pivot}</text>
<line x1="{pad}" y1="{ty_h:.0f}" x2="{w-pad}" y2="{ty_h:.0f}" stroke="#f85149" stroke-dasharray="6 4"/>
<text x="{w-pad+2}" y="{ty_h:.0f}" fill="#f85149" font-size="11" dominant-baseline="middle">BLOCK {halt}</text>
{polyline}{''.join(dots)}
</svg>"""

    rows = ""
    for e in reversed(entries):
        d = e.get("directive", "?")
        c = COLORS.get(d, "#8b949e")
        rows += (f'<tr><td>{html.escape(str(e.get("ts","")))}</td>'
                 f'<td>{html.escape(str(e.get("pr","")))}</td>'
                 f'<td>{e.get("bis") if e.get("bis") is not None else "—"}</td><td>{e.get("tds") if e.get("tds") is not None else "—"}</td>'
                 f'<td style="color:{c};font-weight:600">{html.escape(d)}</td>'
                 f'<td style="color:#8b949e">{html.escape(str(e.get("routing","")))}</td></tr>')
    if not entries:
        rows = '<tr><td colspan="6" style="color:#8b949e">No verdicts logged yet — run the operator in Claude Code and verdict_log.jsonl will populate.</td></tr>'

    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>PR Warden drift dashboard</title>
<style>body{{background:#010409;color:#e6edf3;font:14px/1.5 -apple-system,Segoe UI,sans-serif;max-width:860px;margin:32px auto;padding:0 16px}}
h1{{font-size:20px}} table{{width:100%;border-collapse:collapse;margin-top:16px}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid #21262d;font-size:13px}}
th{{color:#8b949e;font-weight:600}}</style></head><body>
<h1>CDLO — drift history ({len(entries)} verdict{"s" if len(entries)!=1 else ""})</h1>
<p style="color:#8b949e">Ticket-Drift Score per PR verdict against the gate thresholds. The story to watch is the trend: scores climbing toward the halt line mean the work is decoupling from declared intent even while individual changes still pass.</p>
{chart}
<table><tr><th>Timestamp</th><th>Target</th><th>BIS</th><th>TDS</th><th>Directive</th><th>Routing</th></tr>{rows}</table>
</body></html>"""
    open(args.out, "w", encoding="utf-8").write(page)
    print(f"wrote {args.out} ({len(entries)} entries)")


if __name__ == "__main__":
    main()
