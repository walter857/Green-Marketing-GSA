#!/usr/bin/env python3
"""Preflight for PLAN-H - sitelink destination replacement.

APPROVAL RECEIVED: APPROVE PLAN-H 1D63EC1EB68D FOR 1521725229

Verifies, before any mutation:
  * fingerprint and identity
  * the eight current sitelink links still match the plan's recorded state
  * BLAST RADIUS: the four shared assets are linked ONLY to the two in-scope
    campaigns, so unlinking cannot touch anything outside this work order
  * character limits on the four proposed sitelinks
  * FRESH browser verification that all four new destinations are live and
    render the approved tracked number - the plan's own check is 2 days old and
    CLAUDE.md forbids publishing from stale reports

READ ONLY. Issues no mutation.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402
from gm_gsa.safety import approval_code                     # noqa: E402

TZ = ZoneInfo("America/New_York")
CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMP_A = "24103511039"
CAMP_B = "24145053510"
NAMES = {CAMP_A: "Power Washing", CAMP_B: "Power Washing #2"}
APPROVED_FP = "1D63EC1EB68D"
APPROVED = "(631) 502-7946"
APPROVED_DIGITS = "6315027946"
UNTRACKED_DIGITS = "6315025402"
CLIENT = ROOT / "clients/softwind-power-washing"
PLAN_FILE = CLIENT / "plans/2026-08-25-plan-h-sitelink-destinations.yaml"
OUT = CLIENT / "snapshots/h-preflight-2026-08-27.json"

OLD_CAMPAIGN_ASSETS = ["404411414183", "404512529608", "404512534036",
                       "404582047221"]
OLD_CUSTOMER_ASSET = "403671792813"
TEXT_LIMIT, DESC_LIMIT = 25, 35


def normalize(plan: dict) -> dict:
    p = plan["change_plan"]
    t = p["target"]
    actions = []
    for a in p.get("actions", []):
        actions.append({
            "action_id": a["action_id"], "priority": a["priority"],
            "resource_type": a["resource_type"], "operation": a["operation"],
            "customer_id": a.get("customer_id", t["child_customer_id"]),
            "campaign_id": a.get("campaign_id"),
            "ad_group_id": a.get("ad_group_id"),
            "resource_id": a.get("resource_id"),
            "current_value": a.get("current_value"),
            "proposed_value": a.get("proposed_value"),
            "object_count": a.get("object_count", 1)})
    actions.sort(key=lambda x: x["action_id"])
    return {"target": {"exact_child_account_name": t["exact_child_account_name"],
                       "child_customer_id": t["child_customer_id"],
                       "exact_service": t["exact_service"]},
            "plan_id": p["plan_id"], "approval_type": p["approval_type"],
            "actions": actions, "action_count": len(actions),
            "object_count": sum(a["object_count"] for a in actions)}


def rows(svc, q):
    out = []
    for b in svc.search_stream(customer_id=CID, query=q):
        out.extend(b.results)
    return out


def check_destinations(urls):
    """Real Chromium load. These hosts sit behind SG-Captcha and feed non-JS
    clients an empty stub, so curl/WebFetch would give a false reading."""
    from playwright.sync_api import sync_playwright
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for url in urls:
            rec = {"url": url}
            try:
                ctx = browser.new_context(
                    viewport={"width": 1366, "height": 900},
                    user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/124.0 Safari/537.36"))
                page = ctx.new_page()
                paid = url + ("&" if "?" in url else "?") + (
                    "gclid=TESTGCLID_readonly_planh&utm_source=google"
                    "&utm_medium=cpc&utm_campaign=planh_preflight")
                resp = page.goto(paid, wait_until="domcontentloaded", timeout=45000)
                rec["http_status"] = resp.status if resp else None
                page.wait_for_timeout(9000)
                html = page.content()
                tels = re.findall(r'href=["\']tel:([^"\']+)["\']', html)
                rec["tel_links_raw"] = sorted(set(tels))
                digits = {re.sub(r"\D", "", t) for t in tels}
                digits = {d[-10:] for d in digits if len(re.sub(r"\D", "", d)) >= 10}
                rec["tel_digits"] = sorted(digits)
                body = re.sub(r"<[^>]+>", " ", html)
                rec["approved_in_tel"] = APPROVED_DIGITS in digits
                rec["untracked_in_tel"] = UNTRACKED_DIGITS in digits
                rec["approved_in_text"] = (
                    APPROVED in body or APPROVED_DIGITS in re.sub(r"\D", "", body))
                rec["form_count"] = html.count("<form")
                rec["title"] = (page.title() or "")[:120]
                rec["h1"] = ""
                h1 = page.query_selector("h1")
                if h1:
                    rec["h1"] = (h1.inner_text() or "")[:160]
                rec["gclid_preserved"] = "TESTGCLID_readonly_planh" in page.url
                rec["final_url_after_redirects"] = page.url.split("?")[0]
                rec["verdict"] = (
                    "OK" if (rec["http_status"] == 200 and rec["approved_in_tel"]
                             and not rec["untracked_in_tel"]) else "PROBLEM")
                ctx.close()
            except Exception as exc:                          # noqa: BLE001
                rec["error"] = str(exc)[:300]
                rec["verdict"] = "PROBLEM"
            results.append(rec)
        browser.close()
    return results


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)
    r = {"read_only": True, "mutations_issued": 0,
         "timestamp_account_local": now.isoformat()}
    problems = []

    print("=" * 76)
    print("PLAN-H PREFLIGHT  %s" % now.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("=" * 76)

    plan = yaml.safe_load(PLAN_FILE.read_text(encoding="utf-8"))
    p = plan["change_plan"]
    fp = approval_code(normalize(plan))
    r["fingerprint"] = {"recomputed": fp, "approved": APPROVED_FP,
                        "match": fp == APPROVED_FP}
    print("\n1. FINGERPRINT & IDENTITY")
    print("   recomputed %s | approved %s | MATCH %s"
          % (fp, APPROVED_FP, fp == APPROVED_FP))
    if fp != APPROVED_FP:
        problems.append("fingerprint mismatch")

    c = rows(svc, "SELECT customer.id, customer.descriptive_name, customer.manager, "
                  "customer.test_account, customer.currency_code, customer.time_zone "
                  "FROM customer LIMIT 1")[0].customer
    ident_ok = (str(c.id) == CID and c.descriptive_name == NAME
                and not c.manager and not c.test_account
                and c.currency_code == "USD" and c.time_zone == "America/New_York")
    r["identity"] = {"id": str(c.id), "name": c.descriptive_name,
                     "manager": c.manager, "test_account": c.test_account,
                     "ok": ident_ok}
    print("   %s | %s | manager=%s test=%s -> %s"
          % (c.descriptive_name, c.id, c.manager, c.test_account,
             "OK" if ident_ok else "MISMATCH"))
    if not ident_ok:
        problems.append("identity mismatch")

    # ---- current sitelink state ----
    print("\n2. CURRENT SITELINK STATE")
    q = ("SELECT campaign.id, campaign_asset.asset, campaign_asset.field_type, "
         "campaign_asset.status, asset.id, asset.name, "
         "asset.sitelink_asset.link_text, asset.sitelink_asset.description1, "
         "asset.sitelink_asset.description2, asset.final_urls "
         f"FROM campaign_asset WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND campaign_asset.field_type = 'SITELINK' "
         "AND campaign_asset.status != 'REMOVED'")
    camp_links = {}
    for x in rows(svc, q):
        aid = str(x.asset.id)
        camp_links.setdefault(str(x.campaign.id), {})[aid] = {
            "link_text": x.asset.sitelink_asset.link_text,
            "desc1": x.asset.sitelink_asset.description1,
            "desc2": x.asset.sitelink_asset.description2,
            "final_urls": list(x.asset.final_urls),
            "status": x.campaign_asset.status.name}
    r["current_campaign_sitelinks"] = camp_links
    for cid_, links in camp_links.items():
        print("   %s (%s): %d SITELINK links" % (NAMES[cid_], cid_, len(links)))
        for aid, d in sorted(links.items()):
            print("      %-14s %-18s %s" % (aid, d["link_text"][:18],
                                            d["final_urls"][0] if d["final_urls"] else "-"))
    for cid_ in (CAMP_A, CAMP_B):
        got = set(camp_links.get(cid_, {}))
        if set(OLD_CAMPAIGN_ASSETS) - got:
            problems.append("campaign %s missing expected sitelink assets %s"
                            % (cid_, sorted(set(OLD_CAMPAIGN_ASSETS) - got)))

    q = ("SELECT customer_asset.asset, customer_asset.field_type, "
         "customer_asset.status, asset.id, asset.sitelink_asset.link_text, "
         "asset.final_urls FROM customer_asset "
         "WHERE customer_asset.field_type = 'SITELINK' "
         "AND customer_asset.status != 'REMOVED'")
    cust_links = {str(x.asset.id): {
        "link_text": x.asset.sitelink_asset.link_text,
        "final_urls": list(x.asset.final_urls),
        "status": x.customer_asset.status.name} for x in rows(svc, q)}
    r["current_customer_sitelinks"] = cust_links
    print("   ACCOUNT-LEVEL: %d SITELINK links" % len(cust_links))
    for aid, d in sorted(cust_links.items()):
        mark = "  <-- PLAN-H removes this link" if aid == OLD_CUSTOMER_ASSET else ""
        print("      %-14s %-18s %s%s" % (aid, d["link_text"][:18],
                                          d["final_urls"][0] if d["final_urls"] else "-", mark))
    if OLD_CUSTOMER_ASSET not in cust_links:
        problems.append("account-level asset %s link not found" % OLD_CUSTOMER_ASSET)

    # ---- BLAST RADIUS ----
    print("\n3. BLAST RADIUS - where else are these assets linked?")
    blast = {}
    for aid in OLD_CAMPAIGN_ASSETS + [OLD_CUSTOMER_ASSET]:
        camps = [cid_ for cid_, links in camp_links.items() if aid in links]
        at_account = aid in cust_links
        q = ("SELECT ad_group.id, ad_group_asset.status, asset.id "
             "FROM ad_group_asset WHERE asset.id = %s "
             "AND ad_group_asset.status != 'REMOVED'" % aid)
        ag = [str(x.ad_group.id) for x in rows(svc, q)]
        blast[aid] = {"campaigns": sorted(camps), "account_level": at_account,
                      "ad_groups": ag}
        contained = set(camps) <= {CAMP_A, CAMP_B} and not ag
        print("   %-14s campaigns=%s account_level=%s ad_groups=%s -> %s"
              % (aid, sorted(camps), at_account, ag or "none",
                 "CONTAINED" if contained else "OUT OF SCOPE"))
        if not contained:
            problems.append("asset %s links outside the two in-scope campaigns" % aid)
    r["blast_radius"] = blast
    q = "SELECT campaign.id, campaign.name FROM campaign WHERE campaign.status != 'REMOVED'"
    all_camps = {str(x.campaign.id): x.campaign.name for x in rows(svc, q)}
    r["all_campaigns_in_account"] = all_camps
    print("   Account contains %d non-removed campaigns: %s"
          % (len(all_camps), list(all_camps.values())))
    print("   -> account-level sitelink removal blast radius is fully contained: %s"
          % (set(all_camps) <= {CAMP_A, CAMP_B}))
    if not set(all_camps) <= {CAMP_A, CAMP_B}:
        problems.append("account contains campaigns outside this work order; "
                        "account-level link removal would reach them")

    # ---- character limits ----
    print("\n4. PROPOSED SITELINK CHARACTER LIMITS")
    proposed = p["proposed_sitelinks"]
    for s in proposed:
        t_ok = len(s["sitelink_text"]) <= TEXT_LIMIT
        d1_ok = len(s["description1"]) <= DESC_LIMIT
        d2_ok = len(s["description2"]) <= DESC_LIMIT
        print("   %-18s text=%2d/%d desc1=%2d/%d desc2=%2d/%d  %s"
              % (s["sitelink_text"], len(s["sitelink_text"]), TEXT_LIMIT,
                 len(s["description1"]), DESC_LIMIT,
                 len(s["description2"]), DESC_LIMIT,
                 "OK" if (t_ok and d1_ok and d2_ok) else "OVER LIMIT"))
        if not (t_ok and d1_ok and d2_ok):
            problems.append("sitelink '%s' exceeds a character limit" % s["sitelink_text"])
    r["proposed_sitelinks"] = proposed

    # ---- FRESH destination verification ----
    print("\n5. FRESH BROWSER VERIFICATION OF THE FOUR NEW DESTINATIONS")
    print("   (the plan's own check is from 2026-08-25 and is now stale)")
    dests = check_destinations([s["final_url"] for s in proposed])
    r["destination_verification"] = dests
    for d in dests:
        print("   %s" % d["url"])
        if d.get("error"):
            print("      ERROR %s" % d["error"])
        else:
            print("      status=%s tel=%s approved=%s untracked=%s forms=%s gclid=%s -> %s"
                  % (d.get("http_status"), d.get("tel_digits"),
                     d.get("approved_in_tel"), d.get("untracked_in_tel"),
                     d.get("form_count"), d.get("gclid_preserved"), d["verdict"]))
            print("      h1: %s" % d.get("h1", "")[:100])
        if d["verdict"] != "OK":
            problems.append("destination not verified: %s" % d["url"])

    r["problems"] = problems
    r["clear_to_execute"] = not problems
    OUT.write_text(json.dumps(r, indent=2), encoding="utf-8")

    print("\n" + "=" * 76)
    if problems:
        print("RESULT: BLOCKED - %d problem(s). NOTHING WAS CHANGED." % len(problems))
        for x in problems:
            print("   !! %s" % x)
    else:
        print("RESULT: CLEAR TO EXECUTE - 21 mutations, order link-then-unlink")
    print("=" * 76)
    print("wrote %s" % OUT)
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
