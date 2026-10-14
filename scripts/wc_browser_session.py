#!/usr/bin/env python3
"""WhatConverts controlled-browser session helper.

The public API (v1/v2) has no endpoint for form tracking, tracking numbers or the Google
Ads integration, so those settings are UI-only. This opens a REAL browser window against a
persistent profile directory so a human can sign in ONCE. The session is then reused by
automation and no password ever passes through the chat or the repo.

    # one-time, run by a human, a window opens:
    .\\.venv\\Scripts\\python.exe scripts\\wc_browser_session.py --login

    # afterwards, anything can reuse it headlessly:
    .\\.venv\\Scripts\\python.exe scripts\\wc_browser_session.py --check

The profile directory holds the session cookie. It lives outside the repo, is listed in
.gitignore terms below, and is never committed or printed.
"""
from __future__ import annotations
import sys, json, argparse, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

# Deliberately OUTSIDE the repository so a browser session can never be committed.
PROFILE_DIR = Path.home() / ".gm-browser-profiles" / "whatconverts"
START = "https://app.whatconverts.com/"
PROFILE_ID = "105803"
ACCOUNT_ID = "115814"


def launch(pw, headless):
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    return pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=headless,
        viewport={"width": 1500, "height": 950},
        locale="en-US",
        timezone_id="America/New_York",
        args=["--disable-dev-shm-usage"])


def signed_in(pg):
    """Signed in when the app does NOT bounce us to a login screen."""
    u = pg.url.lower()
    if "login" in u or "signin" in u or "sign-in" in u:
        return False
    body = (pg.inner_text("body") or "").lower()
    if "sign in" in body[:1500] and "password" in body[:2500]:
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", action="store_true",
                    help="open a visible window so a human can sign in once")
    ap.add_argument("--check", action="store_true",
                    help="headlessly report whether the saved session still works")
    args = ap.parse_args()

    if not (args.login or args.check):
        ap.error("pass --login or --check")

    with sync_playwright() as pw:
        ctx = launch(pw, headless=bool(args.check))
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            pg.goto(START, wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(4000)
            ok = signed_in(pg)
            print(f"profile dir : {PROFILE_DIR}")
            print(f"landed on   : {pg.url}")
            print(f"signed in   : {ok}")

            if args.login:
                if ok:
                    print("\nAlready signed in. Nothing to do.")
                else:
                    print("\n" + "=" * 72)
                    print("A browser window is open. Sign in to WhatConverts there.")
                    print("Use SSO or the password manager - do NOT type anything into")
                    print("the chat. This script never reads or stores what you type;")
                    print("only the resulting session cookie is kept, in the profile")
                    print("directory above.")
                    print("This window waits up to 10 minutes, then closes itself.")
                    print("=" * 72 + "\n")
                    for i in range(120):
                        pg.wait_for_timeout(5000)
                        if signed_in(pg):
                            print(f"signed in after ~{(i + 1) * 5}s - session saved")
                            break
                    else:
                        print("timed out; session NOT saved")

            if signed_in(pg):
                # Prove the session actually reaches Ambient's settings, not just a
                # generic logged-in page.
                for path in (f"/{ACCOUNT_ID}/{PROFILE_ID}/tracking/forms",
                             f"/{ACCOUNT_ID}/{PROFILE_ID}/tracking",
                             f"/{ACCOUNT_ID}/{PROFILE_ID}/integrations"):
                    try:
                        pg.goto(START.rstrip("/") + path,
                                wait_until="domcontentloaded", timeout=40000)
                        pg.wait_for_timeout(2500)
                        print(f"  {path:46s} -> {pg.url[:70]}")
                    except Exception as ex:
                        print(f"  {path:46s} -> {type(ex).__name__}")
        finally:
            state = {"checked": datetime.datetime.now(TZ).isoformat(),
                     "profile_dir": str(PROFILE_DIR),
                     "signed_in": signed_in(pg) if not pg.is_closed() else None}
            SNAP.mkdir(parents=True, exist_ok=True)
            (SNAP / "wc-session-state.json").write_text(
                json.dumps(state, indent=1), encoding="utf-8")
            ctx.close()
    print("\nNo credential was read, stored or printed by this script.")


if __name__ == "__main__":
    main()
