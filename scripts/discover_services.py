#!/usr/bin/env python3
"""Discover the services a live child account advertises. Read-only.

Sequence: validate the discovery document, confirm the exact child account name
and 10-digit child customer ID against a fresh Google Ads identity lookup,
confirm the manager relationship and account type, read only enabled resources,
GET the public landing pages, then report candidate services with evidence.

This command never creates, updates, pauses, enables, removes, or deletes
anything, and it never authorizes the audit that follows.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, load_yaml
from gm_gsa.landing_pages import hosts_from_urls, read_landing_pages
from gm_gsa.service_discovery import (
    DiscoveryError,
    assert_discovery_identity,
    assert_manager_link,
    classify_services,
    collect_account_evidence,
    collect_final_urls,
    discovery_target,
    get_manager_link,
)


def _print_header(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discovery", required=True)
    parser.add_argument("--client", help="Optional client profile to cross-check.")
    parser.add_argument("--output", help="Where to write the JSON discovery report.")
    parser.add_argument(
        "--no-landing-pages",
        action="store_true",
        help="Skip the read-only landing-page GETs.",
    )
    parser.add_argument("--max-landing-pages", type=int, default=None)
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Validate and print the planned read-only steps without calling the API.",
    )
    args = parser.parse_args()

    document = load_yaml(args.discovery)
    profile = load_yaml(args.client) if args.client else None
    try:
        target = discovery_target(document, profile)
    except DiscoveryError as exc:
        print(f"STOP: {exc}")
        return 1

    _print_header("Authorized read-only service-discovery target")
    print(f"Account name : {target.exact_child_account_name}")
    print(f"Child ID     : {target.child_customer_id}")
    print(f"Manager ID   : {target.manager_customer_id}")
    print("Mode         : read-only service discovery (no exact service required or asserted)")

    if args.plan_only:
        _print_header("Planned read-only steps")
        for step in (
            "customer identity lookup (FROM customer)",
            "manager link check (FROM customer_client)",
            "enabled campaigns, ad groups, keywords, ads",
            "enabled campaign, ad group, and customer assets",
            "public landing-page GET for observed final URLs",
        ):
            print(f"- {step}")
        print("\nNo API call was made.")
        return 0

    load_dotenv_if_available(ROOT / ".env")
    from gm_gsa.credentials import google_ads_config, load_google_ads_client

    configured_login = google_ads_config()["login_customer_id"]
    if configured_login != target.manager_customer_id:
        print(
            "\nSTOP: the configured login customer ID does not match the authorized "
            "manager customer ID in the discovery document. No value was printed."
        )
        return 1

    google_client = load_google_ads_client()

    from gm_gsa.google_ads import get_customer_identity

    try:
        identity = get_customer_identity(google_client, target.child_customer_id)
        assert_discovery_identity(identity, target)
        link = get_manager_link(
            google_client, target.manager_customer_id, target.child_customer_id
        )
        assert_manager_link(link, target)
    except DiscoveryError as exc:
        print(f"\nSTOP: {exc}")
        return 1

    _print_header("Identity verification")
    print(f"Observed name        : {identity.descriptive_name}")
    print(f"Observed customer ID : {identity.customer_id}")
    print(f"Currency / time zone : {identity.currency_code} / {identity.time_zone}")
    print(f"Manager account      : {identity.manager}")
    print(f"Test account         : {identity.test_account}")
    print(
        f"Manager link         : level {link.level} under {link.manager_customer_id}, "
        f"status {link.status}"
    )
    print("Identity: PASS. The '- Live' marker is still not authorization.")

    evidence = collect_account_evidence(google_client, target)
    final_urls = collect_final_urls(evidence)

    landing_pages: list[dict] = []
    if target.fetch_landing_pages and not args.no_landing_pages and final_urls:
        allowed = target.allowed_hosts or hosts_from_urls(item["url"] for item in final_urls)
        landing_pages = read_landing_pages(
            (item["url"] for item in final_urls),
            allowed_hosts=allowed,
            max_pages=args.max_landing_pages or target.max_landing_pages,
        )

    classification = classify_services(evidence, landing_pages)

    _print_header("Read-only account evidence")
    print(f"Enabled campaigns : {len(evidence['campaigns'])}")
    print(f"Enabled ad groups : {len(evidence['ad_groups'])}")
    print(f"Enabled keywords  : {len(evidence['keywords'])}")
    print(f"Enabled ads       : {len(evidence['ads'])}")
    print(f"Enabled assets    : {len(evidence['assets'])}")
    print(f"Distinct final URLs: {len(final_urls)}")
    print(f"Landing pages read : {sum(1 for page in landing_pages if page.get('ok'))}")
    if evidence["read_errors"]:
        print("\nResources that could not be read (reported, not silently skipped):")
        for failure in evidence["read_errors"]:
            print(f"- {failure['resource']}: {failure['error']}")
    if evidence["non_removed_campaign_index"]:
        print(
            "\nNo campaign is enabled. Non-removed campaigns found "
            f"({len(evidence['non_removed_campaign_index'])}):"
        )
        for campaign in evidence["non_removed_campaign_index"]:
            print(f"- {campaign['name']} | {campaign['id']} | {campaign['status']}")

    if landing_pages:
        _print_header("Landing-page coverage (read-only GET)")
        for page in landing_pages:
            if page.get("ok"):
                print(f"[READ] {page['url']}")
                print(f"       title    : {page.get('title', '')}")
                print(f"       canonical: {page.get('canonical_url', '')}")
                print(f"       h1       : {'; '.join(page.get('h1', []))}")
                print(f"       headings : {'; '.join(page.get('headings', [])[:12])}")
            else:
                print(f"[FAIL] {page['url']}")
                print(f"       {page.get('error', 'unknown error')}")

    _print_header("Candidate services")
    if not classification["candidates"]:
        print("No candidate service matched the lexicon. Review the unmatched signals below.")
    for candidate in classification["candidates"]:
        print(
            f"[{candidate['confidence'].upper():6}] {candidate['service']} "
            f"({candidate['vertical']}) | evidence: {', '.join(candidate['evidence_kinds'])} "
            f"| matches: {candidate['match_count']}"
        )
        for note in candidate["notes"]:
            print(f"          note: {note}")

    unmatched = classification["unmatched_signals"]
    if unmatched["names_without_a_service_match"]:
        _print_header("Campaign and ad group names with no service match")
        for item in unmatched["names_without_a_service_match"]:
            print(f"- {item['kind']}: {item['text']}")

    if classification["conflicts"]:
        _print_header("Conflicts and ambiguity")
        for conflict in classification["conflicts"]:
            print(f"- {conflict['type']}: {conflict['note']} ({', '.join(conflict['services'])})")

    report = {
        "workflow": "read-only-service-discovery",
        "target": target.to_dict(),
        "identity": identity.to_dict(),
        "manager_link": link.to_dict(),
        "evidence": evidence,
        "final_urls": final_urls,
        "landing_pages": landing_pages,
        "classification": classification,
        "google_ads_changes_made": False,
        "next_step": (
            "Ask the user to confirm the exact service or services. No audit, draft, "
            "build, revamp, or write may start until that confirmation is in a work order."
        ),
    }
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nWrote read-only discovery report: {output}")

    print("\nNo Google Ads changes were made. Discovery is read-only.")
    print("Confirm the exact service before any audit, draft, build, revamp, or write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
