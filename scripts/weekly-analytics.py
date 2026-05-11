#!/usr/bin/env python3
"""
MCLA Weekly Analytics Report.

Queries PostHog (project 147029, EU cloud) and Givebutter for the previous
fully-completed Mon-Sun week (ET), builds an HTML email with W/W comparisons
and an 8-week trend, and sends it via AgentMail.

Run by GitHub Actions on Mondays at 11:00 UTC (= 7am ET in EDT, 6am ET in EST).
Cron: `0 11 * * 1`. Workflow: .github/workflows/weekly-analytics.yml.

Secrets (env vars):
  POSTHOG_API_KEY     phx_... personal API key with Query:Read + Project:Read scope
  GIVEBUTTER_API_KEY  the full token incl. the "9870|" prefix
  AGENTMAIL_API_KEY   am_us_... bearer token

Recipients: hard-coded below. Seb forwards to the MCLA board until the format is finalized.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# --- Configuration ---
POSTHOG_HOST = "https://eu.posthog.com"
POSTHOG_PROJECT_ID = 147029
AGENTMAIL_INBOX = "seb-automated@agentmail.to"
RECIPIENTS = ["sebdebandt@gmail.com"]
USER_AGENT = "MCLAReportBot/1.0 (+https://mantlecellalliance.org)"

BRAND = "#1B2A4A"
UP, DOWN, FLAT = "#2E7D32", "#C62828", "#757575"

POSTHOG_KEY = os.environ["POSTHOG_API_KEY"]
GIVEBUTTER_KEY = os.environ["GIVEBUTTER_API_KEY"]
AGENTMAIL_KEY = os.environ["AGENTMAIL_API_KEY"]

# --- Date math (works on any day of the week) ---
ET = ZoneInfo("America/New_York")
now_et = datetime.now(ET)
days_since_monday = now_et.weekday()  # 0=Mon ... 6=Sun
this_monday_et = (now_et - timedelta(days=days_since_monday)).replace(
    hour=0, minute=0, second=0, microsecond=0
)
# Reported week = the most recently completed Mon-Sun BEFORE this week's Monday.
last_monday_et = this_monday_et - timedelta(days=7)
last_sunday_et = (this_monday_et - timedelta(days=1)).replace(
    hour=23, minute=59, second=59, microsecond=0
)
prior_monday_et = last_monday_et - timedelta(days=7)
prior_sunday_et = (last_monday_et - timedelta(days=1)).replace(
    hour=23, minute=59, second=59, microsecond=0
)
# 8 weeks ending with the reported week
trend_first_monday_et = last_monday_et - timedelta(days=49)
trend_end_et = last_sunday_et


def utc_hogql(d):
    return d.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def utc_iso(d):
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


LAST_WEEK_START = utc_hogql(last_monday_et)
LAST_WEEK_END = utc_hogql(last_sunday_et)
PRIOR_WEEK_START = utc_hogql(prior_monday_et)
PRIOR_WEEK_END = utc_hogql(prior_sunday_et)
TREND_START = utc_hogql(trend_first_monday_et)
TREND_END = utc_hogql(trend_end_et)

LAST_MON_LABEL = last_monday_et.strftime("%b %-d")
LAST_SUN_LABEL = last_sunday_et.strftime("%b %-d")

print(f"Reported week:    {LAST_WEEK_START} to {LAST_WEEK_END} UTC ({LAST_MON_LABEL}-{LAST_SUN_LABEL} ET)")
print(f"Comparison week:  {PRIOR_WEEK_START} to {PRIOR_WEEK_END} UTC")
print(f"Trend window:     {TREND_START} to {TREND_END} UTC (8 weeks)")


# --- HTTP helpers (stdlib, no requests dependency) ---
def http_request(method, url, headers=None, body=None, timeout=60):
    headers = dict(headers or {})
    headers.setdefault("User-Agent", USER_AGENT)  # Cloudflare-fronted APIs (Givebutter) reject default urllib UA
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code} on {method} {url}\n{body_text}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Request error on {method} {url}: {e}", file=sys.stderr)
        raise


# --- PostHog ---
def hogql(query):
    """Run a HogQL query against PostHog project 147029. Returns the `results` array (empty on error)."""
    body = {"query": {"kind": "HogQLQuery", "query": query}}
    headers = {"Authorization": f"Bearer {POSTHOG_KEY}"}
    url = f"{POSTHOG_HOST}/api/projects/{POSTHOG_PROJECT_ID}/query/"
    try:
        return http_request("POST", url, headers, body).get("results", [])
    except Exception:
        return []


def weekly_totals(start, end):
    rows = hogql(f"""
        SELECT count() AS pageviews,
               uniq(person_id) AS unique_visitors,
               uniq(properties.$session_id) AS sessions
        FROM events
        WHERE event = '$pageview'
          AND timestamp >= toDateTime('{start}')
          AND timestamp <= toDateTime('{end}')
    """)
    if not rows:
        return {"pageviews": 0, "unique_visitors": 0, "sessions": 0}
    pv, uv, ss = rows[0]
    return {"pageviews": pv or 0, "unique_visitors": uv or 0, "sessions": ss or 0}


def trend_weeks(start, end):
    rows = hogql(f"""
        SELECT toMonday(timestamp) AS week_start, count() AS pageviews
        FROM events
        WHERE event = '$pageview'
          AND timestamp >= toDateTime('{start}')
          AND timestamp <= toDateTime('{end}')
        GROUP BY week_start
        ORDER BY week_start
    """)
    return rows


def top_pages(start, end):
    return hogql(f"""
        SELECT properties.$pathname AS pathname, count() AS pageviews
        FROM events
        WHERE event = '$pageview'
          AND timestamp >= toDateTime('{start}')
          AND timestamp <= toDateTime('{end}')
          AND properties.$pathname IS NOT NULL
        GROUP BY pathname
        ORDER BY pageviews DESC
        LIMIT 10
    """)


def top_referrers(start, end):
    return hogql(f"""
        SELECT properties.$referring_domain AS domain, count() AS pageviews
        FROM events
        WHERE event = '$pageview'
          AND timestamp >= toDateTime('{start}')
          AND timestamp <= toDateTime('{end}')
          AND properties.$referring_domain != '$direct'
          AND properties.$referring_domain IS NOT NULL
          AND properties.$referring_domain != ''
        GROUP BY domain
        ORDER BY pageviews DESC
        LIMIT 5
    """)


def top_countries(start, end):
    return hogql(f"""
        SELECT properties.$geoip_country_name AS country, uniq(person_id) AS unique_visitors
        FROM events
        WHERE event = '$pageview'
          AND timestamp >= toDateTime('{start}')
          AND timestamp <= toDateTime('{end}')
          AND properties.$geoip_country_name IS NOT NULL
        GROUP BY country
        ORDER BY unique_visitors DESC
        LIMIT 5
    """)


# --- Givebutter ---
def givebutter_week(start_iso, end_iso):
    qs = urllib.parse.urlencode(
        {"createdAfter": start_iso, "createdBefore": end_iso, "per_page": 100}
    )
    url = f"https://api.givebutter.com/v1/contacts?{qs}"
    headers = {"Authorization": f"Bearer {GIVEBUTTER_KEY}"}
    try:
        data = http_request("GET", url, headers)
    except Exception:
        return {"total": 0, "opted_in": 0, "from_website": 0, "names": []}
    contacts = data.get("data", [])
    total = data.get("meta", {}).get("total")
    if total is None:
        total = len(contacts)
    opted_in = sum(1 for c in contacts if c.get("email_opt_in"))
    from_website = sum(1 for c in contacts if "mcla-newsletter" in (c.get("tags") or []))
    names = [
        " ".join(filter(None, [c.get("first_name") or "", c.get("last_name") or ""])).strip()
        for c in contacts
    ]
    names = [n for n in names if n]
    return {"total": total, "opted_in": opted_in, "from_website": from_website, "names": names}


# --- Week-over-week helpers ---
def ww(this_val, last_val):
    """Return (arrow, color, label_text) for a W/W comparison."""
    if last_val == 0:
        if this_val == 0:
            return ("—", FLAT, "—")
        return ("▲", UP, "new")
    pct = round((this_val - last_val) / last_val * 100)
    if pct > 0:
        return ("▲", UP, f"+{pct}%")
    if pct < 0:
        return ("▼", DOWN, f"{pct}%")
    return ("—", FLAT, "0%")


def ww_html(this_val, last_val):
    arrow, color, label = ww(this_val, last_val)
    return f'<span style="color:{color};font-weight:600;">{arrow} {label}</span>'


# --- Run the queries ---
this_traffic = weekly_totals(LAST_WEEK_START, LAST_WEEK_END)
last_traffic = weekly_totals(PRIOR_WEEK_START, PRIOR_WEEK_END)
trend_rows_raw = trend_weeks(TREND_START, TREND_END)
pages_rows = top_pages(LAST_WEEK_START, LAST_WEEK_END)
refs_rows = top_referrers(LAST_WEEK_START, LAST_WEEK_END)
countries_rows = top_countries(LAST_WEEK_START, LAST_WEEK_END)
this_signups = givebutter_week(utc_iso(last_monday_et), utc_iso(last_sunday_et))
last_signups = givebutter_week(utc_iso(prior_monday_et), utc_iso(prior_sunday_et))

# Build 8-week trend, padding any missing weeks with 0
trend_dict = {}
for row in trend_rows_raw:
    if not row:
        continue
    wk, pv = row[0], row[1]
    if isinstance(wk, str):
        key = wk[:10]
    elif hasattr(wk, "strftime"):
        key = wk.strftime("%Y-%m-%d")
    else:
        key = str(wk)[:10]
    trend_dict[key] = pv or 0

trend = []
for i in range(8):
    wk_mon = trend_first_monday_et + timedelta(days=7 * i)
    key = wk_mon.strftime("%Y-%m-%d")
    label = wk_mon.strftime("%b %-d")
    trend.append((label, trend_dict.get(key, 0)))


# --- Build HTML email ---
def section_h2(title):
    return (
        f'<h2 style="color:{BRAND};font-size:16px;border-bottom:1px solid #eee;'
        f'padding-bottom:8px;margin-top:32px;">{title}</h2>'
    )


def table_open(headers):
    th = "".join(
        f'<th style="padding:8px;text-align:{"left" if i == 0 else "right"};">{h}</th>'
        for i, h in enumerate(headers)
    )
    return (
        '<table style="width:100%;border-collapse:collapse;">'
        f'<thead><tr style="background:{BRAND};color:white;">{th}</tr></thead><tbody>'
    )


TABLE_CLOSE = "</tbody></table>"


def row(cells):
    tds = "".join(
        f'<td style="padding:8px;text-align:{"left" if i == 0 else "right"};border-bottom:1px solid #f0f0f0;">{c}</td>'
        for i, c in enumerate(cells)
    )
    return f"<tr>{tds}</tr>"


def fmt(n):
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return str(n)


# Headline
pv_arrow, _, pv_label = ww(this_traffic["pageviews"], last_traffic["pageviews"])
headline = (
    f'{fmt(this_traffic["unique_visitors"])} visitors / '
    f'{fmt(this_traffic["pageviews"])} pageviews this week ({pv_label} vs last week)'
)

html_parts = [
    "<!DOCTYPE html><html><head><meta charset=\"utf-8\"></head>",
    '<body style="font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;'
    'max-width:640px;margin:0 auto;padding:24px;color:#1a1a1a;background:#fff;">',
    f'<h1 style="color:{BRAND};margin:0 0 4px 0;font-size:22px;">MCLA Weekly Report</h1>',
    f'<p style="margin:0 0 4px 0;color:#555;">Week of {LAST_MON_LABEL} to {LAST_SUN_LABEL}</p>',
    f'<p style="margin:0 0 24px 0;color:#222;font-size:14px;">{headline}</p>',
    section_h2("Topline"),
    table_open(["Metric", "This week", "Last week", "W/W"]),
]
for name, tw, lw in [
    ("Page views", this_traffic["pageviews"], last_traffic["pageviews"]),
    ("Unique visitors", this_traffic["unique_visitors"], last_traffic["unique_visitors"]),
    ("Sessions", this_traffic["sessions"], last_traffic["sessions"]),
]:
    html_parts.append(row([name, fmt(tw), fmt(lw), ww_html(tw, lw)]))
html_parts.append(TABLE_CLOSE)

# Signups
html_parts += [
    section_h2("Email signups"),
    table_open(["Type", "This week", "Last week", "W/W"]),
    row([
        "New contacts (total)",
        fmt(this_signups["total"]),
        fmt(last_signups["total"]),
        ww_html(this_signups["total"], last_signups["total"]),
    ]),
    row([
        "Email opted-in",
        fmt(this_signups["opted_in"]),
        fmt(last_signups["opted_in"]),
        ww_html(this_signups["opted_in"], last_signups["opted_in"]),
    ]),
    row([
        "Website form (mcla-newsletter tag)",
        fmt(this_signups["from_website"]),
        fmt(last_signups["from_website"]),
        ww_html(this_signups["from_website"], last_signups["from_website"]),
    ]),
    TABLE_CLOSE,
]
if 0 < this_signups["total"] <= 15 and this_signups["names"]:
    html_parts.append(
        f'<p style="margin-top:12px;font-size:14px;"><strong>New names this week:</strong> '
        f'{", ".join(this_signups["names"])}</p>'
    )

# Trend
html_parts += [
    section_h2("8-week trend (page views)"),
    table_open(["Week of", "Page views"]),
]
for label, pv in trend:
    html_parts.append(row([label, fmt(pv)]))
html_parts.append(TABLE_CLOSE)

# Top pages
html_parts += [section_h2("Top pages this week"), table_open(["Path", "Views"])]
if pages_rows:
    for path, pv in pages_rows:
        path_html = f'<span style="font-family:ui-monospace,monospace;font-size:13px;">{path}</span>'
        html_parts.append(row([path_html, fmt(pv)]))
else:
    html_parts.append(
        '<tr><td colspan="2" style="padding:8px;color:#999;">No page views recorded this week.</td></tr>'
    )
html_parts.append(TABLE_CLOSE)

# Top referrers
html_parts += [section_h2("Top referrers this week"), table_open(["Domain", "Views"])]
if refs_rows:
    for domain, pv in refs_rows:
        html_parts.append(row([domain, fmt(pv)]))
else:
    html_parts.append(
        '<tr><td colspan="2" style="padding:8px;color:#999;">No referring domains this week.</td></tr>'
    )
html_parts.append(TABLE_CLOSE)

# Top countries
html_parts += [section_h2("Top countries this week"), table_open(["Country", "Unique visitors"])]
if countries_rows:
    for country, uv in countries_rows:
        html_parts.append(row([country, fmt(uv)]))
else:
    html_parts.append(
        '<tr><td colspan="2" style="padding:8px;color:#999;">No country data this week.</td></tr>'
    )
html_parts.append(TABLE_CLOSE)

html_parts += [
    f'<p style="margin-top:32px;font-size:12px;color:#999;">'
    f"Report window: Monday {LAST_MON_LABEL} 00:00 ET → Sunday {LAST_SUN_LABEL} 23:59 ET (fully completed). "
    f"Sent Monday morning. Auto-generated from PostHog and Givebutter for mantlecellalliance.org."
    f"</p>",
    "</body></html>",
]
html = "".join(html_parts)


# --- Plain text fallback ---
text_lines = [
    f"MCLA Weekly Report — Week of {LAST_MON_LABEL} to {LAST_SUN_LABEL}",
    headline,
    "",
    "TOPLINE",
]
for name, tw, lw in [
    ("Page views", this_traffic["pageviews"], last_traffic["pageviews"]),
    ("Unique visitors", this_traffic["unique_visitors"], last_traffic["unique_visitors"]),
    ("Sessions", this_traffic["sessions"], last_traffic["sessions"]),
]:
    _, _, label = ww(tw, lw)
    text_lines.append(f"  {name}: {fmt(tw)} (vs {fmt(lw)} last week, {label})")

text_lines += ["", "EMAIL SIGNUPS"]
text_lines.append(f"  New contacts (total): {this_signups['total']} (vs {last_signups['total']})")
text_lines.append(f"  Email opted-in: {this_signups['opted_in']} (vs {last_signups['opted_in']})")
text_lines.append(f"  Website form: {this_signups['from_website']} (vs {last_signups['from_website']})")
if 0 < this_signups["total"] <= 15 and this_signups["names"]:
    text_lines.append(f"  Names: {', '.join(this_signups['names'])}")

text_lines += ["", "8-WEEK TREND (page views)"]
for label, pv in trend:
    text_lines.append(f"  {label}: {fmt(pv)}")

text_lines += ["", "TOP PAGES"]
for path, pv in pages_rows:
    text_lines.append(f"  {fmt(pv):>6}  {path}")

text_lines += ["", "TOP REFERRERS"]
for domain, pv in refs_rows:
    text_lines.append(f"  {fmt(pv):>6}  {domain}")

text_lines += ["", "TOP COUNTRIES"]
for country, uv in countries_rows:
    text_lines.append(f"  {fmt(uv):>6}  {country}")

text_lines += [
    "",
    "—",
    (
        f"Report window: Mon {LAST_MON_LABEL} 00:00 ET → Sun {LAST_SUN_LABEL} 23:59 ET. "
        "Auto-generated from PostHog and Givebutter for mantlecellalliance.org."
    ),
]
plain_text = "\n".join(text_lines)


# --- Send via AgentMail ---
subject = f"MCLA Weekly Report — Week of {LAST_MON_LABEL} to {LAST_SUN_LABEL}"
payload = {"to": RECIPIENTS, "subject": subject, "html": html, "text": plain_text}
url = f"https://api.agentmail.to/v0/inboxes/{AGENTMAIL_INBOX}/messages/send"
headers = {"Authorization": f"Bearer {AGENTMAIL_KEY}"}

try:
    resp = http_request("POST", url, headers, payload)
    msg_id = resp.get("message_id") or resp.get("id") or "(no message_id in response)"
    print(f"AgentMail send OK: {msg_id}")
    print(
        f"Summary: {fmt(this_traffic['pageviews'])} pageviews, "
        f"{fmt(this_traffic['unique_visitors'])} visitors, "
        f"{this_signups['total']} signups "
        f"(pv W/W: {ww(this_traffic['pageviews'], last_traffic['pageviews'])[2]})"
    )
except Exception as e:
    print(f"AgentMail send FAILED: {e}", file=sys.stderr)
    sys.exit(1)
