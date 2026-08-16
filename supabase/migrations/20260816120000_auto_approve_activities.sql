-- Auto-approve activities on ingest (author's decision, 2026-08-16), extending
-- the 2026-08-14 wellness exception to runs. Rationale: export_runs exposes no
-- route, coordinates, or exact start times (date + duration only), so the
-- privacy case for manual gating never applied to the published fields; the
-- raw payload with route data stays private regardless. Manual curation still
-- works — flipping a row to 'private' in Studio sticks, because the ingest
-- payload omits review_state and merge-duplicates leaves absent columns alone.
alter table garmin_activity alter column review_state set default 'approved';

-- Backfill: publish existing ingested activities.
update garmin_activity set review_state = 'approved' where review_state = 'private';
