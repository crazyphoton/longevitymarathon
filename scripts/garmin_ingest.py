#!/usr/bin/env python3
"""Pull recent Garmin Connect data into private Supabase staging tables.

Runs daily in GitHub Actions (and on demand). Loads the rotating Garmin token
bundle from the garmin_token table, fetches the last LOOKBACK_DAYS of
activities and daily wellness, upserts them (never touching review_state, so
curation decisions survive re-ingestion), and writes the refreshed token
bundle back.

Nothing here publishes anything: rows land as review_state='private' and only
become visible to the site build after manual approval (spec §13.2).

Requires: pip install garminconnect requests
Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, optional LOOKBACK_DAYS (default 7)
"""

import datetime as dt
import json
import os
import sys

import requests
from garminconnect import Garmin

SUPABASE_URL = os.environ["SUPABASE_URL"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "7"))

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
}


def rest(method: str, path: str, extra_headers: dict | None = None, **kwargs) -> requests.Response:
    headers = {**HEADERS, **(extra_headers or {})}
    resp = requests.request(method, f"{SUPABASE_URL}/rest/v1/{path}", headers=headers, timeout=60, **kwargs)
    if not resp.ok:
        sys.exit(f"Supabase {method} {path} failed: {resp.status_code} {resp.text[:300]}")
    return resp


def upsert(table: str, conflict: str, rows: list[dict]) -> None:
    if rows:
        rest(
            "POST",
            f"{table}?on_conflict={conflict}",
            extra_headers={"Prefer": "resolution=merge-duplicates"},
            json=rows,
        )


def load_client() -> Garmin:
    rows = rest("GET", "garmin_token?select=tokens").json()
    if not rows:
        sys.exit("No Garmin token in Supabase. Run scripts/garmin_login.py first.")
    client = Garmin()
    client.login(json.dumps(rows[0]["tokens"]))
    return client


def save_tokens(client: Garmin) -> None:
    upsert(
        "garmin_token",
        "id",
        [{"id": True, "tokens": json.loads(client.client.dumps()), "updated_at": "now()"}],
    )


def activity_rows(client: Garmin, start: dt.date, end: dt.date) -> list[dict]:
    activities = client.get_activities_by_date(start.isoformat(), end.isoformat())
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    rows = []
    for a in activities:
        avg_speed = a.get("averageSpeed") or 0  # m/s
        rows.append(
            {
                "garmin_activity_id": a["activityId"],
                "started_at": a.get("startTimeGMT", "").replace(" ", "T") + "+00:00",
                "local_tz": (a.get("timeZoneUnitDTO") or {}).get("timeZone"),
                "activity_type": (a.get("activityType") or {}).get("typeKey", "unknown"),
                "name": a.get("activityName"),
                "distance_m": a.get("distance"),
                "duration_s": a.get("duration"),
                "avg_hr": a.get("averageHR"),
                "max_hr": a.get("maxHR"),
                "avg_pace_s_per_km": round(1000 / avg_speed, 1) if avg_speed else None,
                "elevation_gain_m": a.get("elevationGain"),
                "calories": a.get("calories"),
                "vo2max_estimate": a.get("vO2MaxValue"),
                "raw": a,
                "updated_at": now,
            }
        )
    return rows


def daily_rows(client: Garmin, days: list[dt.date]) -> list[dict]:
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    rows = []
    for day in days:
        iso = day.isoformat()
        raw: dict = {}
        stats = sleep = maxmet = None
        try:
            stats = client.get_stats(iso)
            raw["stats"] = stats
        except Exception as e:
            print(f"  {iso}: stats failed: {e}")
        try:
            sleep = (client.get_sleep_data(iso) or {})
            raw["sleep"] = sleep
        except Exception as e:
            print(f"  {iso}: sleep failed: {e}")
        try:
            maxmet = client.get_max_metrics(iso)
            raw["max_metrics"] = maxmet
        except Exception as e:
            print(f"  {iso}: max metrics failed: {e}")
        if not raw:
            continue

        sleep_dto = (sleep or {}).get("dailySleepDTO") or {}
        sleep_scores = sleep_dto.get("sleepScores") or {}
        vo2 = None
        if isinstance(maxmet, list) and maxmet:
            vo2 = ((maxmet[0] or {}).get("generic") or {}).get("vo2MaxPreciseValue")
        elif isinstance(maxmet, dict):
            vo2 = (maxmet.get("generic") or {}).get("vo2MaxPreciseValue")

        rows.append(
            {
                "day": iso,
                "resting_hr": (stats or {}).get("restingHeartRate"),
                "sleep_seconds": sleep_dto.get("sleepTimeSeconds"),
                "sleep_score": (sleep_scores.get("overall") or {}).get("value"),
                "steps": (stats or {}).get("totalSteps"),
                "body_battery_high": (stats or {}).get("bodyBatteryHighestValue"),
                "body_battery_low": (stats or {}).get("bodyBatteryLowestValue"),
                "vo2max_run": vo2,
                "raw": raw,
                "updated_at": now,
            }
        )
    return rows


def main() -> None:
    today = dt.date.today()
    start = today - dt.timedelta(days=LOOKBACK_DAYS)
    days = [start + dt.timedelta(days=i) for i in range((today - start).days + 1)]

    client = load_client()
    try:
        acts = activity_rows(client, start, today)
        upsert("garmin_activity", "garmin_activity_id", acts)
        print(f"Upserted {len(acts)} activities ({start} → {today}).")

        daily = daily_rows(client, days)
        upsert("garmin_daily", "day", daily)
        print(f"Upserted {len(daily)} daily wellness rows.")
    finally:
        # Always persist the rotated refresh token, even on partial failure.
        save_tokens(client)
        print("Token bundle written back to Supabase.")


if __name__ == "__main__":
    main()
