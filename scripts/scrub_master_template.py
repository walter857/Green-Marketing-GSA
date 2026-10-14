#!/usr/bin/env python3
"""Analyze the landing-page master-template scrub against the canonical example.

Dry-run is the default. Nothing is copied, written, or renamed without --apply.

The dry run is entirely offline: it fetches the canonical document read-only, simulates the
scrub in memory, and proves the manifest drives the source-client facts to zero while
leaving the structure identical. No Drive or Docs write is issued.

--apply delegates to gm_gsa.master_template, the repository's single apply sequence. This
script has no copy, batchUpdate, or rename call of its own, so there is exactly one code
path that can produce the master template, and that path always goes through the TEMP name.

The canonical document is protected by gm_gsa.template_scrub. Every write helper refuses to
target it, so the worst case is a partially scrubbed TEMP copy, never a damaged source.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.google_drive import (  # noqa: E402
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
    TEMP_SCRUB_NAME,
    MasterTemplateBlockedError,
    apply_master_template,
    format_pipeline,
    plan_master_template,
)
from gm_gsa.template_scrub import (  # noqa: E402
    ScrubValidationError,
    assert_structure_preserved,
    document_structure_fingerprint,
    load_scrub_manifest,
    plan_scrub,
    simulate_scrub,
    validate_scrubbed,
)

EXPECTED_EMAIL = "access@greenmarketingfl.com"
MANIFEST_PATH = ROOT / "config" / "landing-page-template-scrub.yaml"


def fetch(docs_service, document_id: str) -> dict:
    return (
        docs_service.documents()
        .get(documentId=document_id, includeTabsContent=True)
        .execute()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan or apply the master-template scrub.")
    parser.add_argument("--apply", action="store_true", help="Perform the copy and scrub.")
    parser.add_argument("--expect-email", default=EXPECTED_EMAIL)
    parser.add_argument("--manifest", default=str(MANIFEST_PATH))
    parser.add_argument("--show-detections", action="store_true")
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

    identity = authorized_identity(drive_service)
    email = identity.get("emailAddress", "")
    if args.expect_email and email.lower() != args.expect_email.lower():
        print(f"FAIL: authorized as {email}, expected {args.expect_email}.")
        return 1
    print(f"Authorized account: {email}")

    canonical_id = settings.canonical_source_template_id
    if manifest.source_document_id != canonical_id:
        print("FAIL: manifest source_document_id does not match the configured canonical ID.")
        return 1

    print(f"Canonical source (READ-ONLY): {canonical_id}")
    canonical = fetch(docs_service, canonical_id)
    print(f"Canonical title: {canonical.get('title')!r}")

    plan = plan_scrub(canonical, manifest, document_id=None)
    fingerprint = document_structure_fingerprint(canonical)
    summary = plan.summary()

    print("\n--- SCRUB PLAN ---")
    print(f"Replacement rules          : {len(manifest.rules)}")
    print(f"Rules matching the source  : {summary['detected_rules']}")
    print(f"Total occurrences detected : {summary['detected_occurrences']}")
    print(f"Rules with NO match        : {summary['unmatched_rules']}")
    print(f"Link/rich-link requests    : {summary['link_requests']}")
    print(f"replaceAllText requests    : {summary['text_requests']}")
    print(f"Forbidden terms to verify  : {len(manifest.forbidden_after_scrub)}")

    print("\n--- CANONICAL STRUCTURE FINGERPRINT ---")
    print(f"Tabs        : {fingerprint['tab_count']}")
    print(f"Paragraphs  : {fingerprint['paragraph_count']}")
    print(f"Bullets     : {fingerprint['bullet_count']}")
    print(f"Tables      : {fingerprint['tables'] or 'none'}")

    if plan.unmatched:
        print("\n--- RULES WITH NO MATCH (review these) ---")
        for rule in plan.unmatched:
            print(f"  [{rule.category}] {rule.find[:90]!r}")

    if args.show_detections:
        print("\n--- DETECTED CLIENT-SPECIFIC ITEMS ---")
        for detection in plan.detections:
            rule = detection.rule
            print(f"  [{rule.category}] x{detection.occurrences}  {rule.find[:80]!r}")
            print(f"      -> {rule.replace[:80]!r}")

    residual = validate_scrubbed(canonical, manifest.forbidden_after_scrub)
    print(f"\nSource-client facts present in the canonical document: {len(residual)}")
    print("(That count is expected to be high. It is the baseline the scrub must drive to 0.)")

    print("\n--- OFFLINE SIMULATION (no API call, canonical untouched) ---")
    simulated = simulate_scrub(canonical, manifest)
    remaining = validate_scrubbed(simulated, manifest.forbidden_after_scrub)
    sim_fingerprint = document_structure_fingerprint(simulated)
    print(f"Residual source-client facts after simulated scrub: {len(remaining)}")
    for violation in remaining[:15]:
        print(f"  ! {violation.term!r} at {violation.where}: {violation.sample[:90]!r}")
    try:
        assert_structure_preserved(fingerprint, sim_fingerprint)
        print("Structure preserved: YES (paragraphs, styles, bullets, tables, tabs identical)")
    except ScrubValidationError as exc:
        print(f"Structure preserved: NO - {exc}")

    print("\n--- THE SEQUENCE THAT --apply WOULD RUN ---")
    try:
        pipeline = plan_master_template(drive_service, settings)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: planning failed: {redact_error_text(exc)}")
        return 1
    print(format_pipeline(pipeline))
    for note in pipeline.notes:
        print(f"NOTE: {note}")

    if not args.apply:
        print("\nDRY RUN - no Drive or Docs write was issued.")
        print("Nothing was copied, modified, renamed, or recorded.")
        return 0

    # ---------------- apply ----------------
    # Delegated so that the copy-to-TEMP, scrub, re-read, validate, rename, and record
    # sequence exists in exactly one place and cannot drift between the two scripts.
    try:
        report = apply_master_template(
            drive_service, docs_service, settings, manifest, pipeline
        )
    except MasterTemplateBlockedError as exc:
        print(f"\nFAIL: {exc}")
        return 1
    except PartialWriteError as exc:
        print(f"\nFAIL: {redact_error_text(exc)}")
        print("\nPARTIAL RESOURCES - inventory:")
        for item in exc.inventory():
            url = item.get("url") or drive_url(str(item["id"]), str(item.get("mimeType", "")))
            print(f"  - {item['key']}: {item['name']} ({item['id']})")
            print(f"      URL: {url}")
        print(f"\nAny document copy is still named {TEMP_SCRUB_NAME!r}.")
        print("The canonical source was not modified. Nothing was deleted, trashed, moved,")
        print("or shared. Review before any retry. Do not blindly rerun.")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"\nFAIL: {redact_error_text(exc)}")
        return 1

    print("\nValidation passed.")
    print(f"  Master ID  : {report['master_template_document_id']}")
    print(f"  Master URL : {report['master_template_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
