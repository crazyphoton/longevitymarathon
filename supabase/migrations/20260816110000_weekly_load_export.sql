-- Weekly load aggregates for the public dashboard. Plan v3 is duration-led
-- (§3.1): time on feet and long-run share are the primary exposure readouts,
-- distance is context. Everything here is an aggregate — session-RPE load is
-- a weekly sum (raw RPE stays private), amber days are a count (symptom
-- detail stays private) — consistent with the wellness-aggregate publish
-- class recorded in spec §13.8.
create view export_weekly_load as
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
where p.plan_version = 'v3'
group by p.week_no, p.week_start, p.target_km, p.long_run_km, p.is_cutback
order by p.week_no;

revoke all on export_weekly_load from anon, authenticated;
