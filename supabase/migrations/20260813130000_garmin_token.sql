-- Garmin OAuth token bundle. Garmin's refresh tokens rotate on every use, so a
-- static CI secret would go stale; instead the ingest job loads this row,
-- refreshes, and writes the rotated bundle back. Single row, service-role only.
create table garmin_token (
  id         boolean primary key default true check (id),
  tokens     jsonb not null,
  updated_at timestamptz not null default now()
);

alter table garmin_token enable row level security;
