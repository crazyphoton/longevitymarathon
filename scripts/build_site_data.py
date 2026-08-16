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
HOME = ROOT / "site" / "index.html"
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


def hm(seconds: float) -> str:
    """Seconds → h:mm."""
    m = round(seconds / 60)
    return f"{m // 60}:{m % 60:02d}"


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
    total = len(weeks)

    phase_stat = stat("Phase", "—", "Plan not started.", "stat__value")
    if current:
        in_phase = [w["week_no"] for w in weeks if w["phase"] == current["phase"]]
        phase_stat = stat(
            "Phase",
            escape(current["phase"]),
            f"Weeks {min(in_phase)}&ndash;{max(in_phase)} of {total}.",
            "stat__value",
        )
    elif done >= len(weeks):
        phase_stat = stat("Phase", "Done", f"All {total} weeks complete.", "stat__value")

    if current:
        day_num = (today - current["start"]).days + 1
        weeks_note = f"Week {current['week_no']} in progress, day {day_num}."
    elif done >= len(weeks):
        weeks_note = f"All {total} weeks complete."
    else:
        weeks_note = "Plan v3 starts Mon 17 Aug."
    weeks_stat = stat(
        "Weeks completed", f"{done} <span class='stat__value--muted'>/ {total}</span>", weeks_note
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
            f"{fmt(num(longest['distance_km']))} km &middot; {hm(num(longest.get('duration_s')))}",
            f"{note}" + (f", Week {wk}." if wk else ". Plan v3 caps long runs by time, not just distance."),
        )
    else:
        longest_stat = stat(
            "Longest run so far",
            "&mdash;",
            "Awaiting Data.",
            "stat__value mono stat__value--muted",
        )

    week_runs = [
        r for r in runs
        if current and current["start"] <= dt.date.fromisoformat(r["run_date"]) < current["start"] + dt.timedelta(days=7)
    ] if current else []
    if week_runs:
        feet_stat = stat(
            "Time on feet this week",
            hm(sum(num(r.get("duration_s")) for r in week_runs)),
            "Duration is the primary lever in plan v3; distance is context.",
        )
    else:
        feet_stat = stat(
            "Time on feet this week",
            "&mdash;",
            "Duration is the primary lever in plan v3; distance is context.",
            "stat__value mono stat__value--muted",
        )

    target_stat = stat("Target", "42.2 km / 5:00", "The fixed point.")
    readiness_stat = stat(
        "Readiness",
        "Not shown",
        "Omitted until a defensible, transparent model exists.",
        "stat__value stat__value--muted",
    )

    parts = [target_stat, phase_stat, weeks_stat, sessions_stat, feet_stat, longest_stat, readiness_stat]
    return '      <div class="stat-strip">' + "".join(parts) + "</div>"


def pre_plan_km(weeks: list[dict], runs: list[dict]) -> float:
    """Approved kilometres run before v3 Week 1 (the 10–16 Aug v2 week)."""
    start = min(w["start"] for w in weeks)
    return sum(num(r["distance_km"]) for r in runs if dt.date.fromisoformat(r["run_date"]) < start)


def pre_plan_row(pre_km: float, max_target: float) -> str:
    pct = min(100, round(pre_km / max_target * 100))
    return (
        '<div class="barchart__row">\n'
        '          <span class="barchart__label">W0</span>\n'
        f'          <span class="barchart__track"><span class="barchart__fill--actual" style="width:{pct}%"></span></span>\n'
        f'          <span class="barchart__val">{fmt(pre_km)} km run under v2</span>\n'
        "        </div>"
    )


def build_mileage(weeks: list[dict], pre_km: float = 0.0) -> str:
    max_target = max(w["target_km"] for w in weeks)
    any_actual = any(w["actual_km"] > 0 for w in weeks) or pre_km > 0

    rows = [pre_plan_row(pre_km, max_target)] if pre_km > 0 else []
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

    total = len(weeks)
    if any_actual:
        heading = f"      <h3>Planned vs. actual weekly mileage, all {total} weeks</h3>"
        intro = (
            '      <p class="text-small" style="color:var(--color-ink-faint);">Plan v3 targets with\n'
            "      actual mileage layered on as the dark inner bar. Actuals count approved, published\n"
            "      runs only, so a week can briefly show less than was really run. W0 is the 10&ndash;16 Aug\n"
            "      week run under the v2 placeholder, before v3 week numbering began.</p>"
        )
    else:
        heading = f"      <h3>Planned weekly mileage, all {total} weeks</h3>"
        intro = (
            '      <p class="text-small" style="color:var(--color-ink-faint);">Plan v3 targets, shown ahead\n'
            "      of any actual training. As weeks complete, actual mileage will be layered onto this same\n"
            "      chart rather than replacing it.</p>"
        )

    chart = '      <div class="barchart"><div class="barchart__rows">' + "".join(rows) + "</div>" + legend + "</div>"
    link = (
        '      <p class="text-small"><a href="/plan/versions/v3-current/">'
        "Full week-by-week table &amp; text equivalent &rarr;</a></p>"
    )
    return "\n".join([heading, intro, chart, link])


def current_week(weeks: list[dict], today: dt.date) -> dict | None:
    return next(
        (w for w in weeks if w["start"] <= today < w["start"] + dt.timedelta(days=7)), None
    )


# ---------------------------------------------------------------------------
# Plan v3 regions: day-level sessions, current-plan chart, weekly decisions,
# and the daily gate-status history. All read from export views; the sessions
# table replaces the previously hand-edited HTML on /dashboard/ and /plan/.
# ---------------------------------------------------------------------------

SESSION_TYPE_LABEL = {
    "rest": "Rest / mobility", "easy": "Easy run", "mlr": "Medium-long run",
    "quality": "Quality", "long": "Long run", "race": "Race",
    "shakeout": "Shakeout", "strength": "Strength", "review": "Review",
}

RUN_TYPES = {"easy", "mlr", "quality", "long", "race", "shakeout"}


def build_sessions_table(sessions: list[dict], runs: list[dict], today: dt.date,
                         week: dict | None) -> str:
    if not week:
        return (
            '      <p class="section__intro">Plan v3 starts Monday 17 August. The first week\'s\n'
            "      day-by-day sessions will appear here when it does.</p>"
        )
    start, end = week["start"], week["start"] + dt.timedelta(days=7)
    week_sessions = sorted(
        (s for s in sessions if start <= dt.date.fromisoformat(s["session_date"]) < end),
        key=lambda s: (s["session_date"], 0 if s["session_type"] != "strength" else 1),
    )
    km_by_date: dict[str, float] = {}
    for r in runs:
        km_by_date[r["run_date"]] = km_by_date.get(r["run_date"], 0) + num(r["distance_km"])

    rows = []
    for s in week_sessions:
        day = dt.date.fromisoformat(s["session_date"])
        plan_bits = []
        if s["target_km"] is not None:
            plan_bits.append(f"{fmt(num(s['target_km']))} km")
        if s["time_cap_min"]:
            plan_bits.append(f"cap {s['time_cap_min'] // 60}:{s['time_cap_min'] % 60:02d}")
        if s["fuel_target_g_h"]:
            plan_bits.append(f"fuel &ge;{fmt(num(s['fuel_target_g_h']))} g/h")
        plan_txt = ", ".join(plan_bits) if plan_bits else "&mdash;"

        is_run = s["session_type"] in RUN_TYPES
        logged = km_by_date.get(s["session_date"])
        if is_run and logged:
            status = f"<span class='mono'>{fmt(logged)} km logged</span>"
        elif day > today or (day == today and not logged):
            status = "<span class='status-badge status-badge--awaiting'>Upcoming</span>" if day > today \
                else "<span class='status-badge status-badge--awaiting'>Today</span>"
        elif is_run:
            status = "<span class='status-badge status-badge--awaiting'>Not logged</span>"
        else:
            status = "&mdash;"

        title = escape(s["title"])
        if s["milestone"]:
            title += f" <span class='status-badge'>&#9733; {escape(s['milestone'])}</span>"
        date_str = day.strftime("%a %d %b").replace(" 0", " ")
        rows.append(
            f"          <tr><td class='mono'>{date_str}</td><td>{title}</td>"
            f"<td>{plan_txt}</td><td>{status}</td></tr>"
        )

    intro = (
        f'      <p class="section__intro">Week {week["week_no"]}, {escape(week["phase"])} phase.\n'
        "      Sessions come from the day-level plan in Supabase, not a hand-edited table; run\n"
        "      status reflects approved, published runs only.</p>"
    )
    return (
        intro
        + '\n      <div class="table-scroll">\n      <table class="data-table">\n'
        + "        <thead><tr><th>Date</th><th>Session</th><th>Plan</th><th>Status</th></tr></thead>\n"
        + "        <tbody>\n" + "\n".join(rows) + "\n        </tbody>\n"
        + "      </table>\n      </div>"
    )


def build_load_table(load: list[dict], runs: list[dict], weeks: list[dict], today: dt.date) -> str:
    """Duration-first weekly load table: time on feet, longest-run duration,
    long-run share, weekly session-RPE load, amber days. Shows W0 (the v2
    week) plus every started v3 week."""
    start1 = min(w["start"] for w in weeks)
    pre = [r for r in runs if dt.date.fromisoformat(r["run_date"]) < start1]

    def row(label, target, km, minutes, longest_min, share, sload, ambers):
        return (
            f"          <tr><td class='mono'>{label}</td>"
            f"<td class='mono'>{target}</td>"
            f"<td class='mono'>{km}</td>"
            f"<td class='mono'>{minutes}</td>"
            f"<td class='mono'>{longest_min}</td>"
            f"<td class='mono'>{share}</td>"
            f"<td class='mono'>{sload}</td>"
            f"<td class='mono'>{ambers}</td></tr>"
        )

    rows = []
    if pre:
        pre_secs = sum(num(r.get("duration_s")) for r in pre)
        pre_longest = max(num(r.get("duration_s")) for r in pre)
        pre_km_total = sum(num(r["distance_km"]) for r in pre)
        pre_share = round(max(num(r["distance_km"]) for r in pre) / pre_km_total * 100) if pre_km_total else 0
        rows.append(row("W0 (v2)", "&mdash;", f"{fmt(pre_km_total)} km", hm(pre_secs),
                        hm(pre_longest), f"{pre_share}%", "&mdash;", "&mdash;"))

    for w in load:
        week_start = dt.date.fromisoformat(w["week_start"])
        if week_start > today:
            continue
        rows.append(row(
            f"W{w['week_no']}",
            f"{fmt(num(w['target_km']))} km",
            f"{fmt(num(w['actual_km']))} km",
            hm(num(w["run_minutes"]) * 60),
            hm(num(w["longest_run_minutes"]) * 60) if w["longest_run_minutes"] else "&mdash;",
            f"{w['long_run_share_pct']}%" if w["long_run_share_pct"] is not None else "&mdash;",
            fmt(num(w["session_load"])) if w["session_load"] is not None else "&mdash;",
            str(w["amber_days"]) if w["amber_days"] else "0",
        ))

    if not rows:
        return (
            '      <p class="section__intro">Weekly load &mdash; time on feet, longest-run\n'
            "      duration, long-run share, and internal load &mdash; will appear here once\n"
            "      plan v3 weeks start completing.</p>"
        )
    intro = (
        '      <p class="section__intro">Plan v3 is duration-led: the marathon is a\n'
        "      time-on-feet problem, so minutes and long-run share are the primary exposure\n"
        "      readouts and distance is context. Session-RPE load (effort &times; minutes,\n"
        "      summed for the week) is the internal-load backbone &mdash; it survives heat,\n"
        "      hills, and a flaky optical sensor. Amber days count the control loop's cautions;\n"
        "      symptom detail stays private.</p>"
    )
    return (
        intro
        + '\n      <div class="table-scroll">\n      <table class="data-table">\n'
        + "        <thead><tr><th>Week</th><th>Target</th><th>Run</th><th>Time on feet</th>"
        + "<th>Longest run</th><th>Long-run share</th><th>Session-RPE load</th><th>Amber days</th></tr></thead>\n"
        + "        <tbody>\n" + "\n".join(rows) + "\n        </tbody>\n"
        + "      </table>\n      </div>"
    )


def build_plan_chart(weeks: list[dict], pre_km: float = 0.0) -> str:
    max_target = max(w["target_km"] for w in weeks)
    rows = [pre_plan_row(pre_km, max_target)] if pre_km > 0 else []
    for w in weeks:
        pct = round(w["target_km"] / max_target * 100)
        fill = "barchart__fill barchart__fill--cutback" if w["is_cutback"] else "barchart__fill"
        track = f'<span class="{fill}" style="width:{pct}%"></span>'
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
        '<span><span class="legend-swatch" style="background:#26221c;opacity:.7"></span>Actual (approved runs)</span>'
        "</div>"
    )
    return ('      <div class="barchart"><div class="barchart__rows">'
            + "".join(rows) + "</div>" + legend + "</div>")


def build_decisions(decisions: list[dict], weeks: list[dict]) -> str:
    if not decisions:
        return (
            '      <p class="section__intro">No weekly decisions recorded yet under plan v3.\n'
            "      One entry lands here at the end of every training week: the status call, the\n"
            "      single lever changed (or held), and the one-sentence rationale &mdash; including\n"
            "      the boring weeks where the decision is simply &ldquo;proceed&rdquo;.</p>"
        )
    items = []
    for d in sorted(decisions, key=lambda x: -x["week_no"]):
        week = next((w for w in weeks if w["week_no"] == d["week_no"]), None)
        date = dt.date.fromisoformat(d["decided_on"]).strftime("%d %b %Y").lstrip("0")
        phase = f", {escape(week['phase'])} phase" if week else ""
        body = f"<p>{escape(d['rationale'])}</p>"
        if d.get("lever"):
            body += f"<p><strong>Lever:</strong> {escape(d['lever'])}</p>"
        if d.get("what_went_right"):
            body += f"<p><strong>Went right:</strong> {escape(d['what_went_right'])}</p>"
        if d.get("data_confidence"):
            body += f"<p class='text-small'>Data confidence: {escape(d['data_confidence'])}.</p>"
        items.append(
            '        <li class="timeline__item">\n'
            f'          <div class="timeline__date">{date}</div>\n'
            f'          <div class="timeline__title">Week {d["week_no"]}{phase}: {escape(d["decision"])}</div>\n'
            f"          <div>{body}</div>\n"
            "        </li>"
        )
    return '      <ul class="timeline">\n' + "\n".join(items) + "\n      </ul>"


STATUS_LABEL = {
    "green": ("G", "Green"), "green_easy": ("G&#8209;", "Green-easy (wearable-only signal)"),
    "amber_life": ("A", "Amber (life)"), "amber_tissue": ("A!", "Amber (tissue)"),
    "red_reported": ("R", "Red reported"),
}


def build_status_history(statuses: list[dict], today: dt.date) -> str:
    recent = [s for s in statuses if dt.date.fromisoformat(s["day"]) > today - dt.timedelta(days=14)]
    if not recent:
        return (
            '      <p class="section__intro">Daily green/amber/red gate statuses will appear here\n'
            "      once the plan v3 control loop has data. Statuses are computed from the same rules\n"
            "      the training decisions use; symptom detail stays private.</p>"
        )
    cells = []
    for s in sorted(recent, key=lambda x: x["day"]):
        day = dt.date.fromisoformat(s["day"])
        short, label = STATUS_LABEL.get(s["status"], ("?", s["status"]))
        color = {"G": "#3e6e64", "G&#8209;": "#7a9a90", "A": "#97552f", "A!": "#97552f", "R": "#8b2f22"}.get(short, "#999")
        cells.append(
            f'<span title="{day.strftime("%a %d %b")}: {label}" '
            f'style="display:inline-block;width:1.5rem;height:1.5rem;line-height:1.5rem;'
            f'text-align:center;border-radius:4px;background:{color};color:#fff;'
            f'font-size:.72rem;font-weight:700;">{short}</span>'
        )
    return (
        '      <p class="section__intro">The last two weeks of daily gate statuses from the\n'
        "      adaptive control loop &mdash; green (execute as planned), green-easy (wearable-only\n"
        "      signal: run easy, no quality), amber (hold or reduce), red (stop; reported symptoms\n"
        "      only, never a wearable verdict). Symptom detail stays private; the status is the\n"
        "      public record.</p>\n"
        '      <div style="display:flex;gap:.3rem;flex-wrap:wrap;">' + "".join(cells) + "</div>"
    )


def build_home_glance(weeks: list[dict], today: dt.date) -> str:
    cur = current_week(weeks, today)
    done = sum(1 for w in weeks if w["start"] + dt.timedelta(days=7) <= today)
    total = len(weeks)
    if cur:
        status_value = f"Week {cur['week_no']} of {total}"
        status_note = f"{escape(cur['phase'])} phase &middot; plan v3, effective 17 Aug 2026"
    elif done >= len(weeks):
        status_value = "Complete"
        status_note = f"All {total} weeks done &middot; training started 10 Aug 2026"
    else:
        status_value = f"Week 0 of {total}"
        status_note = "Plan v3 starts Mon 17 Aug 2026; training began 10 Aug under v2"

    parts = [
        stat(
            "Event",
            "BYD Singapore Marathon 2026",
            "4 December 2026 &mdash; race day, Week 16 of the plan.",
            "stat__value",
        ),
        stat("Goal", "42.2 km in 5:00", "The one number the project is judged against."),
        stat(
            "Scope",
            "Four months",
            "Foundation through taper, race day, and an immediate retrospective.",
            "stat__value",
        ),
        stat("Status", status_value, status_note),
        stat(
            "Collaborators",
            "Author &amp; Dr. Varun Reddy",
            "Informed non-expert runner and sports-medicine / research collaborator.",
            "stat__value stat__value--muted",
        ),
    ]
    return '      <div class="stat-strip">' + "".join(parts) + "</div>"


def build_home_progress(weeks: list[dict], runs: list[dict], today: dt.date) -> str:
    cur = current_week(weeks, today)
    done = sum(1 for w in weeks if w["start"] + dt.timedelta(days=7) <= today)

    if cur:
        day_num = (today - cur["start"]).days + 1
        logged = cur["sessions_logged"]
        if logged == 0 and done == 0:
            intro = (
                f"Day {day_num} of Week {cur['week_no']}. Nothing has been run yet under the\n"
                "      current plan, so this strip mostly shows zeros and a target &mdash; that's what\n"
                "      the start of a sixteen-week plan looks like."
            )
        else:
            intro = (
                f"Day {day_num} of Week {cur['week_no']}, {escape(cur['phase'])} phase. "
                f"{logged} of {cur['sessions_planned']} planned sessions and "
                f"{fmt(cur['actual_km'])} of {fmt(cur['target_km'])} km logged so far this week."
            )
        weeks_note = f"Week {cur['week_no']} in progress."
        sessions_value = (
            f"{logged} <span class='stat__value--muted'>/ {cur['sessions_planned']} planned</span>"
        )
        sessions_note = f"Mon&ndash;Sun, {escape(cur['phase'])} phase."
        if cur["actual_km"] > 0:
            mileage_value = f"{fmt(cur['actual_km'])} <span class='stat__value--muted'>/ {fmt(cur['target_km'])} km</span>"
            mileage_class = "stat__value mono"
            mileage_note = f"Week {cur['week_no']} target vs. approved, published runs."
        else:
            mileage_value = "&mdash;"
            mileage_class = "stat__value mono stat__value--muted"
            mileage_note = f"Target for Week {cur['week_no']}: {fmt(cur['target_km'])} km. Actual: awaiting the week's close."
    else:
        intro = (
            "The sixteen-week plan is complete."
            if done >= len(weeks)
            else "Plan v3 starts Monday 17 August; last week's running happened under the v2 placeholder."
        )
        weeks_note = "&mdash;"
        sessions_value, sessions_note = "&mdash;", "No plan week in progress."
        mileage_value, mileage_class, mileage_note = (
            "&mdash;",
            "stat__value mono stat__value--muted",
            "No plan week in progress.",
        )

    if runs:
        longest = max(runs, key=lambda r: num(r["distance_km"]))
        run_date = dt.date.fromisoformat(longest["run_date"])
        wk = next(
            (w["week_no"] for w in weeks if w["start"] <= run_date < w["start"] + dt.timedelta(days=7)),
            None,
        )
        date_str = run_date.strftime("%a %d %b").replace(" 0", " ")
        longest_stat = stat(
            "Longest run so far",
            f"{fmt(num(longest['distance_km']))} km",
            f"{date_str}" + (f", Week {wk}." if wk else "."),
        )
    else:
        longest_stat = stat(
            "Longest run so far",
            "&mdash;",
            "Awaiting Data &mdash; first long run is Saturday.",
            "stat__value mono stat__value--muted",
        )

    parts = [
        stat("Weeks completed", f"{done} <span class='stat__value--muted'>/ {len(weeks)}</span>", weeks_note),
        stat("Sessions this week", sessions_value, sessions_note),
        stat("Weekly mileage", mileage_value, mileage_note, mileage_class),
        longest_stat,
        stat(
            "Target",
            "42.2 km / 5:00",
            "The fixed point everything else is measured against.",
        ),
    ]
    return (
        f'      <p class="section__intro">{intro}</p>\n'
        + '      <div class="stat-strip">'
        + "".join(parts)
        + "</div>"
    )


# ---------------------------------------------------------------------------
# Health pages (Garmin-fed markers: VO2 max, resting HR, sleep).
# Non-Garmin markers (weight, strength, BP, glucose, bloodwork, body comp)
# stay Awaiting Data until metric_reading rows exist.
# ---------------------------------------------------------------------------

METHODOLOGY_ACTION = (
    '        <div class="state-card__actions"><a class="text-link text-link--arrow" '
    'href="/dashboard/methodology/">Read the measurement methodology</a></div>'
)


def d_short(day: dt.date) -> str:
    return day.strftime("%d %b").lstrip("0")


def d_long(day: dt.date) -> str:
    return day.strftime("%a %d %b %Y").replace(" 0", " ")


def state_card(kicker: str, heading: str, rows: list[tuple[str, str]]) -> str:
    dl = "\n".join(f"          <dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    return (
        '      <div class="state-card">\n'
        f'        <div class="state-card__kicker">{kicker}</div>\n'
        f"        <h3>{heading}</h3>\n"
        "        <dl>\n"
        f"{dl}\n"
        "        </dl>\n"
        f"{METHODOLOGY_ACTION}\n"
        "      </div>"
    )


AWAITING_CARDS = {
    "vo2-max": state_card(
        "Awaiting Data",
        "No readings recorded yet",
        [
            ("What will appear here", "The maximum rate at which the body can take up and use oxygen during hard exercise, usually expressed in millilitres of oxygen per kilogram of body weight per minute (mL/kg/min)."),
            ("Why it matters", "It's one of the better single predictors of cardiorespiratory fitness and is associated with long-term health outcomes in population research &mdash; and it's the marker most directly targeted by an endurance training block."),
            ("Current status", "No readings have been recorded for this project yet."),
            ("What unlocks it", "Garmin needs a handful of outdoor runs with heart-rate data before it will produce an estimate. The first one should appear during the Foundation phase."),
        ],
    ),
    "resting-heart-rate": state_card(
        "Awaiting Data",
        "No readings recorded yet",
        [
            ("What will appear here", "Heart rate at rest, typically measured first thing in the morning or overnight during sleep."),
            ("Why it matters", "A relatively accessible, low-burden signal of cardiovascular fitness and recovery status &mdash; and one of the more common ways training adaptation is discussed outside a lab."),
            ("Current status", "No readings have been recorded for this project yet."),
            ("What unlocks it", "Passive &mdash; it accumulates automatically once the watch is worn overnight. A first weekly average will appear after Week 1."),
        ],
    ),
    "sleep": state_card(
        "Awaiting Data",
        "No readings recorded yet",
        [
            ("What will appear here", "Sleep duration and Garmin's staging estimate (light / deep / REM), plus a subjective sleep-quality note."),
            ("Why it matters", "Sleep is both a recovery input to training and a confound for nearly every other marker on this dashboard &mdash; it needs to be visible on its own, not just implied."),
            ("Current status", "No readings have been recorded for this project yet."),
            ("What unlocks it", "Accumulates passively; a first weekly summary will appear after Week 1."),
        ],
    ),
}


def health_series(daily: list[dict]) -> dict:
    days = sorted(daily, key=lambda r: r["day"])
    vo2 = [(dt.date.fromisoformat(r["day"]), num(r["vo2max_run"])) for r in days if r["vo2max_run"] is not None]
    rhr = [(dt.date.fromisoformat(r["day"]), int(r["resting_hr"])) for r in days if r["resting_hr"] is not None]
    sleep = [
        (dt.date.fromisoformat(r["day"]), int(r["sleep_seconds"]), r["sleep_score"])
        for r in days
        if r["sleep_seconds"] is not None
    ]
    hrv = [
        (dt.date.fromisoformat(r["day"]), int(r["hrv_last_night"]))
        for r in days
        if r.get("hrv_last_night") is not None
    ]
    return {"vo2": vo2, "rhr": rhr, "sleep": sleep, "hrv": hrv}


def last7(series: list[tuple], today: dt.date) -> list[tuple]:
    return [x for x in series if x[0] > today - dt.timedelta(days=7)]


def build_vo2_card(s: dict, today: dt.date) -> str:
    if not s["vo2"]:
        return AWAITING_CARDS["vo2-max"]
    day, v = s["vo2"][-1]
    recent = " &middot; ".join(f"{d_short(d)} &mdash; {val:.1f}" for d, val in s["vo2"][-5:])
    return state_card(
        "Tracking &middot; Garmin device estimate",
        f'<span class="mono">{v:.1f}</span> mL/kg/min',
        [
            ("Latest", f"{v:.1f} mL/kg/min &mdash; {d_long(day)}, Garmin estimate."),
            ("Recent estimates", recent),
            ("How to read it", "A device model, not a lab measurement &mdash; day-to-day moves are mostly noise; the trend across weeks is the signal. A laboratory value, if one is obtained, will be reported separately and never merged."),
        ],
    )


def build_rhr_card(s: dict, today: dt.date) -> str:
    if not s["rhr"]:
        return AWAITING_CARDS["resting-heart-rate"]
    day, v = s["rhr"][-1]
    week = last7(s["rhr"], today)
    vals = [x[1] for x in week]
    week_line = (
        f"avg {round(sum(vals) / len(vals))} bpm &middot; range {min(vals)}&ndash;{max(vals)} bpm "
        f"({len(vals)} of 7 days recorded)"
    ) if vals else "&mdash;"
    rows = [
        ("Latest", f"{v} bpm &mdash; {d_long(day)}, measured overnight by the watch."),
        ("Last 7 days", week_line),
    ]
    if s.get("hrv"):
        hweek = [x[1] for x in last7(s["hrv"], today)]
        hday, hval = s["hrv"][-1]
        hline = f"{hval} ms last night ({d_short(hday)})"
        if hweek:
            hline += f" &middot; 7-day avg {round(sum(hweek) / len(hweek))} ms"
        rows.append(("Overnight HRV", hline + " &mdash; read as a rolling trend against a personal baseline band, never a single-day verdict."))
    rows.append(("How to read it", "Meaningful as a multi-week trend under consistent conditions. Single-day spikes usually reflect poor sleep, heat, alcohol, or stress &mdash; not a change in fitness."))
    return state_card(
        "Tracking &middot; Garmin, overnight",
        f'<span class="mono">{v}</span> bpm',
        rows,
    )


def build_sleep_card(s: dict, today: dt.date) -> str:
    if not s["sleep"]:
        return AWAITING_CARDS["sleep"]
    day, secs, score = s["sleep"][-1]
    hours = secs / 3600
    week = last7(s["sleep"], today)
    avg_h = sum(x[1] for x in week) / len(week) / 3600 if week else 0
    night = f"{d_short(day - dt.timedelta(days=1))}&ndash;{d_short(day)}"
    latest = f"{hours:.1f} h &mdash; night of {night}"
    if score is not None:
        latest += f", Garmin sleep score {score}"
    latest += "."
    return state_card(
        "Tracking &middot; Garmin, overnight",
        f'<span class="mono">{hours:.1f}</span> h last night',
        [
            ("Last night", latest),
            ("Last 7 days", f"avg {avg_h:.1f} h/night ({len(week)} of 7 nights recorded)"),
            ("How to read it", "Duration is the dependable number; Garmin's staging estimate is treated as rough. Trends matter more than any single night."),
        ],
    )


HEALTH_CARD_BUILDERS = {
    "vo2-max": build_vo2_card,
    "resting-heart-rate": build_rhr_card,
    "sleep": build_sleep_card,
}


def build_vo2_margin_status(s: dict) -> str:
    value = "Tracking" if s["vo2"] else "Awaiting Data"
    return (
        '        <div class="margin-note">\n'
        '          <span class="margin-note__label">Status</span>\n'
        f'          <span class="margin-note__value" style="font-size:0.95rem;">{value}</span>\n'
        "        </div>"
    )


# (slug, title-html, blurb) per category for the /health/ index. Garmin-fed
# slugs get a live kicker; the rest stay Awaiting Data.
HEALTH_INDEX = [
    ("Cardiorespiratory", [
        ("vo2-max", "VO&#8322; max", "One of the better single predictors of cardiorespiratory fitness and long-term health."),
    ]),
    ("Recovery", [
        ("resting-heart-rate", "Resting heart rate", "A relatively accessible, low-burden signal of cardiovascular fitness and recovery."),
        ("sleep", "Sleep", "A recovery input to training and a confound for nearly every other marker here."),
    ]),
    ("Body composition", [
        ("weight", "Weight", "The simplest, noisiest body-composition signal &mdash; read alongside fat and muscle mass."),
        ("body-composition", "Body fat &amp; muscle mass", "Where a running-heavy block might quietly cost muscle, not just fat."),
    ]),
    ("Strength", [
        ("strength", "Strength benchmarks", "The counterweight to an aerobic-only plan, logged as an exact protocol."),
    ]),
    ("Cardiometabolic", [
        ("blood-pressure", "Blood pressure", "A core cardiometabolic marker, and a plausible place to see a training effect."),
        ("glucose", "Glucose", "Endurance training can meaningfully affect glucose regulation &mdash; worth watching on its own."),
    ]),
    ("Laboratory", [
        ("bloodwork", "Selected blood tests", "Panels like lipids and inflammatory markers, beyond what a watch or cuff can measure."),
    ]),
]


def health_kickers(s: dict) -> dict:
    kickers = {}
    if s["vo2"]:
        d, v = s["vo2"][-1]
        kickers["vo2-max"] = f"{v:.1f} mL/kg/min &middot; {d_short(d)}"
    if s["rhr"]:
        week = [x[1] for x in s["rhr"][-7:]]
        kickers["resting-heart-rate"] = f"{round(sum(week) / len(week))} bpm avg (7d)"
    if s["sleep"]:
        week = s["sleep"][-7:]
        avg_h = sum(x[1] for x in week) / len(week) / 3600
        kickers["sleep"] = f"{avg_h:.1f} h/night avg (7d)"
    return kickers


def build_health_deck(s: dict) -> str:
    if not any(s.values()):
        return (
            '      <p class="article-head__deck">Nine markers, grouped by category. Every one of them is\n'
            "      Awaiting Data right now &mdash; the project is four days into Week 1 and no baseline has\n"
            "      been recorded. Each page explains what will appear, why it matters here, and what\n"
            "      unlocks it, rather than sitting empty.</p>"
        )
    return (
        '      <p class="article-head__deck">Nine markers, grouped by category. The Garmin-fed\n'
        "      markers &mdash; VO&#8322; max, resting heart rate, and sleep &mdash; are reporting live data.\n"
        "      Clinical and manual baselines are still Awaiting Data. Each page explains what appears,\n"
        "      why it matters here, and what unlocks it, rather than sitting empty.</p>"
    )


def build_health_cards(s: dict) -> str:
    kickers = health_kickers(s)
    groups = []
    for category, cards in HEALTH_INDEX:
        card_html = []
        for slug, title, blurb in cards:
            kicker = kickers.get(slug, "Awaiting Data")
            card_html.append(
                '<div class="state-card">\n'
                f'          <div class="state-card__kicker">{kicker}</div>\n'
                f'          <h3 style="font-size:1.05rem;"><a href="/health/{slug}/">{title}</a></h3>\n'
                f'          <p class="text-small" style="color:var(--color-ink-soft);">{blurb}</p>\n'
                "        </div>"
            )
        groups.append(
            f'      <h2 style="font-size:1.15rem;margin-top:2.2rem;">{category}</h2>\n'
            '      <div class="card-grid card-grid--3">'
            + "\n        ".join(card_html)
            + "</div>"
        )
    return "\n".join(groups)


def build_health_table(s: dict) -> str:
    kickers = health_kickers(s)
    awaiting = '<span class="status-badge status-badge--awaiting">Awaiting Data</span>'
    rows = []
    for category, cards in HEALTH_INDEX:
        for slug, title, _ in cards:
            status = (
                f'<span class="mono">{kickers[slug]}</span>' if slug in kickers else awaiting
            )
            rows.append(
                f"          <tr><td>{category}</td><td><a href=\"/health/{slug}/\">{title}</a></td>"
                f"<td>{status}</td></tr>"
            )
    if any(s.values()):
        intro = (
            '      <p class="section__intro">The Garmin-fed markers below are reporting live data.\n'
            "      Everything that needs a clinic, a cuff, or a gym test is still Awaiting Data &mdash;\n"
            "      an accurate state, not a broken page. Each row links to a full explanation of what\n"
            "      appears, why, and what unlocks it.</p>"
        )
    else:
        intro = (
            '      <p class="section__intro">Every marker below is Awaiting Data &mdash; the project is four\n'
            "      days into Week 1, and no baseline has been recorded yet. That's an accurate starting\n"
            "      state, not a broken page. Each row links to a full explanation of what will appear, why,\n"
            "      and what unlocks it.</p>"
        )
    return (
        intro
        + '\n      <div class="table-scroll">\n'
        + '      <table class="data-table">\n'
        + "        <thead><tr><th>Category</th><th>Marker</th><th>Status</th></tr></thead>\n"
        + "        <tbody>\n"
        + "\n".join(rows)
        + "\n        </tbody>\n"
        + "      </table>\n      </div>"
    )


def replace_region(html: str, name: str, body: str, path: Path) -> str:
    pattern = re.compile(
        rf"(<!-- data:{name}:start[^>]*-->\n)(.*?)(\n\s*<!-- data:{name}:end -->)", re.DOTALL
    )
    if not pattern.search(html):
        sys.exit(f"Marker data:{name} not found in {path}")
    return pattern.sub(lambda m: m.group(1) + body + m.group(3), html, count=1)


def main() -> None:
    raw_weeks = fetch("export_weekly_progress", "order=week_no")
    runs = fetch("export_runs", "order=run_date")
    daily = fetch("export_daily", "order=day")
    sessions = fetch("export_plan_sessions", "order=session_date")
    decisions = fetch("export_weekly_decisions", "order=week_no")
    statuses = fetch("export_daily_status", "order=day")
    load = fetch("export_weekly_load", "order=week_no")
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

    cur = current_week(weeks, today)

    html = DASHBOARD.read_text()
    html = replace_region(html, "stat-strip", build_stat_strip(weeks, runs, today), DASHBOARD)
    html = replace_region(html, "mileage", build_mileage(weeks, pre_plan_km(weeks, runs)), DASHBOARD)
    html = replace_region(html, "sessions", build_sessions_table(sessions, runs, today, cur), DASHBOARD)
    html = replace_region(html, "load", build_load_table(load, runs, weeks, today), DASHBOARD)
    html = replace_region(html, "status-history", build_status_history(statuses, today), DASHBOARD)
    DASHBOARD.write_text(html)

    plan_page = ROOT / "site" / "plan" / "index.html"
    html = plan_page.read_text()
    html = replace_region(html, "plan-current-chart", build_plan_chart(weeks, pre_plan_km(weeks, runs)), plan_page)
    html = replace_region(html, "plan-sessions", build_sessions_table(sessions, runs, today, cur), plan_page)
    html = replace_region(html, "plan-decisions", build_decisions(decisions, weeks), plan_page)
    plan_page.write_text(html)

    html = HOME.read_text()
    html = replace_region(html, "home-glance", build_home_glance(weeks, today), HOME)
    html = replace_region(html, "home-progress", build_home_progress(weeks, runs, today), HOME)
    HOME.write_text(html)

    series = health_series(daily)

    html = DASHBOARD.read_text()
    html = replace_region(html, "health-table", build_health_table(series), DASHBOARD)
    DASHBOARD.write_text(html)

    health_index = ROOT / "site" / "health" / "index.html"
    html = health_index.read_text()
    html = replace_region(html, "health-deck", build_health_deck(series), health_index)
    html = replace_region(html, "health-cards", build_health_cards(series), health_index)
    health_index.write_text(html)

    for slug, builder in HEALTH_CARD_BUILDERS.items():
        page = ROOT / "site" / "health" / slug / "index.html"
        html = page.read_text()
        html = replace_region(html, "health-current", builder(series, today), page)
        if slug == "vo2-max":
            html = replace_region(html, "health-status", build_vo2_margin_status(series), page)
        page.write_text(html)

    DATA_JSON.parent.mkdir(parents=True, exist_ok=True)
    DATA_JSON.write_text(
        json.dumps(
            {
                "as_of": today.isoformat(),
                "weeks": [{**w, "start": w["start"].isoformat()} for w in weeks],
                "runs": runs,
                "daily": daily,
                "sessions": sessions,
                "decisions": decisions,
                "statuses": statuses,
                "load": load,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Rewrote {DASHBOARD.relative_to(ROOT)} and {DATA_JSON.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
