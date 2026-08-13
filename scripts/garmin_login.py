#!/usr/bin/env python3
"""One-time Garmin Connect login, driven by files instead of prompts (the
sandbox's `!` commands have no interactive stdin).

Flow:
1. This script runs in the background and waits (up to 30 min) for
   data/garmin_credentials.json to appear:  {"email": "...", "password": "..."}
2. It logs in. If Garmin asks for an MFA code, it waits (up to 10 min) for
   data/garmin_mfa_code.txt containing just the code.
3. On success it uploads the token bundle to the private garmin_token table in
   Supabase, keeps a local copy in gitignored data/garmin_tokens/, and deletes
   the credentials and MFA files. The password is never stored.

Requires: pip install garminconnect requests
Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from garminconnect import Garmin

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CREDS_FILE = DATA_DIR / "garmin_credentials.json"
MFA_FILE = DATA_DIR / "garmin_mfa_code.txt"
TOKEN_DIR = DATA_DIR / "garmin_tokens"

CREDS_TIMEOUT_S = int(os.environ.get("CREDS_TIMEOUT_S", 30 * 60))
MFA_TIMEOUT_S = int(os.environ.get("MFA_TIMEOUT_S", 10 * 60))
COOLDOWN_S = int(os.environ.get("COOLDOWN_S", 0))  # wait before first attempt (429 cool-off)
RETRIES = int(os.environ.get("RETRIES", 3))
RETRY_WAIT_S = int(os.environ.get("RETRY_WAIT_S", 60 * 60))
POLL_S = 5


def wait_for_file(path: Path, timeout_s: int, what: str) -> str:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if path.exists():
            content = path.read_text().strip()
            if content:
                return content
        time.sleep(POLL_S)
    sys.exit(f"Timed out after {timeout_s // 60} min waiting for {what} at {path}.")


def prompt_mfa() -> str:
    print(
        f"MFA required. Check your email/authenticator, then write the code to\n"
        f"  {MFA_FILE}\n"
        f"(e.g.  echo 123456 > data/garmin_mfa_code.txt )",
        flush=True,
    )
    return wait_for_file(MFA_FILE, MFA_TIMEOUT_S, "the MFA code")


def shred(path: Path) -> None:
    if path.exists():
        path.write_text("0" * 256)
        path.unlink()


def main() -> None:
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_key:
        sys.exit("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    shred(MFA_FILE)  # never reuse a stale code

    print(f"Waiting for credentials file {CREDS_FILE} ...", flush=True)
    creds = json.loads(wait_for_file(CREDS_FILE, CREDS_TIMEOUT_S, "credentials"))
    email, password = creds["email"].strip(), creds["password"]
    if "REAL-EMAIL" in email.upper() or email in ("your@email.com", ""):
        shred(CREDS_FILE)
        sys.exit(f"Credentials file still contains the placeholder email ({email!r}). "
                 "Edit it with your real Garmin email and re-run.")
    print(f"Credentials received for {email}.", flush=True)

    if COOLDOWN_S:
        print(f"Cooling down {COOLDOWN_S // 60} min before login (Garmin rate limit) ...", flush=True)
        time.sleep(COOLDOWN_S)

    try:
        tokens = None
        for attempt in range(1, RETRIES + 1):
            try:
                print(f"Login attempt {attempt}/{RETRIES} ...", flush=True)
                client = Garmin(email, password, prompt_mfa=prompt_mfa)
                TOKEN_DIR.mkdir(parents=True, exist_ok=True)
                client.login(str(TOKEN_DIR))
                tokens = json.loads(client.client.dumps())
                break
            except Exception as e:
                if attempt == RETRIES:
                    raise
                print(f"Attempt {attempt} failed ({e}). Retrying in {RETRY_WAIT_S // 60} min ...", flush=True)
                time.sleep(RETRY_WAIT_S)
    finally:
        shred(CREDS_FILE)
        shred(MFA_FILE)

    resp = requests.post(
        f"{supabase_url}/rest/v1/garmin_token?on_conflict=id",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        },
        json=[{"id": True, "tokens": tokens, "updated_at": "now()"}],
        timeout=30,
    )
    resp.raise_for_status()
    print(f"Success. Tokens saved to {TOKEN_DIR} and uploaded to Supabase.")


if __name__ == "__main__":
    main()
