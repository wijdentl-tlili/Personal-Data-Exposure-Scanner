import json
import uuid
import os
from datetime import datetime, timezone


TOOL_NAME    = "Personal Data Exposure Scanner"
TOOL_VERSION = "1.0.0"

RISK_COLORS = {
    "LOW":      "#22c55e",   # green
    "MEDIUM":   "#f59e0b",   # amber
    "HIGH":     "#ef4444",   # red
    "CRITICAL": "#7c3aed",   # purple
}

RISK_BG = {
    "LOW":      "#f0fdf4",
    "MEDIUM":   "#fffbeb",
    "HIGH":     "#fef2f2",
    "CRITICAL": "#f5f3ff",
}


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _ensure_dir(filename: str) -> None:
    """Create parent directories if they don't exist."""
    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)


def _build_metadata(scan_id: str, timestamp: str) -> dict:
    return {
        "tool":       TOOL_NAME,
        "version":    TOOL_VERSION,
        "scan_id":    scan_id,
        "generated":  timestamp,
    }


# ---------------------------------------------------------------------------
# JSON report
# ---------------------------------------------------------------------------

def generate_json_report(data: dict, filename: str) -> bool:
    """
    Write a JSON report to `filename`.
    Returns True on success, False on failure.
    """
    try:
        _ensure_dir(filename)

        scan_id   = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        report = {
            "metadata": _build_metadata(scan_id, timestamp),
            "results":  data,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

        return True

    except OSError as e:
        print(f"[report] Could not write JSON report: {e}")
        return False


# ---------------------------------------------------------------------------
# TXT report
# ---------------------------------------------------------------------------

SEVERITY_SYMBOLS = {
    "LOW":      "[ LOW      ]",
    "MEDIUM":   "[ MEDIUM   ]",
    "HIGH":     "[ HIGH     ]",
    "CRITICAL": "[ CRITICAL ]",
}

def generate_txt_report(data: dict, filename: str) -> bool:
    """
    Write a plain-text report to `filename`.
    Returns True on success, False on failure.
    """
    try:
        _ensure_dir(filename)

        scan_id   = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        level     = data.get("risk_level", "UNKNOWN")
        score     = data.get("risk_score", 0)
        findings  = data.get("findings", [])

        severity_line = SEVERITY_SYMBOLS.get(level, f"[ {level} ]")

        lines = [
            "=" * 52,
            f"  {TOOL_NAME.upper()}",
            f"  {TOOL_VERSION}",
            "=" * 52,
            "",
            f"  Scan ID   : {scan_id}",
            f"  Generated : {timestamp}",
            "",
            "  RISK SUMMARY",
            "  " + "-" * 30,
            f"  Severity  : {severity_line}",
            f"  Score     : {score}/100",
            "",
            "  FINDINGS",
            "  " + "-" * 30,
        ]

        if findings:
            for finding in findings:
                # Strip rich markup tags for plain text (e.g. ⚠  ... (+N pts))
                clean = finding.replace("[red]", "").replace("[/red]", "") \
                               .replace("[green]", "").replace("[/green]", "")
                lines.append(f"  {clean}")
        else:
            lines.append("  No findings recorded.")

        lines += [
            "",
            "=" * 52,
            "  End of Report",
            "=" * 52,
        ]

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return True

    except OSError as e:
        print(f"[report] Could not write TXT report: {e}")
        return False


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

def generate_html_report(data: dict, filename: str) -> bool:
    """
    Write a styled HTML report to `filename`.
    Returns True on success, False on failure.
    """
    try:
        _ensure_dir(filename)

        scan_id   = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        level     = data.get("risk_level", "UNKNOWN")
        score     = data.get("risk_score", 0)
        findings  = data.get("findings", [])

        color  = RISK_COLORS.get(level, "#6b7280")
        bg     = RISK_BG.get(level, "#f9fafb")

        findings_html = "".join(
            f'<li>{f}</li>' for f in findings
        ) if findings else "<li>No findings recorded.</li>"

        # Score arc (SVG progress ring)
        radius      = 54
        circumf     = 2 * 3.14159 * radius
        dash_offset = circumf * (1 - score / 100)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Exposure Report — {timestamp}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      min-height: 100vh;
      padding: 2rem;
    }}
    .card {{
      max-width: 720px;
      margin: 0 auto;
      background: #1e293b;
      border-radius: 16px;
      padding: 2rem 2.5rem;
      box-shadow: 0 25px 60px rgba(0,0,0,0.4);
    }}
    .header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid #334155;
      padding-bottom: 1.25rem;
      margin-bottom: 1.75rem;
    }}
    .header h1 {{
      font-size: 1.25rem;
      font-weight: 700;
      color: #f8fafc;
      letter-spacing: -0.02em;
    }}
    .badge {{
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.3rem 0.75rem;
      border-radius: 99px;
      background: {color}22;
      color: {color};
      border: 1px solid {color}55;
      letter-spacing: 0.05em;
    }}
    .meta {{
      font-size: 0.78rem;
      color: #64748b;
      margin-bottom: 2rem;
    }}
    .meta span {{ margin-right: 1.5rem; }}
    .score-section {{
      display: flex;
      align-items: center;
      gap: 2rem;
      background: {bg}11;
      border: 1px solid {color}33;
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 2rem;
    }}
    .ring-wrap {{ flex-shrink: 0; }}
    .ring-wrap svg {{ display: block; }}
    .score-text {{ font-size: 1.5rem; font-weight: 800; fill: {color}; }}
    .score-label {{ font-size: 0.65rem; fill: #94a3b8; }}
    .score-info h2 {{
      font-size: 2rem;
      font-weight: 800;
      color: {color};
      line-height: 1;
      margin-bottom: 0.35rem;
    }}
    .score-info p {{
      font-size: 0.88rem;
      color: #94a3b8;
    }}
    h3 {{
      font-size: 0.9rem;
      font-weight: 600;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      margin-bottom: 0.85rem;
    }}
    ul.findings {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }}
    ul.findings li {{
      background: #0f172a;
      border: 1px solid #334155;
      border-left: 3px solid {color};
      border-radius: 8px;
      padding: 0.65rem 1rem;
      font-size: 0.88rem;
      color: #cbd5e1;
    }}
    .footer {{
      margin-top: 2rem;
      padding-top: 1rem;
      border-top: 1px solid #334155;
      font-size: 0.72rem;
      color: #475569;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h1>🔍 Personal Data Exposure Report</h1>
      <span class="badge">{level}</span>
    </div>

    <div class="meta">
      <span>🕒 {timestamp}</span>
      <span>🆔 {scan_id}</span>
    </div>

    <div class="score-section">
      <div class="ring-wrap">
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="{radius}" fill="none"
                  stroke="#1e293b" stroke-width="10"/>
          <circle cx="60" cy="60" r="{radius}" fill="none"
                  stroke="{color}" stroke-width="10"
                  stroke-dasharray="{circumf:.2f}"
                  stroke-dashoffset="{dash_offset:.2f}"
                  stroke-linecap="round"
                  transform="rotate(-90 60 60)"/>
          <text x="60" y="55" text-anchor="middle" class="score-text">{score}</text>
          <text x="60" y="70" text-anchor="middle" class="score-label">/ 100</text>
        </svg>
      </div>
      <div class="score-info">
        <h2>{level}</h2>
        <p>Risk score: <strong>{score}/100</strong></p>
        <p style="margin-top:0.5rem;font-size:0.8rem;">
          {len(findings)} finding(s) detected across all scanned targets.
        </p>
      </div>
    </div>

    <h3>Findings</h3>
    <ul class="findings">
      {findings_html}
    </ul>

    <div class="footer">
      Generated by {TOOL_NAME} v{TOOL_VERSION}
    </div>
  </div>
</body>
</html>"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        return True

    except OSError as e:
        print(f"[report] Could not write HTML report: {e}")
        return False