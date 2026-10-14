#!/usr/bin/env python3
"""Verify the separate Drive/Docs authorization without exposing any secret.

Reports the authorized account, the scopes Google actually granted, Drive and Docs API
connectivity, and whether the canonical native Google Doc template is reachable under the
current least-privilege scopes.

This script is read-only. It creates, modifies, shares, and deletes nothing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.google_drive import (  # noqa: E402
    DRIVE_SCOPES,
    DriveAuthorizationError,
    authorized_identity,
    build_docs_service,
    build_drive_service,
    check_template_access,
    granted_scopes,
    load_drive_settings,
    load_stored_credentials,
    redact_error_text,
)

EXPECTED_EMAIL = "access@greenmarketingfl.com"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Green Marketing Drive/Docs access.")
    parser.add_argument("--expect-email", default=EXPECTED_EMAIL)
    args = parser.parse_args()

    settings = load_drive_settings()
    described = settings.describe()

    print("=" * 78)
    print("GREEN MARKETING DRIVE / DOCS ACCESS VERIFICATION")
    print("=" * 78)
    print(f"OAuth client file present : {described['credentials_file_present']}")
    print(f"Token file present        : {described['token_file_present']}")
    print(f"Configured root folder    : {described['root_folder_name']}")
    print(f"Configured root folder ID : {described['root_folder_id'] or '(not set yet)'}")
    print(f"Canonical template ID     : {described['canonical_source_template_id']}")
    print("Configured scopes         :")
    for scope in described["scopes"]:
        print(f"  - {scope}")

    try:
        credentials = load_stored_credentials(settings)
    except DriveAuthorizationError as exc:
        print(f"\nFAIL: {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"\nFAIL: could not load credentials: {redact_error_text(exc)}")
        return 1

    drive_service = build_drive_service(credentials)
    docs_service = build_docs_service(credentials)

    print("\n--- Identity ---")
    try:
        identity = authorized_identity(drive_service)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: Drive API identity check failed: {redact_error_text(exc)}")
        return 1

    email = identity.get("emailAddress", "")
    print(f"Authorized account : {email}")
    print(f"Display name       : {identity.get('displayName', '')}")

    actual_scopes = granted_scopes(credentials)
    print("Granted scopes     :")
    for scope in actual_scopes:
        print(f"  - {scope}")

    unexpected = [s for s in actual_scopes if s not in set(DRIVE_SCOPES)]
    if unexpected:
        print("NOTE: scopes granted beyond the two configured Drive/Docs scopes:")
        for scope in unexpected:
            print(f"  ! {scope}")

    failed = False
    if args.expect_email and email.lower() != args.expect_email.lower():
        print(f"\nFAIL: expected {args.expect_email}, got {email}. Stopping.")
        return 1

    print("\n--- API connectivity ---")
    print("Drive API : OK (about.get succeeded)")

    print("\n--- Canonical template access ---")
    report = check_template_access(
        drive_service, docs_service, settings.canonical_source_template_id
    )
    drive_result = report.get("drive", {})
    docs_result = report.get("docs", {})

    if drive_result.get("accessible"):
        print(f"Drive metadata : OK - {drive_result.get('name')!r}")
        print(f"  MIME type          : {drive_result.get('mimeType')}")
        print(f"  Native Google Doc  : {drive_result.get('is_native_google_doc')}")
        print(f"  Copyable           : {drive_result.get('can_copy')}")
    else:
        failed = True
        print(f"Drive metadata : NOT ACCESSIBLE ({drive_result.get('kind')})")
        print(f"  HTTP status : {drive_result.get('status')}")
        print(f"  Message     : {drive_result.get('message')}")

    if docs_result.get("accessible"):
        print(f"Docs API       : OK - title {docs_result.get('title')!r}")
    else:
        kind = docs_result.get("kind")
        if kind == "api_not_enabled":
            failed = True
            print("Docs API       : NOT ENABLED in the Cloud project")
        else:
            print(f"Docs API       : reachable, template not accessible ({kind})")
        print(f"  HTTP status : {docs_result.get('status')}")
        print(f"  Message     : {docs_result.get('message')}")

    print("\n" + "=" * 78)
    if failed:
        print("RESULT: BLOCKED")
        print(
            "The narrow drive.file scope only reaches files this OAuth app created or that\n"
            "were explicitly opened with it. Do NOT broaden the scope without approval.\n"
            "Options: (1) grant the template to this app via a Google Picker selection, or\n"
            "(2) obtain separate written approval for the broader drive scope."
        )
        return 2
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
