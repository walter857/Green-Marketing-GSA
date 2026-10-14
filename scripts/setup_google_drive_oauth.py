#!/usr/bin/env python3
"""Run the installed-app OAuth flow for the separate Green Marketing Drive integration.

This never touches the Google Ads OAuth client, the Google Ads refresh token, or
Application Default Credentials. It reads the desktop client JSON only by handing its path
to google-auth-oauthlib, and it writes the resulting token outside the repository.

No secret is printed. The only credential-derived values shown are the authorized email
address and the list of granted scopes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.google_drive import (  # noqa: E402
    DriveAuthorizationError,
    authorized_identity,
    build_drive_service,
    granted_scopes,
    load_drive_settings,
    load_stored_credentials,
    redact_error_text,
    save_credentials,
)

EXPECTED_EMAIL = "access@greenmarketingfl.com"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Authorize the separate Green Marketing Drive/Docs integration."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Fixed local callback port for the OAuth redirect (default: 8080).",
    )
    parser.add_argument(
        "--expect-email",
        default=EXPECTED_EMAIL,
        help="Authorization fails if a different account completes consent.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reauthorize even if a valid token already exists.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the authorization URL instead of opening a browser.",
    )
    args = parser.parse_args()

    settings = load_drive_settings()

    if not settings.credentials_file.exists():
        print(f"FAIL: OAuth client file not found at {settings.credentials_file}")
        print("Create a Desktop app OAuth client and download it to that path.")
        return 1
    print(f"OAuth client file: present at {settings.credentials_file} (contents not read here)")
    print(f"Token destination: {settings.token_file}")
    print("Requested scopes:")
    for scope in settings.scopes:
        print(f"  - {scope}")

    if settings.token_file.exists() and not args.force:
        try:
            credentials = load_stored_credentials(settings)
            identity = authorized_identity(build_drive_service(credentials))
            print(
                f"\nAlready authorized as {identity.get('emailAddress')}. "
                "Pass --force to reauthorize."
            )
            return 0
        except DriveAuthorizationError:
            print("\nExisting token is unusable. Starting a fresh authorization.")
        except Exception as exc:  # noqa: BLE001
            print(f"\nExisting token check failed: {redact_error_text(exc)}")
            print("Starting a fresh authorization.")

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("FAIL: google-auth-oauthlib is not installed in this environment.")
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(
        str(settings.credentials_file), list(settings.scopes)
    )

    print("\n" + "=" * 78)
    print(f"ACTION REQUIRED: sign in as {args.expect_email}")
    print("=" * 78)

    try:
        if args.no_browser:
            flow.redirect_uri = f"http://localhost:{args.port}/"
            credentials = flow.run_local_server(
                port=args.port,
                open_browser=False,
                prompt="consent",
                login_hint=args.expect_email,
                authorization_prompt_message="Open this URL to authorize:\n\n{url}\n",
                success_message=(
                    "Green Marketing Drive authorization complete. Return to the terminal."
                ),
            )
        else:
            credentials = flow.run_local_server(
                port=args.port,
                open_browser=True,
                prompt="consent",
                login_hint=args.expect_email,
                # The authorization URL embeds the OAuth client ID, so it is never
                # printed on the browser path. Use --no-browser if you need the URL.
                authorization_prompt_message=(
                    "Your browser has been opened for Google sign-in. "
                    "Complete consent there, then return here.\n"
                ),
                success_message=(
                    "Green Marketing Drive authorization complete. Return to the terminal."
                ),
            )
    except Exception as exc:  # noqa: BLE001
        print(f"\nFAIL: authorization did not complete: {redact_error_text(exc)}")
        print("If the callback port is busy, retry with --port <other port>.")
        return 1

    # Confirm the account BEFORE persisting the token.
    try:
        identity = authorized_identity(build_drive_service(credentials))
    except Exception as exc:  # noqa: BLE001
        print(f"\nFAIL: could not read the authorized identity: {redact_error_text(exc)}")
        print("The token was NOT saved.")
        return 1

    email = identity.get("emailAddress", "")
    if args.expect_email and email.lower() != args.expect_email.lower():
        print(f"\nFAIL: authorized account is {email}, expected {args.expect_email}.")
        print("The token was NOT saved. Re-run and select the correct account.")
        return 1

    save_credentials(credentials, settings.token_file)
    print(f"\nAuthorized account: {email}")
    print("Granted scopes:")
    for scope in granted_scopes(credentials):
        print(f"  - {scope}")
    print(f"\nToken saved to {settings.token_file} (contents never printed).")
    print("Next: python scripts/verify_google_drive_access.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
