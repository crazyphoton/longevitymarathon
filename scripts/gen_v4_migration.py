#!/usr/bin/env python3
"""Generate the plan v4 seed migration (insert v4; v3 rows stay as history).

v4 implements the doctor's 19 Aug prescription: rebuild from 20 km/week at
+15% per week to a 50 km/week peak held for two weeks (W9-W10), then ramp
back down to race day. Calendar landmarks keep their weeks: HM tune-up W11,
go/no-go W13, dress rehearsal (reduced volume, logistics focus) W14, race
Fri 4 Dec in W17. The minimum-viable-peak fueled >=26 km long run moves to
the peak weeks — the only weeks where it fits the <=55% long-run share rule.
No strides anywhere (heel); strength is hip/core/calf/knee per the doctor,
with drop heel raises as the calf loading stretch. Re-run after editing
WEEKS to regenerate. The export views switch from v3 to v4 here too.
"""

import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "supabase" / "migrations" / "20260819150000_plan_v4_doctor_ramp.sql"

W1 = dt.date(2026, 8, 10)  # Monday of Week 1 (retroactive); race Fri 4 Dec 2026 in Week 17.

# (wk, phase, target_km, long_km, long_cap_min, mlr_km, tue_km, thu_km, sat_km,
#  thu_quality, long_fuel_g_h, note, milestone)
WEEKS = [
    (3,  "Build",     23, 12,   90,  None, 4, 5, 3, None, 30,
     "The 15% ramp begins. Fuel practice on runs >75 min (30–40 g/h). Daily stretching; flat routes.", None),
    (4,  "Build",     26, 13,   100, None, 5, 5, 3, None, 35,
     "Long run is the sole progression lever.", None),
    (5,  "Build",     30, 15,   115, None, 5, 6, 4, None, 35,
     "Hold form; strength continues; review the heel trend before progressing.", "Farthest-ever long run"),
    (6,  "Build",     35, 17,   130, None, 6, 7, 4, None, 40,
     "Fuel/fluid/equipment rehearsal; sweat-rate test.", "Farthest-ever long run"),
    (7,  "Build",     40, 20,   150, 10,   5, 4, 3, None, 45,
     "Midweek medium-long run begins — spreads load.", "Farthest-ever long run"),
    (8,  "Build",     46, 23,   170, 11,   6, 5, 3, None, 45,
     "Log GI, skin, foot, late mechanics. Fuel ≥45 g/h on the long run.", "Farthest-ever long run"),
    (9,  "Peak",      50, 26,   195, 12,   6, 5, 3, None, 55,
     "Peak week 1. The fueled ≥26 km long run — the minimum viable peak — lands here under v4.",
     "Minimum viable peak — fueled ≥26 km"),
    (10, "Peak",      50, 27,   200, 12,   6, 5, 3, None, 60,
     "Peak week 2. Fuel ≥60 g/h; settle race gear.", "Farthest-ever long run"),
    (11, "Tune-up",   43, 21.1, None, 11,  6, None, 3, None, 50,
     "Half-marathon tune-up at controlled effort. Race-morning rehearsal; result sets the marathon pacing plan.",
     "Half-marathon tune-up race"),
    (12, "Descend",   38, 18,   135, 10,   5, 4, 3, None, 60,
     "Descent begins. 2×3 km at marathon effort inside the long run; fuel ≥60 g/h.", None),
    (13, "Descend",   33, 16,   120, 8,    5, 4, 3, None, 60,
     "Go/no-go: choose time goal / completion / run-walk from evidence.", "Week 13 go/no-go decision"),
    (14, "Descend",   28, 14,   105, 6,    4, 4, 3, None, 60,
     "Dress rehearsal at reduced volume: race breakfast, kit, anti-chafe, race start time; "
     "4–6 km continuous at marathon effort; fuel ≥60 g/h.", "Dress rehearsal — the confidence anchor"),
    (15, "Taper",     24, 12,   90,  None, 4, 6, 3, "2×2 km at marathon effort", 60,
     "Confirm race plan; strength maintenance; nothing new.", None),
    (16, "Taper",     20, 10,   75,  None, 4, 6, 3, "3×2 km at marathon effort", 60,
     "Volume down, small doses of marathon effort; protect sleep.", None),
    (17, "Race week", 15, None, None, None, 4, None, None, None, 60,
     "Freshness and logistics. Carb load Wed–Thu 10–12 g/kg/day. Race Fri 4 Dec.", "Race day"),
]


def q(s):
    return "'" + s.replace("'", "''") + "'" if s is not None else "null"


def n(v):
    return "null" if v is None else f"{v:g}"


RETRO_NOTE = (
    "Adopted retroactively: run 10–16 Aug under the starting plan’s grid, before the "
    "v3 document existed. Sessions recorded as run, not as planned."
)
W2_NOTE = (
    "Doctor-advised reduce week (20–30 km band): daily stretching protocol begins; "
    "hip/core/calf/knee strength; flat routes, slopes walked. First half recorded as run."
)
STRENGTH_A = "Hip and core focus (doctor's priority). 2–4 sets, 2–3 reps in reserve; no failure."
STRENGTH_B = (
    "Calf and knee focus — drop heel raises (doctor: specifically a loading stretch). "
    "No upper body. Load-bearing for this plan — absence is recorded, not waved through."
)


def week_rows():
    rows = [
        f"  ('v4', 1, 'Stabilize', '2026-08-10', 31, 12.4, 3, false, {q(RETRO_NOTE)})",
        f"  ('v4', 2, 'Stabilize', '2026-08-17', 20, 12, 3, false, {q(W2_NOTE)})",
    ]
    for w in WEEKS:
        wk, phase, km, lng, _cap, mlr = w[0], w[1], w[2], w[3], w[4], w[5]
        note = w[11]
        start = W1 + dt.timedelta(weeks=wk - 1)
        runs = 3 if wk == 17 else (5 if mlr else 4)
        rows.append(
            f"  ('v4', {wk}, {q(phase)}, '{start.isoformat()}', {n(km)}, {n(lng)}, "
            f"{runs}, false, {q(note)})"
        )
    return ",\n".join(rows)


def session_rows():
    rows = []

    def add(date, stype, title, target_km=None, cap=None, detail=None,
            fuel=None, key=False, milestone=None):
        rows.append(
            f"  ('v4', '{date.isoformat()}', {q(stype)}, {q(title)}, {n(target_km)}, "
            f"{n(cap)}, {q(detail)}, {n(fuel)}, {'true' if key else 'false'}, {q(milestone)})"
        )

    # Retroactive Week 1: the runs that actually happened.
    add(dt.date(2026, 8, 12), "easy", "Easy run (as run)", 8.9, None, RETRO_NOTE)
    add(dt.date(2026, 8, 13), "easy", "Easy run (as run)", 9.5, None, RETRO_NOTE)
    add(dt.date(2026, 8, 16), "long", "Long run (as run)", 12.4, None, RETRO_NOTE, None, True)

    # Week 2: first half as run (v4 adopted mid-week on doctor's advice).
    add(dt.date(2026, 8, 17), "easy", "Easy run (as run)", 9.4, None,
        "Run before the v4 revision existed.")
    add(dt.date(2026, 8, 19), "easy", "Easy run (as run)", 12, None,
        "Run the morning of the doctor review; heel 3/10 at run start.")
    add(dt.date(2026, 8, 20), "rest", "Rest + daily stretching protocol",
        detail="Towel stretch, toe extension, calf on step, calf against wall — every day from here.")
    add(dt.date(2026, 8, 21), "strength", "Strength B", detail=STRENGTH_B)
    add(dt.date(2026, 8, 22), "easy", "Easy 5 km, flat", 5)
    add(dt.date(2026, 8, 23), "rest", "Rest / mobility")

    for wk, phase, km, lng, cap, mlr, tue_km, thu_km, sat_km, quality, fuel, note, milestone in WEEKS:
        start = W1 + dt.timedelta(weeks=wk - 1)
        mon, tue, wed, thu, fri, sat, sun = (start + dt.timedelta(days=i) for i in range(7))

        if wk == 17:
            add(mon, "rest", "Rest / mobility")
            add(tue, "easy", "Easy 20–25 min", 4)
            add(wed, "quality", "2×1.5 km at marathon effort", 6, 40,
                "Carb load begins today: 10–12 g/kg/day Wed–Thu.")
            add(thu, "rest", "Rest (carb load continues)", detail="Race kit laid out; early night.")
            add(fri, "race", "BYD Singapore Marathon", 42.2, None,
                "Segments: 0–10 settle · 10–25 rhythm · 25–35 work · 35–42 execute. "
                "Fuel ≥60 g/h from 20–30 min. Red flag overrides participation.",
                60, True, "Race day")
            add(sat, "rest", "Recovery walk only")
            add(sun, "rest", "Recovery walk only")
            add(tue, "strength", "Strength — light activation",
                detail="Familiar light work only; last session before race.")
            continue

        # Monday
        add(mon, "rest", "Rest / mobility", detail="Post-long-run assessment day; daily stretching.")
        # Tuesday easy + strength A
        add(tue, "easy", f"Easy {tue_km:g} km, flat", tue_km)
        add(tue, "strength", "Strength A", detail=STRENGTH_A)
        # Wednesday MLR or rest
        if mlr:
            add(wed, "mlr", f"Medium-long run {mlr:g} km", mlr, None,
                "Load-spreading, not load-adding; first run shortened when reducing.",
                key=(wk >= 9))
        else:
            add(wed, "rest", "Rest or short easy 4 km, flat")
        # Thursday: easy only (no strides while the heel is in play) except
        # taper-week marathon-effort touches and W11 pre-race freshness.
        if wk == 11:
            add(thu, "easy", "Rest or 20 min easy jog (pre-race)", None, None,
                "Freshness for the Sunday half; no quality this week.")
        elif quality:
            add(thu, "quality", quality, thu_km, None,
                "Small race-specific dose; skip on any amber.")
        else:
            add(thu, "easy", f"Easy {thu_km:g} km, flat", thu_km)
        # Friday rest + strength B
        add(fri, "rest", "Rest")
        add(fri, "strength", "Strength B", detail=STRENGTH_B)
        # Saturday short easy (no strides)
        add(sat, "shakeout", f"Short easy {sat_km:g} km, flat", sat_km, None,
            "No fatigue accumulation before the long run. No strides.")
        # Sunday long run / HM tune-up
        if wk == 11:
            add(sun, "race", "Half-marathon tune-up — controlled effort", 21.1, None,
                "Not all-out. Race-morning rehearsal: breakfast, kit, fuel under race stress. "
                "If amber: run as a controlled long run instead.", 50, True, milestone)
        else:
            mp = {12: "Includes 2×3 km at marathon effort.",
                  14: "Includes 4–6 km continuous at marathon effort."}.get(wk)
            detail = note if wk in (6, 8, 9, 10, 12, 14) else None
            d = " ".join(x for x in (detail, mp) if x) or None
            add(sun, "long", f"Long run {lng:g} km (cap {cap // 60}:{cap % 60:02d})", lng, cap,
                d, fuel, True, milestone if wk != 13 else None)
        if wk == 13:
            add(sun, "review", "Go/no-go review", detail=(
                "Formal decision from evidence: time goal / completion / run-walk / defer. "
                "Recorded in the weekly decision log."), key=True, milestone=milestone)
    return ",\n".join(rows)


DDL = """\
-- Plan v4: the doctor's ramp (19 Aug 2026 review). Rebuild from 20 km/week
-- at +15% per week to a 50 km peak held W9-W10, then ramp down to race day.
-- v3 rows are kept as history; the export views move to v4. The week 2
-- 'reduce' decision is re-tagged v4 (it is v4's founding decision).
-- Generated by scripts/gen_v4_migration.py — edit that script, not this file.

delete from plan_session where plan_version = 'v4';
delete from plan_week    where plan_version = 'v4';

insert into plan_week (plan_version, week_no, phase, week_start, target_km, long_run_km, sessions_planned, is_cutback, note) values
{WEEK_ROWS};

insert into plan_session (plan_version, session_date, session_type, title, target_km, time_cap_min, detail, fuel_target_g_h, is_key, milestone) values
{SESSION_ROWS};

update weekly_decision set plan_version = 'v4' where plan_version = 'v3' and week_no = 2;

create or replace view export_weekly_progress as
select
  p.week_no,
  p.phase,
  p.week_start,
  p.target_km,
  p.long_run_km,
  p.sessions_planned,
  p.is_cutback,
  coalesce(sum(r.distance_km), 0)          as actual_km,
  count(r.garmin_activity_id)::integer     as sessions_logged,
  max(r.distance_km)                       as longest_run_km
from plan_week p
left join export_runs r
  on r.run_date >= p.week_start and r.run_date < p.week_start + 7
where p.plan_version = 'v4'
group by p.week_no, p.phase, p.week_start, p.target_km, p.long_run_km,
         p.sessions_planned, p.is_cutback
order by p.week_no;

create or replace view export_plan_sessions as
select session_date, session_type, title, target_km, time_cap_min, detail,
       fuel_target_g_h, is_key, milestone
from plan_session
where plan_version = 'v4';

create or replace view export_weekly_decisions as
select week_no, decided_on, decision, lever, rationale, what_went_right,
       data_confidence
from weekly_decision
where plan_version = 'v4' and is_public;

create or replace view export_weekly_load as
select
  p.week_no,
  p.week_start,
  p.target_km,
  p.long_run_km                                   as target_long_km,
  p.is_cutback,
  coalesce(sum(r.distance_km), 0)                 as actual_km,
  round(coalesce(sum(r.duration_s), 0) / 60.0)    as run_minutes,
  round(coalesce(max(r.duration_s), 0) / 60.0)    as longest_run_minutes,
  max(r.distance_km)                              as longest_run_km,
  case when sum(r.distance_km) > 0
       then round(max(r.distance_km) / sum(r.distance_km) * 100)
  end                                             as long_run_share_pct,
  (select round(sum(l.session_load))
     from v_session_load l
    where l.day >= p.week_start and l.day < p.week_start + 7) as session_load,
  (select count(*)
     from v_daily_status s
    where s.day >= p.week_start and s.day < p.week_start + 7
      and s.status like 'amber%')                 as amber_days
from plan_week p
left join export_runs r
  on r.run_date >= p.week_start and r.run_date < p.week_start + 7
where p.plan_version = 'v4'
group by p.week_no, p.week_start, p.target_km, p.long_run_km, p.is_cutback
order by p.week_no;

revoke all on export_weekly_progress, export_plan_sessions,
              export_weekly_decisions, export_weekly_load
  from anon, authenticated;
"""


def main():
    sql = DDL.replace("{WEEK_ROWS}", week_rows()).replace("{SESSION_ROWS}", session_rows())
    OUT.write_text(sql)
    print(f"Wrote {OUT} ({len(sql.splitlines())} lines)")


if __name__ == "__main__":
    main()
