-- Adaptive plan v3 (16 weeks, race Fri 4 Dec 2026) + capture/gate schema.
-- Source of truth for the plan content: Adaptive_Marathon_Plan_v3_16_Week.md.
-- v2 seed rows are removed: v2 was a placeholder that never carried day-level
-- sessions; its public snapshot page remains for the historical record.

-- ---------------------------------------------------------------------------
-- Garmin daily: nightly HRV (verified available via garminconnect
-- get_hrv_data: lastNightAvg / weeklyAvg / status / personal baseline band).
-- ---------------------------------------------------------------------------
alter table garmin_daily
  add column if not exists hrv_last_night   integer,
  add column if not exists hrv_weekly_avg   integer,
  add column if not exists hrv_status       text,
  add column if not exists hrv_baseline_low integer,
  add column if not exists hrv_baseline_high integer;

-- ---------------------------------------------------------------------------
-- Day-level planned sessions (kills the hand-edited dashboard table).
-- ---------------------------------------------------------------------------
create table plan_session (
  plan_version  text not null,
  session_date  date not null,
  session_type  text not null check (session_type in
    ('rest','easy','mlr','quality','long','race','shakeout','strength','review')),
  title         text not null,
  target_km     numeric,
  time_cap_min  integer,
  detail        text,
  fuel_target_g_h numeric,
  is_key        boolean not null default false,
  milestone     text,
  primary key (plan_version, session_date, session_type)
);

-- ---------------------------------------------------------------------------
-- Manual capture: the four daily moments. The minimum viable dataset is
-- post_run.rpe and next_morning.issue_vs_baseline — everything else nullable.
-- ---------------------------------------------------------------------------
create table checkin (
  id            bigint generated always as identity primary key,
  local_date    date not null,
  moment        text not null check (moment in ('morning','pre_run','post_run','next_morning')),
  -- morning
  sleep_quality smallint check (sleep_quality between 1 and 5),
  energy        smallint check (energy between 1 and 5),
  mood          smallint check (mood between 1 and 5),
  soreness      smallint check (soreness between 0 and 5),
  illness       boolean,
  -- pre_run
  red_flag      boolean,
  pain_severity smallint check (pain_severity between 0 and 10),
  pain_location text,
  gait_affected boolean,
  -- post_run (rpe is the core field)
  rpe           smallint check (rpe between 1 and 10),
  completed_as_planned boolean,
  pain_trend    text check (pain_trend in ('none','improving','stable','worsening')),
  fuel_g_per_h  numeric,
  fluid_ml      integer,
  gi_score      smallint check (gi_score between 0 and 5),
  skin_foot_issue boolean,
  -- next_morning (issue_vs_baseline is the core field)
  issue_vs_baseline text check (issue_vs_baseline in ('better','baseline','worse')),
  stiffness_min integer,
  swelling      boolean,
  stairs_normal boolean,
  ready_for_easy boolean,
  note          text,
  device_confidence text check (device_confidence in ('high','medium','low')),
  created_at    timestamptz not null default now(),
  unique (local_date, moment)
);

-- ---------------------------------------------------------------------------
-- Issue register (location-specific, clinician-visible with consent).
-- ---------------------------------------------------------------------------
create table issue (
  id            bigint generated always as identity primary key,
  location      text not null,
  kind          text,
  onset_date    date not null default current_date,
  status        text not null default 'watch' check (status in ('watch','active','clinical','resolved')),
  severity      smallint check (severity between 0 and 10),
  trend         text check (trend in ('improving','stable','worsening')),
  gait_affected boolean not null default false,
  clinician_status text,
  loading_rule  text,
  resolved_at   date,
  note          text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Weekly decision log (§17): the Adapt step, one row per plan week.
-- ---------------------------------------------------------------------------
create table weekly_decision (
  plan_version  text not null,
  week_no       integer not null,
  decided_on    date not null default current_date,
  decision      text not null check (decision in ('progress','hold','reduce','substitute','review')),
  lever         text,
  rationale     text not null,
  what_went_right text,
  stop_conditions text,
  energy_availability_ok boolean,
  ea_note       text,
  data_confidence text check (data_confidence in ('high','medium','low')),
  clinician_note text,
  is_public     boolean not null default false,
  created_at    timestamptz not null default now(),
  primary key (plan_version, week_no)
);

-- ---------------------------------------------------------------------------
-- Gate rules as data so thresholds iterate without schema changes.
-- ---------------------------------------------------------------------------
create table gate_rule (
  key         text primary key,
  params      jsonb not null,
  description text not null
);

insert into gate_rule (key, params, description) values
  ('hrv_amber',        '{"consecutive_days": 3}',
   'HRV 7-day rolling mean outside the personal baseline band for >=N consecutive days, plus a symptom, is a life-amber input. Wearable-only deviation defaults to green-easy.'),
  ('rhr_amber',        '{"delta_bpm": 5, "consecutive_days": 3}',
   'Resting HR >=delta above its rolling baseline for >=N consecutive days, plus a symptom.'),
  ('decoupling_abort', '{"pct": 10}',
   'Abort MP blocks (continue easy) if back-half pace:HR decoupling exceeds pct under comparable conditions.'),
  ('pain_green_max',   '{"severity": 2}',
   'Pain above this, or any gait change, leaves green.'),
  ('stiffness_green_max', '{"minutes": 10}',
   'Next-morning stiffness above this leaves green.'),
  ('poor_sleep_amber', '{"nights": 2, "quality_max": 2, "min_seconds": 21600}',
   'N consecutive poor nights (short or low-quality) is a life-amber input.'),
  ('circuit_breaker',  '{"ambers": 3, "window_days": 7}',
   'N amber days in the window forces a structured review instead of another silent reduction.'),
  ('min_viable_peak',  '{"km": 26, "by_week": 13}',
   'At least one fueled long run >= km must be completed by end of this week.');

-- ---------------------------------------------------------------------------
-- Plan v3 seed (v2 placeholder rows removed).
-- ---------------------------------------------------------------------------
delete from plan_week where plan_version in ('v2');

insert into plan_week (plan_version, week_no, phase, week_start, target_km, long_run_km, sessions_planned, is_cutback, note) values
  ('v3', 1, 'Stabilize', '2026-08-17', 35, 15, 4, false, 'Baselines; capture reliability; zone anchors.'),
  ('v3', 2, 'Stabilize', '2026-08-24', 36, 16, 4, false, 'Fuel practice on runs >75 min (30–40 g/h).'),
  ('v3', 3, 'Duration', '2026-08-31', 38, 18, 4, false, 'Long run is sole progression.'),
  ('v3', 4, 'Absorb', '2026-09-07', 32, 14, 4, true, 'Review trends and zone anchors. Never make up missed distance.'),
  ('v3', 5, 'Build', '2026-09-14', 39, 19, 4, false, 'Fuel/fluid/equipment rehearsal; sweat-rate test.'),
  ('v3', 6, 'Build', '2026-09-21', 43, 20, 5, false, 'Midweek medium-long run begins — spreads load.'),
  ('v3', 7, 'Build', '2026-09-28', 45, 22, 5, false, 'Log GI, skin, foot, late mechanics. Fuel ≥40 g/h on long run.'),
  ('v3', 8, 'Absorb', '2026-10-05', 37, 16, 5, true, 'Review aerobic and durability trends; confirm HM logistics.'),
  ('v3', 9, 'Durability', '2026-10-12', 47, 24, 5, false, 'Fuel every long run ≥50 g/h; settle race gear.'),
  ('v3', 10, 'Tune-up', '2026-10-19', 45, 21.1, 5, false, 'Half-marathon tune-up at controlled effort. Race-morning rehearsal; result sets the marathon pacing plan.'),
  ('v3', 11, 'Durability', '2026-10-26', 51, 26, 5, false, '2×3 km at marathon effort inside the long run; fuel ≥60 g/h.'),
  ('v3', 12, 'Absorb', '2026-11-02', 41, 19, 5, true, 'Fix race-system failures. Go/no-go: choose time goal / completion / run-walk from evidence.'),
  ('v3', 13, 'Peak', '2026-11-09', 54, 28, 5, false, 'Dress rehearsal: race breakfast, kit, anti-chafe, fuel ≥60 g/h, race start time. 4–6 km continuous at marathon effort inside the long run. Finish with reserves.'),
  ('v3', 14, 'Consolidate', '2026-11-16', 45, 23, 5, false, 'Confirm race plan; strength maintenance; nothing new.'),
  ('v3', 15, 'Taper', '2026-11-23', 34, 16, 5, false, 'Volume down, intensity maintained in small doses; protect sleep.'),
  ('v3', 16, 'Race week', '2026-11-30', 16, null, 3, false, 'Freshness and logistics. Carb load Wed–Thu 10–12 g/kg/day. Race Fri 4 Dec.');

insert into plan_session (plan_version, session_date, session_type, title, target_km, time_cap_min, detail, fuel_target_g_h, is_key, milestone) values
  ('v3', '2026-08-17', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-08-18', 'easy', 'Easy 6 km', 6, null, null, null, false, null),
  ('v3', '2026-08-18', 'strength', 'Strength A', null, null, '2–4 sets, 2–3 reps in reserve; no failure.', null, false, null),
  ('v3', '2026-08-19', 'rest', 'Rest or short easy 4–5 km', null, null, null, null, false, null),
  ('v3', '2026-08-20', 'easy', 'Easy 7 km + 4×15 s strides after easy run', 7, null, null, null, false, null),
  ('v3', '2026-08-21', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-08-21', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through.', null, false, null),
  ('v3', '2026-08-22', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-08-23', 'long', 'Long run 15 km (cap 1:50)', 15, 110, null, null, true, null),
  ('v3', '2026-08-24', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-08-25', 'easy', 'Easy 6 km', 6, null, null, null, false, null),
  ('v3', '2026-08-25', 'strength', 'Strength A', null, null, '2–4 sets, 2–3 reps in reserve; no failure.', null, false, null),
  ('v3', '2026-08-26', 'rest', 'Rest or short easy 4–5 km', null, null, null, null, false, null),
  ('v3', '2026-08-27', 'easy', 'Easy 7 km + 4×15 s strides after easy run', 7, null, null, null, false, null),
  ('v3', '2026-08-28', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-08-28', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through.', null, false, null),
  ('v3', '2026-08-29', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-08-30', 'long', 'Long run 16 km (cap 2:00)', 16, 120, null, 35, true, null),
  ('v3', '2026-08-31', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-09-01', 'easy', 'Easy 6 km', 6, null, null, null, false, null),
  ('v3', '2026-09-01', 'strength', 'Strength A', null, null, '2–4 sets, 2–3 reps in reserve; no failure.', null, false, null),
  ('v3', '2026-09-02', 'rest', 'Rest or short easy 4–5 km', null, null, null, null, false, null),
  ('v3', '2026-09-03', 'easy', 'Easy 7 km + 6×15 s strides after easy run', 7, null, null, null, false, null),
  ('v3', '2026-09-04', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-09-04', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through.', null, false, null),
  ('v3', '2026-09-05', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-09-06', 'long', 'Long run 18 km (cap 2:10)', 18, 130, null, 35, true, 'Farthest-ever long run'),
  ('v3', '2026-09-07', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-09-08', 'easy', 'Easy 6 km', 6, null, null, null, false, null),
  ('v3', '2026-09-08', 'strength', 'Strength A', null, null, '2–4 sets, 2–3 reps in reserve; no failure.', null, false, null),
  ('v3', '2026-09-09', 'rest', 'Rest or short easy 4–5 km', null, null, null, null, false, null),
  ('v3', '2026-09-10', 'easy', 'Easy 7 km + 4×15 s strides after easy run', 7, null, null, null, false, null),
  ('v3', '2026-09-11', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-09-11', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through.', null, false, null),
  ('v3', '2026-09-12', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-09-13', 'long', 'Long run 14 km (cap 1:40)', 14, 100, null, 35, true, null),
  ('v3', '2026-09-14', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-09-15', 'easy', 'Easy 6 km', 6, null, null, null, false, null),
  ('v3', '2026-09-15', 'strength', 'Strength A', null, null, '2–4 sets, 2–3 reps in reserve; no failure.', null, false, null),
  ('v3', '2026-09-16', 'rest', 'Rest or short easy 4–5 km', null, null, null, null, false, null),
  ('v3', '2026-09-17', 'quality', '10 min steady finish on midweek run', 7, null, 'Default when green; first thing removed when amber. Skipping on a green day is a recorded deviation.', null, false, null),
  ('v3', '2026-09-18', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-09-18', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through.', null, false, null),
  ('v3', '2026-09-19', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-09-20', 'long', 'Long run 19 km (cap 2:20)', 19, 140, 'Fuel/fluid/equipment rehearsal; sweat-rate test.', 35, true, 'Farthest-ever long run'),
  ('v3', '2026-09-21', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-09-22', 'easy', 'Easy 7 km', 7, null, null, null, false, null),
  ('v3', '2026-09-22', 'strength', 'Strength A', null, null, '2–4 sets, 2–3 reps in reserve; no failure.', null, false, null),
  ('v3', '2026-09-23', 'mlr', 'Medium-long run 10 km', 10, null, 'Includes 2×8 min controlled steady (default when green). Load-spreading, not load-adding; first run shortened when reducing.', null, false, null),
  ('v3', '2026-09-24', 'easy', 'Easy 7 km + 2×8 min steady inside the medium-long run', 7, null, null, null, false, null),
  ('v3', '2026-09-25', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-09-25', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through.', null, false, null),
  ('v3', '2026-09-26', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-09-27', 'long', 'Long run 20 km (cap 2:25)', 20, 145, null, 45, true, 'Farthest-ever long run'),
  ('v3', '2026-09-28', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-09-29', 'easy', 'Easy 7 km', 7, null, null, null, false, null),
  ('v3', '2026-09-29', 'strength', 'Strength A', null, null, '2–4 sets, 2–3 reps in reserve; no failure.', null, false, null),
  ('v3', '2026-09-30', 'mlr', 'Medium-long run 11 km', 11, null, 'Load-spreading, not load-adding; first run shortened when reducing.', null, false, null),
  ('v3', '2026-10-01', 'easy', 'Easy 7 km + 6×15 s strides after easy run', 7, null, null, null, false, null),
  ('v3', '2026-10-02', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-10-02', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through.', null, false, null),
  ('v3', '2026-10-03', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-10-04', 'long', 'Long run 22 km (cap 2:40)', 22, 160, 'Log GI, skin, foot, late mechanics. Fuel ≥40 g/h on long run.', 45, true, 'Farthest-ever long run'),
  ('v3', '2026-10-05', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-10-06', 'easy', 'Easy 7 km', 7, null, null, null, false, null),
  ('v3', '2026-10-06', 'strength', 'Strength A', null, null, '2–4 sets, 2–3 reps in reserve; no failure.', null, false, null),
  ('v3', '2026-10-07', 'mlr', 'Medium-long run 10 km', 10, null, 'Load-spreading, not load-adding; first run shortened when reducing.', null, false, null),
  ('v3', '2026-10-08', 'easy', 'Easy 7 km + 4×15 s strides after easy run', 7, null, null, null, false, null),
  ('v3', '2026-10-09', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-10-09', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through.', null, false, null),
  ('v3', '2026-10-10', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-10-11', 'long', 'Long run 16 km (cap 2:00)', 16, 120, null, 45, true, null),
  ('v3', '2026-10-12', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-10-13', 'easy', 'Easy 7 km', 7, null, null, null, false, null),
  ('v3', '2026-10-13', 'strength', 'Strength A', null, null, '2–4 sets, 2–3 reps in reserve; no failure.', null, false, null),
  ('v3', '2026-10-14', 'mlr', 'Medium-long run 12 km', 12, null, 'Load-spreading, not load-adding; first run shortened when reducing.', null, true, null),
  ('v3', '2026-10-15', 'quality', '3×10 min steady with 3 min float', 8, null, 'Default when green; first thing removed when amber. Skipping on a green day is a recorded deviation.', null, false, null),
  ('v3', '2026-10-16', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-10-16', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through.', null, false, null),
  ('v3', '2026-10-17', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-10-18', 'long', 'Long run 24 km (cap 2:50)', 24, 170, 'Fuel every long run ≥50 g/h; settle race gear.', 55, true, 'Farthest-ever long run'),
  ('v3', '2026-10-19', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-10-20', 'easy', 'Easy 7 km', 7, null, null, null, false, null),
  ('v3', '2026-10-20', 'strength', 'Strength A', null, null, '2–4 sets, 2–3 reps in reserve; no failure.', null, false, null),
  ('v3', '2026-10-21', 'mlr', 'Medium-long run 12 km', 12, null, 'Load-spreading, not load-adding; first run shortened when reducing.', null, true, null),
  ('v3', '2026-10-22', 'easy', 'Rest or 20 min easy jog (pre-race)', null, null, 'Freshness for the Sunday half; no quality this week.', null, false, null),
  ('v3', '2026-10-23', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-10-23', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through.', null, false, null),
  ('v3', '2026-10-24', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-10-25', 'race', 'Half-marathon tune-up — controlled effort', 21.1, null, 'Not all-out. Race-morning rehearsal: breakfast, kit, fuel under race stress. If amber: run as a controlled long run instead.', 50, true, 'Half-marathon tune-up race'),
  ('v3', '2026-10-26', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-10-27', 'easy', 'Easy 7 km', 7, null, null, null, false, null),
  ('v3', '2026-10-27', 'strength', 'Strength A', null, null, 'Maintain intensity; reduced sets/accessories.', null, false, null),
  ('v3', '2026-10-28', 'mlr', 'Medium-long run 13 km', 13, null, 'Load-spreading, not load-adding; first run shortened when reducing.', null, true, null),
  ('v3', '2026-10-29', 'easy', 'Easy 8 km + 6×15 s strides after easy run', 8, null, null, null, false, null),
  ('v3', '2026-10-30', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-10-30', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through. Reduced lower-body volume from Week 11.', null, false, null),
  ('v3', '2026-10-31', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-11-01', 'long', 'Long run 26 km (cap 3:05)', 26, 185, '2×3 km at marathon effort inside the long run; fuel ≥60 g/h. Includes 2×3 km at marathon effort.', 60, true, 'Farthest-ever long run'),
  ('v3', '2026-11-02', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-11-03', 'easy', 'Easy 7 km', 7, null, null, null, false, null),
  ('v3', '2026-11-03', 'strength', 'Strength A', null, null, 'Maintain intensity; reduced sets/accessories.', null, false, null),
  ('v3', '2026-11-04', 'mlr', 'Medium-long run 10 km', 10, null, 'Load-spreading, not load-adding; first run shortened when reducing.', null, true, null),
  ('v3', '2026-11-05', 'quality', '3×6 min threshold with 2 min jog', 8, null, 'Default when green; first thing removed when amber. Skipping on a green day is a recorded deviation.', null, false, null),
  ('v3', '2026-11-06', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-11-06', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through. Reduced lower-body volume from Week 11.', null, false, null),
  ('v3', '2026-11-07', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-11-08', 'long', 'Long run 19 km (cap 2:25)', 19, 145, null, 60, true, null),
  ('v3', '2026-11-08', 'review', 'Go/no-go review', null, null, 'Formal decision from evidence: time goal / completion / run-walk / defer. Recorded in the weekly decision log.', null, true, 'Week 12 go/no-go decision'),
  ('v3', '2026-11-09', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-11-10', 'easy', 'Easy 7 km', 7, null, null, null, false, null),
  ('v3', '2026-11-10', 'strength', 'Strength A', null, null, 'Maintain intensity; reduced sets/accessories.', null, false, null),
  ('v3', '2026-11-11', 'mlr', 'Medium-long run 14 km', 14, null, 'Load-spreading, not load-adding; first run shortened when reducing.', null, true, null),
  ('v3', '2026-11-12', 'easy', 'Easy 8 km + 4×15 s strides after easy run', 8, null, null, null, false, null),
  ('v3', '2026-11-13', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-11-13', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through. Reduced lower-body volume from Week 11.', null, false, null),
  ('v3', '2026-11-14', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-11-15', 'long', 'Long run 28 km (cap 3:25)', 28, 205, 'Dress rehearsal: race breakfast, kit, anti-chafe, fuel ≥60 g/h, race start time. 4–6 km continuous at marathon effort inside the long run. Finish with reserves. Includes 4–6 km continuous at marathon effort.', 60, true, 'Dress rehearsal — the confidence anchor'),
  ('v3', '2026-11-16', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-11-17', 'easy', 'Easy 7 km', 7, null, null, null, false, null),
  ('v3', '2026-11-17', 'strength', 'Strength A', null, null, 'Maintain intensity; reduced sets/accessories.', null, false, null),
  ('v3', '2026-11-18', 'mlr', 'Medium-long run 12 km', 12, null, 'Load-spreading, not load-adding; first run shortened when reducing.', null, true, null),
  ('v3', '2026-11-19', 'quality', '2×2 km at marathon effort', 8, null, 'Default when green; first thing removed when amber. Skipping on a green day is a recorded deviation.', null, false, null),
  ('v3', '2026-11-20', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-11-20', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through. Reduced lower-body volume from Week 11.', null, false, null),
  ('v3', '2026-11-21', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-11-22', 'long', 'Long run 23 km (cap 2:50)', 23, 170, 'Includes 2×2 km at marathon effort.', 60, true, null),
  ('v3', '2026-11-23', 'rest', 'Rest / mobility', null, null, 'Post-long-run assessment day.', null, false, null),
  ('v3', '2026-11-24', 'easy', 'Easy 7 km', 7, null, null, null, false, null),
  ('v3', '2026-11-24', 'strength', 'Strength A', null, null, 'Maintain intensity; reduced sets/accessories.', null, false, null),
  ('v3', '2026-11-25', 'mlr', 'Medium-long run 9 km', 9, null, 'Load-spreading, not load-adding; first run shortened when reducing.', null, true, null),
  ('v3', '2026-11-26', 'quality', '3×2 km at marathon effort', 8, null, 'Default when green; first thing removed when amber. Skipping on a green day is a recorded deviation.', null, false, null),
  ('v3', '2026-11-27', 'rest', 'Rest', null, null, null, null, false, null),
  ('v3', '2026-11-27', 'strength', 'Strength B', null, null, 'Load-bearing for this plan — absence is recorded, not waved through. Reduced lower-body volume from Week 11.', null, false, null),
  ('v3', '2026-11-28', 'shakeout', 'Short easy 4–5 km + strides', 4.5, null, 'No fatigue accumulation before the long run.', null, false, null),
  ('v3', '2026-11-29', 'long', 'Long run 16 km (cap 2:00)', 16, 120, 'Includes 3×2 km at marathon effort.', 60, true, null),
  ('v3', '2026-11-30', 'rest', 'Rest / mobility', null, null, null, null, false, null),
  ('v3', '2026-12-01', 'easy', 'Easy 20–25 min + 4 strides', 4, null, null, null, false, null),
  ('v3', '2026-12-02', 'quality', '2×1.5 km at marathon effort', 6, 40, 'Carb load begins today: 10–12 g/kg/day Wed–Thu.', null, false, null),
  ('v3', '2026-12-03', 'rest', 'Rest (carb load continues)', null, null, 'Race kit laid out; early night.', null, false, null),
  ('v3', '2026-12-04', 'race', 'BYD Singapore Marathon', 42.2, null, 'Segments: 0–10 settle · 10–25 rhythm · 25–35 work · 35–42 execute. Fuel ≥60 g/h from 20–30 min. Red flag overrides participation.', 60, true, 'Race day'),
  ('v3', '2026-12-05', 'rest', 'Recovery walk only', null, null, null, null, false, null),
  ('v3', '2026-12-06', 'rest', 'Recovery walk only', null, null, null, null, false, null),
  ('v3', '2026-12-01', 'strength', 'Strength — light activation', null, null, 'Familiar light work only; last session before race.', null, false, null);

-- ---------------------------------------------------------------------------
-- RLS / auth: a single author user (Supabase Auth) may read and write the
-- capture tables from the private /log/ page. Visitors never authenticate;
-- public signups are disabled at the project level. is_author() is the only
-- door, keyed to the author's email claim.
-- ---------------------------------------------------------------------------
create or replace function is_author() returns boolean
language sql stable as $$
  select coalesce(auth.jwt() ->> 'email', '') = 'snishanths@gmail.com'
$$;

-- Views run with owner rights, so each private view gates internally. The
-- service role (site build, ingest) and direct SQL (migrations, Studio) pass;
-- an authenticated browser session passes only as the author.
create or replace function can_read_private() returns boolean
language sql stable as $$
  select is_author()
      or coalesce(auth.role(), '') = 'service_role'
      or current_setting('request.jwt.claims', true) is null
$$;

alter table plan_session   enable row level security;
alter table checkin        enable row level security;
alter table issue          enable row level security;
alter table weekly_decision enable row level security;
alter table gate_rule      enable row level security;

create policy author_all on checkin
  for all to authenticated using (is_author()) with check (is_author());
create policy author_all on issue
  for all to authenticated using (is_author()) with check (is_author());
create policy author_all on weekly_decision
  for all to authenticated using (is_author()) with check (is_author());
create policy author_read on plan_week
  for select to authenticated using (is_author());
create policy author_read on plan_session
  for select to authenticated using (is_author());
create policy author_read on gate_rule
  for select to authenticated using (is_author());
create policy author_read on garmin_daily
  for select to authenticated using (is_author());
create policy author_read on garmin_activity
  for select to authenticated using (is_author());

grant select, insert, update on checkin, issue, weekly_decision to authenticated;
grant select on plan_week, plan_session, gate_rule, garmin_daily, garmin_activity to authenticated;
grant usage on all sequences in schema public to authenticated;

-- ---------------------------------------------------------------------------
-- Gate engine. Views execute with owner rights, so each private view gates on
-- is_author() internally; the service role bypasses via a dedicated clause.
-- ---------------------------------------------------------------------------

-- Per-day joined signals (private).
create view v_daily_signals as
select
  d.day,
  d.resting_hr,
  d.sleep_seconds,
  d.sleep_score,
  d.hrv_last_night,
  d.hrv_baseline_low,
  d.hrv_baseline_high,
  avg(d.hrv_last_night) over w7  as hrv_7d,
  avg(d.resting_hr)     over w7  as rhr_7d,
  avg(d.resting_hr)     over w7p as rhr_prev7,
  (d.hrv_last_night is null)     as hrv_missing,
  m.sleep_quality, m.energy, m.mood, m.soreness, m.illness,
  nm.issue_vs_baseline, nm.stiffness_min, nm.stairs_normal, nm.swelling, nm.ready_for_easy,
  pr.red_flag, pr.pain_severity, pr.gait_affected,
  po.rpe, po.pain_trend, po.completed_as_planned
from garmin_daily d
left join checkin m  on m.local_date  = d.day and m.moment  = 'morning'
left join checkin nm on nm.local_date = d.day and nm.moment = 'next_morning'
left join checkin pr on pr.local_date = d.day and pr.moment = 'pre_run'
left join checkin po on po.local_date = d.day and po.moment = 'post_run'
where can_read_private()
window
  w7  as (order by d.day rows between 6 preceding and current row),
  w7p as (order by d.day rows between 7 preceding and 1 preceding);

-- Daily status proposal (private). Red is only ever *reported*, never derived
-- from wearables; wearable-only deviations without symptoms resolve green_easy.
create view v_daily_status as
with s as (
  select *,
    -- symptom corroboration for wearable signals
    (coalesce(energy, 3) <= 2 or coalesce(sleep_quality, 3) <= 2
     or coalesce(soreness, 0) >= 4 or coalesce(illness, false)) as symptomatic,
    -- autonomic deviation: 7d HRV mean outside personal band, or RHR elevated
    ((hrv_7d is not null and hrv_baseline_low is not null
      and (hrv_7d < hrv_baseline_low or hrv_7d > hrv_baseline_high))
     or (rhr_prev7 is not null and resting_hr is not null
         and resting_hr - rhr_prev7 >= (select (params->>'delta_bpm')::int from gate_rule where key = 'rhr_amber')))
      as autonomic_off,
    (coalesce(sleep_seconds, 28800) < (select (params->>'min_seconds')::int from gate_rule where key = 'poor_sleep_amber')
     or coalesce(sleep_quality, 3) <= (select (params->>'quality_max')::int from gate_rule where key = 'poor_sleep_amber'))
      as poor_night
  from v_daily_signals
),
runs as (
  select s.*,
    (select count(*) from s s2
      where s2.day > s.day - (select (params->>'consecutive_days')::int from gate_rule where key = 'hrv_amber')
        and s2.day <= s.day and s2.autonomic_off) as autonomic_run,
    (select count(*) from s s3
      where s3.day > s.day - (select (params->>'nights')::int from gate_rule where key = 'poor_sleep_amber')
        and s3.day <= s.day and s3.poor_night) as poor_night_run
  from s
)
select
  day,
  case
    when coalesce(red_flag, false) then 'red_reported'
    when coalesce(issue_vs_baseline, 'baseline') = 'worse'
      or coalesce(stiffness_min, 0) > (select (params->>'minutes')::int from gate_rule where key = 'stiffness_green_max')
      or stairs_normal is false
      or coalesce(swelling, false)
      or coalesce(pain_severity, 0) > 2
      or pain_trend = 'worsening'
      or coalesce(gait_affected, false)
      then 'amber_tissue'
    when (autonomic_run >= (select (params->>'consecutive_days')::int from gate_rule where key = 'hrv_amber')
          and symptomatic)
      or poor_night_run >= (select (params->>'nights')::int from gate_rule where key = 'poor_sleep_amber')
      or coalesce(illness, false)
      then 'amber_life'
    when autonomic_run >= (select (params->>'consecutive_days')::int from gate_rule where key = 'hrv_amber')
      then 'green_easy'
    else 'green'
  end as status,
  autonomic_run, poor_night_run, symptomatic,
  hrv_7d, rhr_7d, hrv_missing,
  rpe, issue_vs_baseline, stiffness_min, pain_severity
from runs;

-- Today card + circuit breaker (private).
create view v_today_status as
select
  ds.*,
  (select count(*) from v_daily_status d2
    where d2.day > ds.day - (select (params->>'window_days')::int from gate_rule where key = 'circuit_breaker')
      and d2.day <= ds.day and d2.status like 'amber%') as amber_days_7d,
  (select count(*) >= (select (params->>'ambers')::int from gate_rule where key = 'circuit_breaker')
     from v_daily_status d3
    where d3.day > ds.day - (select (params->>'window_days')::int from gate_rule where key = 'circuit_breaker')
      and d3.day <= ds.day and d3.status like 'amber%') as circuit_breaker
from v_daily_status ds
order by ds.day desc
limit 1;

-- Session internal load: post-run RPE × run minutes, by day (private).
create view v_session_load as
select
  (a.started_at at time zone coalesce(a.local_tz, 'Asia/Singapore'))::date as day,
  round(sum(a.duration_s) / 60.0)                      as run_minutes,
  round(sum(a.distance_m) / 1000.0, 2)                 as run_km,
  max(c.rpe)                                           as rpe,
  round(max(c.rpe) * sum(a.duration_s) / 60.0)         as session_load
from garmin_activity a
left join checkin c
  on c.local_date = (a.started_at at time zone coalesce(a.local_tz, 'Asia/Singapore'))::date
 and c.moment = 'post_run'
where a.activity_type ilike '%running%'
  and can_read_private()
group by 1;

-- Capture completeness, last 7 days (private): feeds data confidence.
create view v_capture_stats as
select
  count(*) filter (where moment = 'post_run')     as post_run_7d,
  count(*) filter (where moment = 'morning')      as morning_7d,
  count(*) filter (where moment = 'next_morning') as next_morning_7d
from checkin
where local_date > current_date - 7
  and can_read_private();

grant select on v_daily_signals, v_daily_status, v_today_status, v_session_load,
               v_capture_stats to authenticated;

-- ---------------------------------------------------------------------------
-- Export views for the public site build (service role only, like the rest).
-- ---------------------------------------------------------------------------
drop view export_weekly_progress;
create view export_weekly_progress as
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
where p.plan_version = 'v3'
group by p.week_no, p.phase, p.week_start, p.target_km, p.long_run_km,
         p.sessions_planned, p.is_cutback
order by p.week_no;

create view export_plan_sessions as
select session_date, session_type, title, target_km, time_cap_min, detail,
       fuel_target_g_h, is_key, milestone
from plan_session
where plan_version = 'v3';

create view export_weekly_decisions as
select week_no, decided_on, decision, lever, rationale, what_went_right,
       data_confidence
from weekly_decision
where plan_version = 'v3' and is_public;

-- Daily gate status history for the public dashboard: status only, no
-- symptom detail (wellness-aggregate class, auto-published like RHR/sleep).
create view export_daily_status as
select day, status from v_daily_status;

-- HRV joins the auto-published wellness aggregates.
drop view export_daily;
create view export_daily as
select day, resting_hr, sleep_seconds, sleep_score, vo2max_run,
       hrv_last_night, hrv_weekly_avg, hrv_status
from garmin_daily
where review_state = 'approved';

revoke all on export_weekly_progress, export_plan_sessions,
           export_weekly_decisions, export_daily_status, export_daily
  from anon, authenticated;
