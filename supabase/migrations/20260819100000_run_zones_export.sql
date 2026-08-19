-- Time-in-HR-zone per approved run, for the dashboard's intensity-distribution
-- chart. Zone seconds come from Garmin's activity summary (raw jsonb,
-- hrTimeInZone_1..5); they are aggregates with no route or location data, so
-- they fall under the activity publish class already recorded in spec §13.8.
create view export_run_zones as
select
  garmin_activity_id,
  (started_at at time zone coalesce(local_tz, 'Asia/Singapore'))::date as run_date,
  round(distance_m / 1000.0, 2)                  as distance_km,
  round(duration_s)                              as duration_s,
  avg_hr,
  round((raw->>'hrTimeInZone_1')::numeric)       as z1_s,
  round((raw->>'hrTimeInZone_2')::numeric)       as z2_s,
  round((raw->>'hrTimeInZone_3')::numeric)       as z3_s,
  round((raw->>'hrTimeInZone_4')::numeric)       as z4_s,
  round((raw->>'hrTimeInZone_5')::numeric)       as z5_s
from garmin_activity
where review_state = 'approved'
  and activity_type ilike '%running%'
  and raw ? 'hrTimeInZone_1';

revoke all on export_run_zones from anon, authenticated;
