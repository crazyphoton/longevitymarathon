#!/usr/bin/env python3
"""Regenerate the data-driven regions of the static site from Supabase.

Reads only the curated export views (approved/public rows), rewrites the
marked regions in site/dashboard/index.html, and writes site/data/dashboard.json.
The site remains fully static: this runs in CI (or locally), never in the
visitor's browser.

Requires: pip install requests
Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
"""

import datetime as dt
import json
import os
import re
import sys
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = ROOT / "site" / "dashboard" / "index.html"
DATA_JSON = ROOT / "site" / "data" / "dashboard.json"
TZ = ZoneInfo("Asia/Singapore")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def fetch(view: str, query: str = "") -> list[dict]:
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/{view}?{query}",
        headers={"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}"},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def num(v) -> float:
    return float(v) if v is not None else 0.0


def fmt(v: float) -> str:
    return f"{round(v, 1):g}"


def stat(label: str, value_html: str, note_html: str, value_class: str = "stat__value mono") -> str:
    return (
        '<div class="stat">\n'
        f'          <span class="stat__label">{label}</span>\n'
        f'          <span class="{value_class}">{value_html}</span>\n'
        f'          <span class="stat__note">{note_html}</span>\n'
        "        </div>"
    )


def build_stat_strip(weeks: list[dict], runs: list[dict], today: dt.date) -> str:
    current = next(
        (w for w in weeks if w["start"] <= today < w["start"] + dt.timedelta(days=7)), None
    )
    done = sum(1 for w in weeks if w["start"] + dt.timedelta(days=7) <= today)

    phase_stat = stat("Phase", "—", "Plan not started.", "stat__value")
    if current:
        in_phase = [w["week_no"] for w in weeks if w["phase"] == current["phase"]]
        phase_stat = stat(
            "Phase",
            escape(current["phase"]),
            f"Weeks {min(in_phase)}&ndash;{max(in_phase)} of 17.",
            "stat__value",
        )
    elif done >= len(weeks):
        phase_stat = stat("Phase", "Done", "All 17 weeks complete.", "stat__value")

    if current:
        day_num = (today - current["start"]).days + 1
        weeks_note = f"Week {current['week_no']} in progress, day {day_num}."
    elif done >= len(weeks):
        weeks_note = "All 17 weeks complete."
    else:
        weeks_note = "Plan starts Mon 10 Aug."
    weeks_stat = stat(
        "Weeks completed", f"{done} <span class='stat__value--muted'>/ 17</span>", weeks_note
    )

    if current:
        logged = current["sessions_logged"]
        sessions_value = (
            f"{logged} <span class='stat__value--muted'>/ {current['sessions_planned']} planned</span>"
        )
        sessions_note = (
            "Not yet logged &mdash; see below."
            if logged == 0
            else f"{fmt(current['actual_km'])} km logged so far this week."
        )
        sessions_stat = stat("Sessions this week", sessions_value, sessions_note)
    else:
        sessions_stat = stat(
            "Sessions this week",
            "&mdash;",
            "No plan week in progress.",
            "stat__value mono stat__value--muted",
        )

    if runs:
        longest = max(runs, key=lambda r: num(r["distance_km"]))
        run_date = dt.date.fromisoformat(longest["run_date"])
        wk = next(
            (w["week_no"] for w in weeks if w["start"] <= run_date < w["start"] + dt.timedelta(days=7)),
            None,
        )
        note = run_date.strftime("%a %d %b").replace(" 0", " ")
        longest_stat = stat(
            "Longest run so far",
            f"{fmt(num(longest['distance_km']))} km",
            f"{note}" + (f", Week {wk}." if wk else "."),
        )
    else:
        longest_stat = stat(
            "Longest run so far",
            "&mdash;",
            "Awaiting Data. First long run: Sat 15 Aug.",
            "stat__value mono stat__value--muted",
        )

    target_stat = stat("Target", "42.2 km / 5:00", "The fixed point.")
    readiness_stat = stat(
        "Readiness",
        "Not shown",
        "Omitted until a defensible, transparent model exists.",
        "stat__value stat__value--muted",
    )

    parts = [target_stat, phase_stat, weeks_stat, sessions_stat, longest_stat, readiness_stat]
    return '      <div class="stat-strip">' + "".join(parts) + "</div>"


def build_mileage(weeks: list[dict]) -> str:
    max_target = max(w["target_km"] for w in weeks)
    any_actual = any(w["actual_km"] > 0 for w in weeks)

    rows = []
    for w in weeks:
        pct = round(w["target_km"] / max_target * 100)
        fill_class = "barchart__fill barchart__fill--cutback" if w["is_cutback"] else "barchart__fill"
        track = f'<span class="{fill_class}" style="width:{pct}%"></span>'
        val = f"{fmt(w['target_km'])} km"
        if w["actual_km"] > 0:
            actual_pct = min(100, round(w["actual_km"] / max_target * 100))
            track += f'<span class="barchart__fill--actual" style="width:{actual_pct}%"></span>'
            val = f"{fmt(w['actual_km'])} / {fmt(w['target_km'])} km"
        rows.append(
            '<div class="barchart__row">\n'
            f'          <span class="barchart__label">W{w["week_no"]}</span>\n'
            f'          <span class="barchart__track">{track}</span>\n'
            f'          <span class="barchart__val">{val}</span>\n'
            "        </div>"
        )

    legend = (
        '<div class="barchart__legend">'
        '<span><span class="legend-swatch" style="background:#3e6e64"></span>Planned build week</span>'
        '<span><span class="legend-swatch" style="background:#9fb8b0"></span>Planned cutback week</span>'
    )
    if any_actual:
        legend += (
            '<span><span class="legend-swatch" style="background:#26221c;opacity:.7"></span>'
            "Actual (approved runs)</span>"
        )
    legend += "</div>"

    if any_actual:
        heading = "      <h3>Planned vs. actual weekly mileage, all 17 weeks</h3>"
        intro = (
            '      <p class="text-small" style="color:var(--color-ink-faint);">Plan v2 targets with\n'
            "      actual mileage layered on as the dark inner bar. Actuals count approved, published\n"
            "      runs only, so a week can briefly show less than was really run.</p>"
        )
    else:
        heading = "      <h3>Planned weekly mileage, all 17 weeks</h3>"
        intro = (
            '      <p class="text-small" style="color:var(--color-ink-faint);">Plan v2 targets, shown ahead\n'
            "      of any actual training. As weeks complete, actual mileage will be layered onto this same\n"
            "      chart rather than replacing it.</p>"
        )

    chart = '      <div class="barchart"><div class="barchart__rows">' + "".join(rows) + "</div>" + legend + "</div>"
    link = (
        '      <p class="text-small"><a href="/plan/versions/v2-current/">'
        "Full week-by-week table &amp; text equivalent &rarr;</a></p>"
    )
    return "\n".join([heading, intro, chart, link])


def replace_region(html: str, name: str, body: str) -> str:
    pattern = re.compile(
        rf"(<!-- data:{name}:start[^>]*-->\n)(.*?)(\n\s*<!-- data:{name}:end -->)", re.DOTALL
    )
    if not pattern.search(html):
        sys.exit(f"Marker data:{name} not found in {DASHBOARD}")
    return pattern.sub(lambda m: m.group(1) + body + m.group(3), html, count=1)


def main() -> None:
    raw_weeks = fetch("export_weekly_progress", "order=week_no")
    runs = fetch("export_runs", "order=run_date")
    weeks = [
        {
            "week_no": w["week_no"],
            "phase": w["phase"],
            "start": dt.date.fromisoformat(w["week_start"]),
            "target_km": num(w["target_km"]),
            "long_run_km": num(w["long_run_km"]) if w["long_run_km"] is not None else None,
            "sessions_planned": w["sessions_planned"],
            "is_cutback": w["is_cutback"],
            "actual_km": num(w["actual_km"]),
            "sessions_logged": w["sessions_logged"],
            "longest_run_km": num(w["longest_run_km"]) if w["longest_run_km"] is not None else None,
        }
        for w in raw_weeks
    ]
    today = dt.datetime.now(TZ).date()

    html = DASHBOARD.read_text()
    html = replace_region(html, "stat-strip", build_stat_strip(weeks, runs, today))
    html = replace_region(html, "mileage", build_mileage(weeks))
    DASHBOARD.write_text(html)

    DATA_JSON.parent.mkdir(parents=True, exist_ok=True)
    DATA_JSON.write_text(
        json.dumps(
            {
                "as_of": today.isoformat(),
                "weeks": [{**w, "start": w["start"].isoformat()} for w in weeks],
                "runs": runs,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Rewrote {DASHBOARD.relative_to(ROOT)} and {DATA_JSON.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
