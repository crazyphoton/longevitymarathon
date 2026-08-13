#!/usr/bin/env python3
"""Interactive one-time Garmin Connect login.

Run this yourself (it prompts for your Garmin email, password, and MFA code):

    python3 scripts/garmin_login.py

It mints Garmin OAuth tokens, keeps a local copy in the gitignored
data/garmin_tokens/ folder, and uploads the bundle to the private garmin_token
table in Supabase, where the daily ingest job keeps it fresh as the refresh
token rotates. Your password is used only for this login and is never stored.

Requires: pip install garminconnect requests
Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
"""

import getpass
import json
import os
import sys
from pathlib import Path

import requests
from garminconnect import Garmin

TOKEN_DIR = Path(__file__).resolve().parent.parent / "data" / "garmin_tokens"


def main() -> None:
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_key:
        sys.exit("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set.")

    email = input("Garmin email: ").strip()
    password = getpass.getpass("Garmin password: ")

    client = Garmin(email, password, prompt_mfa=lambda: input("MFA code: ").strip())
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    client.login(str(TOKEN_DIR))

    tokens_json = client.client.dumps()

    resp = requests.post(
        f"{supabase_url}/rest/v1/garmin_token?on_conflict=id",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        },
        json=[{"id": True, "tokens": json.loads(tokens_json), "updated_at": "now()"}],
        timeout=30,
    )
    resp.raise_for_status()
    name = client.get_full_name() if hasattr(client, "get_full_name") else email
    print(f"Logged in ({name}). Tokens saved to {TOKEN_DIR} and uploaded to Supabase.")


if __name__ == "__main__":
    main()
