-- Phase 2 data platform (spec §13.8): private staging + curated export views.
-- All tables are default-deny (RLS enabled, no policies). Only the service role
-- (GitHub Actions, author tooling) reads or writes; site visitors never touch Supabase.

create extension if not exists citext;

create type review_state as enum ('private', 'approved');

-- Source taxonomy from spec §9: estimates vs measurements are never mixed.
create type source_type as enum (
  'garmin_estimate',
  'device_measurement',
  'home_reading',
  'laboratory',
  'clinical_test',
  'manual'
);

-- Raw Garmin activities. garmin_activity_id is the stable private source
-- identifier (§13.2) so content never has to be rebuilt when automation changes.
-- Route/location data stays in `raw` and is never exposed by an export view.
create table garmin_activity (
  id            bigint generated always as identity primary key,
  garmin_activity_id bigint not null unique,
  started_at    timestamptz not null,
  local_tz      text,
  activity_type text not null,
  name          text,
  distance_m    numeric,
  duration_s    numeric,
  avg_hr        integer,
  max_hr        integer,
  avg_pace_s_per_km numeric,
  elevation_gain_m  numeric,
  calories      integer,
  vo2max_estimate   numeric,
  raw           jsonb not null,
  ingested_at   timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  review_state  review_state not null default 'private',
  public_note   text
);

-- Daily wellness rollup from Garmin (RHR, sleep, steps, VO2max estimate).
create table garmin_daily (
  day           date primary key,
  resting_hr    integer,
  sleep_seconds integer,
  sleep_score   integer,
  steps         integer,
  body_battery_high integer,
  body_battery_low  integer,
  vo2max_run    numeric,
  raw           jsonb not null,
  ingested_at   timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  review_state  review_state not null default 'private'
);

-- Manual readings: weight, BP, bloodwork markers, strength benchmarks.
create table metric_reading (
  id          bigint generated always as identity primary key,
  metric      text not null,
  value       numeric not null,
  unit        text not null,
  measured_at timestamptz not null,
  source_type source_type not null,
  method      text,
  note        text,
  is_public   boolean not null default false,
  created_at  timestamptz not null default now()
);

-- Plan targets per week per plan version, so planned-vs-actual is computed
-- here instead of hand-edited into HTML.
create table plan_week (
  plan_version     text not null,
  week_no          integer not null,
  phase            text not null,
  week_start       date not null,
  target_km        numeric not null,
  long_run_km      numeric,
  sessions_planned integer not null default 5,
  is_cutback       boolean not null default false,
  note             text,
  primary key (plan_version, week_no)
);

-- Newsletter subscribers (double opt-in; suppression = unsubscribed_at set).
create table subscriber (
  id                uuid primary key default gen_random_uuid(),
  email             citext not null unique,
  first_name        text,
  source            text,
  consent_at        timestamptz not null default now(),
  confirm_token     uuid not null default gen_random_uuid(),
  confirmed_at      timestamptz,
  unsubscribe_token uuid not null default gen_random_uuid(),
  unsubscribed_at   timestamptz
);

alter table garmin_activity enable row level security;
alter table garmin_daily    enable row level security;
alter table metric_reading  enable row level security;
alter table plan_week       enable row level security;
alter table subscriber      enable row level security;

-- Belt and braces: Supabase grants anon/authenticated table privileges by
-- default; revoke them so even a misconfigured policy exposes nothing.
revoke all on all tables in schema public from anon, authenticated;
alter default privileges in schema public revoke all on tables from anon, authenticated;

-- ---------------------------------------------------------------------------
-- Export views: the only surface the site build reads. Approved/public rows
-- only; no coordinates, no raw JSON, no exact start times (date + duration only).
-- ---------------------------------------------------------------------------

create view export_runs as
select
  garmin_activity_id,
  (started_at at time zone coalesce(local_tz, 'Asia/Singapore'))::date as run_date,
  round(distance_m / 1000.0, 2) as distance_km,
  round(duration_s)             as duration_s,
  avg_hr,
  round(avg_pace_s_per_km)      as avg_pace_s_per_km,
  round(elevation_gain_m)       as elevation_gain_m,
  public_note
from garmin_activity
where review_state = 'approved'
  and activity_type ilike '%running%';

create view export_daily as
select day, resting_hr, sleep_seconds, sleep_score, vo2max_run
from garmin_daily
where review_state = 'approved';

create view export_metrics as
select metric, value, unit, measured_at, source_type, method, note
from metric_reading
where is_public;

create view export_plan_weeks as
select plan_version, week_no, phase, week_start, target_km, long_run_km,
       sessions_planned, is_cutback, note
from plan_week;

-- Planned vs actual per week for the current plan (approved runs only).
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
where p.plan_version = 'v2'
group by p.week_no, p.phase, p.week_start, p.target_km, p.long_run_km,
         p.sessions_planned, p.is_cutback
order by p.week_no;

revoke all on export_runs, export_daily, export_metrics, export_plan_weeks,
             export_weekly_progress from anon, authenticated;

-- ---------------------------------------------------------------------------
-- Seed: plan v2 (site/plan/versions/v2-current). Week 1 starts Mon 2026-08-10;
-- race day 2026-12-04 falls in Week 17.
-- ---------------------------------------------------------------------------

insert into plan_week (plan_version, week_no, phase, week_start, target_km, long_run_km, sessions_planned, is_cutback, note) values
  ('v2',  1, 'Foundation', '2026-08-10', 24,  8, 5, false, '3 easy runs + 2 strength sessions'),
  ('v2',  2, 'Foundation', '2026-08-17', 27, 10, 5, false, null),
  ('v2',  3, 'Foundation', '2026-08-24', 30, 11, 5, false, null),
  ('v2',  4, 'Foundation', '2026-08-31', 22,  8, 5, true,  'Cutback week + strength benchmark test'),
  ('v2',  5, 'Build',      '2026-09-07', 32, 14, 5, false, 'Tempo intervals begin'),
  ('v2',  6, 'Build',      '2026-09-14', 35, 16, 5, false, null),
  ('v2',  7, 'Build',      '2026-09-21', 38, 17, 5, false, null),
  ('v2',  8, 'Build',      '2026-09-28', 28, 13, 5, true,  'Cutback week'),
  ('v2',  9, 'Build',      '2026-10-05', 40, 18, 5, false, null),
  ('v2', 10, 'Peak',       '2026-10-12', 44, 20, 5, false, 'Goal-pace long-run segments introduced'),
  ('v2', 11, 'Peak',       '2026-10-19', 47, 22, 5, false, null),
  ('v2', 12, 'Peak',       '2026-10-26', 34, 15, 5, true,  'Cutback week'),
  ('v2', 13, 'Peak',       '2026-11-02', 42, 32, 5, false, 'Peak long run'),
  ('v2', 14, 'Taper',      '2026-11-09', 32, 16, 5, false, null),
  ('v2', 15, 'Taper',      '2026-11-16', 24, 12, 5, false, null),
  ('v2', 16, 'Taper',      '2026-11-23', 16,  8, 5, false, null),
  ('v2', 17, 'Race week',  '2026-11-30', 10, null, 3, false, 'BYD Singapore Marathon 2026 race day — 4 Dec 2026');
