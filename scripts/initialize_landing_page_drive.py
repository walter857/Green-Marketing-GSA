#!/usr/bin/env python3
"""Initialize the approved Green Marketing landing-page scaffold in Google Drive.

Dry-run is the default. Nothing is written unless --apply is passed explicitly.

Scope of this script, and nothing more:

    Green Marketing Landing Pages/
      Templates/
        TEMP - Master Template Scrub In Progress   (copy of the canonical native Google Doc)
          -> scrubbed, re-read, validated, then renamed to
        Landing Page Content Template - Master

No client folder is ever created here. Nothing is deleted, trashed, moved, or shared.

The master document is never copied straight to its final name. That name is a promise that
the document carries no source-client facts, and it can only be earned by renaming a TEMP
copy that has already passed content and structure validation.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.google_drive import (  # noqa: E402
    DOCUMENT_MIME_TYPE,
    MASTER_TEMPLATE_NAME,
    TEMP_SCRUB_NAME,
    DriveAmbiguityError,
    DriveAuthorizationError,
    PartialWriteError,
    authorized_identity,
    build_docs_service,
    build_drive_service,
    drive_url,
    load_drive_settings,
    load_stored_credentials,
    redact_error_text,
)
from gm_gsa.master_template import (  # noqa: E402
    STATUS_BLOCKED_TEMP_EXISTS,
    STATUS_REUSE_MASTER,
    MasterTemplateBlockedError,
    apply_master_template,
    expected_new_resources,
    format_pipeline,
    plan_master_template,
)
from gm_gsa.template_scrub import load_scrub_manifest  # noqa: E402

EXPECTED_EMAIL = "access@greenmarketingfl.com"
MANIFEST_PATH = ROOT / "config" / "landing-page-template-scrub.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Plan (default) or apply the landing-page Drive scaffold and master template."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually run the sequence. Without this flag nothing is written.",
    )
    parser.add_argument("--expect-email", default=EXPECTED_EMAIL)
    parser.add_argument("--manifest", default=str(MANIFEST_PATH))
    args = parser.parse_args()

    settings = load_drive_settings()
    manifest = load_scrub_manifest(args.manifest)

    try:
        credentials = load_stored_credentials(settings)
    except DriveAuthorizationError as exc:
        print(f"FAIL: {exc}")
        return 1

    drive_service = build_drive_service(credentials)
    docs_service = build_docs_service(credentials)

    try:
        identity = authorized_identity(drive_service)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: identity check failed: {redact_error_text(exc)}")
        return 1

    email = identity.get("emailAddress", "")
    if args.expect_email and email.lower() != args.expect_email.lower():
        print(f"FAIL: authorized as {email}, expected {args.expect_email}. Stopping.")
        return 1
    print(f"Authorized account: {email}")
    print(f"Canonical source (READ-ONLY, never modified): {settings.canonical_source_template_id}")

    try:
        plan = plan_master_template(drive_service, settings)
    except DriveAmbiguityError as exc:
        print(f"FAIL: {exc}")
        print("Duplicate exact-name matches are never guessed at. Resolve them in Drive first.")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: planning failed: {redact_error_text(exc)}")
        return 1

    print("\n--- PLANNED SEQUENCE ---")
    print(format_pipeline(plan))
    print(f"\nSummary: {plan.summary()}")
    for note in plan.notes:
        print(f"NOTE: {note}")

    print("\n--- RESOURCES A FUTURE --apply WOULD CREATE ---")
    expected = expected_new_resources(plan, settings)
    if expected:
        for item in expected:
            print(f"  - {item}")
    else:
        print("  (none)")

    if plan.status == STATUS_BLOCKED_TEMP_EXISTS:
        print("\nBLOCKED. A TEMP copy exists with no validated master.")
        print(f"  ID  : {plan.temp_id}")
        print(f"  URL : {drive_url(str(plan.temp_id), DOCUMENT_MIME_TYPE)}")
        print("Review that document by hand. Nothing will be copied, renamed, or deleted.")
        return 1

    if plan.status == STATUS_REUSE_MASTER:
        print(f"\nThe validated master {MASTER_TEMPLATE_NAME!r} already exists and is reused.")
        print(f"  ID  : {plan.final_master_id}")
        print(f"  URL : {drive_url(str(plan.final_master_id), DOCUMENT_MIME_TYPE)}")

    if not args.apply:
        print("\nDRY RUN - no Drive write, no Docs write, no local configuration write.")
        print("Re-run with --apply only after explicit approval of the sequence above.")
        return 0

    print("\n--- APPLYING ---")
    try:
        report = apply_master_template(
            drive_service, docs_service, settings, manifest, plan
        )
    except MasterTemplateBlockedError as exc:
        print(f"FAIL: {exc}")
        return 1
    except PartialWriteError as exc:
        print(f"FAIL: {redact_error_text(exc)}")
        print("\nPARTIAL WRITE. Every resource already created:")
        for item in exc.inventory():
            url = item.get("url") or drive_url(str(item["id"]), str(item.get("mimeType", "")))
            print(f"  - {item['key']}: {item['name']} ({item['id']})")
            print(f"      URL: {url}")
        print(f"\nAny copy is still named {TEMP_SCRUB_NAME!r}. The canonical source is unchanged.")
        print("Nothing was deleted, trashed, moved, or shared. Do not blindly rerun.")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {redact_error_text(exc)}")
        return 1

    print("\n--- READBACK ---")
    for step in report["steps"]:
        print(f"  {step['key']}: {step['outcome']}")
    print(f"\nRoot folder ID     : {report['root_folder_id']}")
    print(f"Master template ID : {report['master_template_document_id']}")
    print(f"Master template URL: {report['master_template_url']}")
    print("\nBoth non-secret IDs were recorded in config/google-drive.yaml.")
    print("Re-run this script without --apply to confirm it now plans zero new resources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
