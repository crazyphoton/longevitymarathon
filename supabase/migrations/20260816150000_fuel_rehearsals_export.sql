-- Fuel-rehearsal aggregates for the public race-systems/readiness display:
-- g carbohydrate/hour on run days, with GI outcome reduced to a boolean
-- ("tolerated"), per the §13 aggregates-only rule. No symptom detail.
create view export_fuel_rehearsals as
select
  c.local_date as day,
  c.fuel_g_per_h,
  (coalesce(c.gi_score, 0) <= 1) as gi_ok,
  r.km,
  r.minutes
from checkin c
join (
  select run_date, sum(distance_km) as km, round(sum(duration_s) / 60.0) as minutes
  from export_runs
  group by run_date
) r on r.run_date = c.local_date
where c.moment = 'post_run' and c.fuel_g_per_h is not null;

revoke all on export_fuel_rehearsals from anon, authenticated;
