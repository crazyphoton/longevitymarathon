#!/usr/bin/env python3
"""Generate the plan v3 seed migration (reseed: delete + insert).

The v3 DDL lives in the already-applied 20260816090000_adaptive_v3.sql and is
not regenerated. This script is the source of truth for the plan CONTENT:
plan_week and plan_session rows are generated from WEEKS below so the
day-level schedule stays consistent with Adaptive_Marathon_Plan_v3_17_Week.md
(§8). Week 1 (10–16 Aug) predates the v3 document and is adopted
retroactively — its sessions are recorded as run, not as planned. Re-run
after editing WEEKS to regenerate the migration.
"""

import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "supabase" / "migrations" / "20260816130000_v3_seventeen_weeks.sql"

W1 = dt.date(2026, 8, 10)  # Monday of Week 1 (retroactive); race Fri 4 Dec 2026 in Week 17.

# (week, phase, target_km, long_km, long_cap_min, mlr_km, cutback, quality, note, milestone)
# quality: short description used for the Thursday slot (None -> easy run).
WEEKS = [
    (2,  "Stabilize",   35, 15,   110, None, False, "4×15 s strides after easy run",
     "Baselines; capture reliability; zone anchors.", None),
    (3,  "Stabilize",   36, 16,   120, None, False, "4×15 s strides after easy run",
     "Fuel practice on runs >75 min (30–40 g/h).", None),
    (4,  "Duration",    38, 18,   130, None, False, "6×15 s strides after easy run",
     "Long run is sole progression.", "Farthest-ever long run"),
    (5,  "Absorb",      32, 14,   100, None, True,  "4×15 s strides after easy run",
     "Review trends and zone anchors. Never make up missed distance.", None),
    (6,  "Build",       39, 19,   140, None, False, "10 min steady finish on midweek run",
     "Fuel/fluid/equipment rehearsal; sweat-rate test.", "Farthest-ever long run"),
    (7,  "Build",       43, 20,   145, 10,   False, "2×8 min steady inside the medium-long run",
     "Midweek medium-long run begins — spreads load.", "Farthest-ever long run"),
    (8,  "Build",       45, 22,   160, 11,   False, "6×15 s strides after easy run",
     "Log GI, skin, foot, late mechanics. Fuel ≥40 g/h on long run.", "Farthest-ever long run"),
    (9,  "Absorb",      37, 16,   120, 10,   True,  "4×15 s strides after easy run",
     "Review aerobic and durability trends; confirm HM logistics.", None),
    (10,  "Durability",  47, 24,   170, 12,   False, "3×10 min steady with 3 min float",
     "Fuel every long run ≥50 g/h; settle race gear.", "Farthest-ever long run"),
    (11, "Tune-up",     45, 21.1, None, 12,  False, "Rest or 20 min easy jog (pre-race)",
     "Half-marathon tune-up at controlled effort. Race-morning rehearsal; result sets the marathon pacing plan.",
     "Half-marathon tune-up race"),
    (12, "Durability",  51, 26,   185, 13,   False, "6×15 s strides after easy run",
     "2×3 km at marathon effort inside the long run; fuel ≥60 g/h.", "Farthest-ever long run"),
    (13, "Absorb",      41, 19,   145, 10,   True,  "3×6 min threshold with 2 min jog",
     "Fix race-system failures. Go/no-go: choose time goal / completion / run-walk from evidence.",
     "Week 13 go/no-go decision"),
    (14, "Peak",        54, 28,   205, 14,   False, "4×15 s strides after easy run",
     "Dress rehearsal: race breakfast, kit, anti-chafe, fuel ≥60 g/h, race start time. 4–6 km continuous at marathon effort inside the long run. Finish with reserves.",
     "Dress rehearsal — the confidence anchor"),
    (15, "Consolidate", 45, 23,   170, 12,   False, "2×2 km at marathon effort",
     "Confirm race plan; strength maintenance; nothing new.", None),
    (16, "Taper",       34, 16,   120, 9,    False, "3×2 km at marathon effort",
     "Volume down, intensity maintained in small doses; protect sleep.", None),
    (17, "Race week",   16, None, None, None, False, "2×1.5 km at marathon effort (Wed)",
     "Freshness and logistics. Carb load Wed–Thu 10–12 g/kg/day. Race Fri 4 Dec.", "Race day"),
]


def q(s):
    return "'" + s.replace("'", "''") + "'" if s is not None else "null"


def n(v):
    return "null" if v is None else f"{v:g}"


RETRO_NOTE = (
    "Adopted retroactively: run 10\u201316 Aug under the starting plan\u2019s grid, before the "
    "v3 document existed. Sessions recorded as run, not as planned."
)


def week_rows():
    rows = [
        f"  ('v3', 1, 'Stabilize', '2026-08-10', 31, 12.4, 3, false, {q(RETRO_NOTE)})"
    ]
    for wk, phase, km, lng, _cap, mlr, cutback, _q, note, _m in WEEKS:
        start = W1 + dt.timedelta(weeks=wk - 1)
        runs = 3 if wk in (1, 17) else (5 if mlr else 4)
        rows.append(
            f"  ('v3', {wk}, {q(phase)}, '{start.isoformat()}', {n(km)}, {n(lng)}, "
            f"{runs}, {'true' if cutback else 'false'}, {q(note)})"
        )
    return ",\n".join(rows)


def session_rows():
    rows = []

    def add(date, stype, title, target_km=None, cap=None, detail=None,
            fuel=None, key=False, milestone=None):
        rows.append(
            f"  ('v3', '{date.isoformat()}', {q(stype)}, {q(title)}, {n(target_km)}, "
            f"{n(cap)}, {q(detail)}, {n(fuel)}, {'true' if key else 'false'}, {q(milestone)})"
        )

    # Retroactive Week 1: the runs that actually happened, recorded as such.
    add(dt.date(2026, 8, 12), "easy", "Easy run (as run)", 8.9, None, RETRO_NOTE)
    add(dt.date(2026, 8, 13), "easy", "Easy run (as run)", 9.5, None, RETRO_NOTE)
    add(dt.date(2026, 8, 16), "long", "Long run (as run)", 12.4, None, RETRO_NOTE, None, True)

    for wk, phase, km, lng, cap, mlr, cutback, quality, note, milestone in WEEKS:
        start = W1 + dt.timedelta(weeks=wk - 1)
        mon, tue, wed, thu, fri, sat, sun = (start + dt.timedelta(days=i) for i in range(7))

        if wk == 17:
            add(mon, "rest", "Rest / mobility")
            add(tue, "easy", "Easy 20–25 min + 4 strides", 4)
            add(wed, "quality", "2×1.5 km at marathon effort", 6, 40,
                "Carb load begins today: 10–12 g/kg/day Wed–Thu.")
            add(thu, "rest", "Rest (carb load continues)", detail="Race kit laid out; early night.")
            add(fri, "race", "BYD Singapore Marathon", 42.2, None,
                "Segments: 0–10 settle · 10–25 rhythm · 25–35 work · 35–42 execute. "
                "Fuel ≥60 g/h from 20–30 min. Red flag overrides participation.",
                60, True, "Race day")
            add(sat, "rest", "Recovery walk only")
            add(sun, "rest", "Recovery walk only")
            add(tue, "strength", "Strength — light activation", detail="Familiar light work only; last session before race.")
            continue

        # Monday
        add(mon, "rest", "Rest / mobility", detail="Post-long-run assessment day.")
        # Tuesday easy + strength A
        tue_km = 6 if wk <= 6 else 7
        add(tue, "easy", f"Easy {tue_km} km", tue_km)
        add(tue, "strength", "Strength A", detail="2–4 sets, 2–3 reps in reserve; no failure." if wk <= 11 else "Maintain intensity; reduced sets/accessories.")
        # Wednesday MLR or rest
        if mlr:
            mlr_detail = "Load-spreading, not load-adding; first run shortened when reducing."
            if wk == 7:
                mlr_detail = "Includes 2×8 min controlled steady (default when green). " + mlr_detail
            add(wed, "mlr", f"Medium-long run {mlr:g} km", mlr, None, mlr_detail,
                key=(wk >= 10))
        else:
            add(wed, "rest", "Rest or short easy 4–5 km")
        # Thursday quality (default when green) or easy. Week 6's steady block
        # lives inside the Wednesday MLR; Week 10 Thursday is pre-race easy.
        thu_km = 7 if wk <= 9 else 8
        is_q = quality and "strides" not in quality and wk not in (7, 11)
        if wk == 11:
            add(thu, "easy", "Rest or 20 min easy jog (pre-race)", None, None,
                "Freshness for the Sunday half; no quality this week.")
        else:
            add(thu, "quality" if is_q else "easy",
                quality if is_q else f"Easy {thu_km} km + {quality}" if quality else f"Easy {thu_km} km",
                thu_km, None,
                "Default when green; first thing removed when amber. Skipping on a green day is a recorded deviation." if is_q else None)
        # Friday rest + strength B
        add(fri, "rest", "Rest")
        add(fri, "strength", "Strength B",
            detail="Load-bearing for this plan — absence is recorded, not waved through."
            + (" Reduced lower-body volume from Week 12." if wk >= 12 else ""))
        # Saturday shakeout
        add(sat, "shakeout", "Short easy 4–5 km + strides", 4.5, None,
            "No fatigue accumulation before the long run.")
        # Sunday long run / race
        if wk == 11:
            add(sun, "race", "Half-marathon tune-up — controlled effort", 21.1, None,
                "Not all-out. Race-morning rehearsal: breakfast, kit, fuel under race stress. "
                "If amber: run as a controlled long run instead.", 50, True, milestone)
        else:
            fuel = (None if wk < 3 else 35 if wk <= 6 else 45 if wk <= 9 else 55 if wk <= 11 else 60)
            detail = note if wk in (6, 8, 10, 12, 14) else None
            mp = {12: "Includes 2×3 km at marathon effort.",
                  14: "Includes 4–6 km continuous at marathon effort.",
                  15: "Includes 2×2 km at marathon effort.",
                  16: "Includes 3×2 km at marathon effort."}.get(wk)
            d = " ".join(x for x in (detail, mp) if x) or None
            add(sun, "long", f"Long run {lng:g} km (cap {cap//60}:{cap%60:02d})", lng, cap,
                d, fuel, True, milestone if wk != 13 else None)
        if wk == 13:
            add(sun, "review", "Go/no-go review", detail=(
                "Formal decision from evidence: time goal / completion / run-walk / defer. "
                "Recorded in the weekly decision log."), key=True, milestone=milestone)
    return ",\n".join(rows)


DDL = """\
-- Plan v3 reseed: v3 becomes 17 weeks with Week 1 = Mon 10 Aug 2026
-- (retroactive; run before the v3 document existed) and race Fri 4 Dec in
-- Week 17. All other weeks keep their calendar dates and renumber +1.
-- Generated by scripts/gen_v3_migration.py — edit that script, not this file.

delete from plan_session where plan_version = 'v3';
delete from plan_week    where plan_version = 'v3';

insert into plan_week (plan_version, week_no, phase, week_start, target_km, long_run_km, sessions_planned, is_cutback, note) values
{WEEK_ROWS};

insert into plan_session (plan_version, session_date, session_type, title, target_km, time_cap_min, detail, fuel_target_g_h, is_key, milestone) values
{SESSION_ROWS};
"""


def main():
    sql = DDL.replace("{WEEK_ROWS}", week_rows()).replace("{SESSION_ROWS}", session_rows())
    OUT.write_text(sql)
    print(f"Wrote {OUT} ({len(sql.splitlines())} lines)")


if __name__ == "__main__":
    main()
