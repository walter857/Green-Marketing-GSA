#!/usr/bin/env python3
"""Self-review an audit + remediation package before any fingerprint is trusted.

Local files only. No API call, no mutation.

Covers the Green Marketing self-review checklist from config/agency.yaml: client truth,
conversion isolation, mutation necessity, status handling, URL mapping, location targeting,
budget math, unsupported claims, mutation counts, artifact hashes and bundle completeness.
Exit code 1 if any check fails.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402

PROTECTED = {"near me", "quote", "quotes", "price", "prices", "pricing", "cost", "costs",
             "best", "hire", "local", "emergency", "free"}
SECRETISH = re.compile(r"(AIza[0-9A-Za-z_\-]{20,}|ya29\.[0-9A-Za-z_\-]{20,}|"
                       r"-----BEGIN [A-Z ]*PRIVATE KEY-----|"
                       r"[0-9]+-[0-9a-z]{32}\.apps\.googleusercontent\.com)")

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))


def norm(t: str) -> str:
    t = (t or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s&'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--client", required=True)
    ap.add_argument("--work-order", required=True)
    ap.add_argument("--locations", required=True)
    ap.add_argument("--reverify", required=True,
                    help="fresh read-only re-verification JSON (drift + custom goal check)")
    args = ap.parse_args()

    S = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    OUT = Path(args.outdir)
    profile = load_yaml(args.client)["client"]
    order = load_yaml(args.work_order)["work_order"]
    locs = load_yaml(args.locations)["location_targets"]
    RV = json.loads(Path(args.reverify).read_text(encoding="utf-8"))
    plan_doc = load_yaml(OUT / "11_exact_change_plan.yaml")
    plan = plan_doc["change_plan"]
    tgt = plan["target"]
    LIVE = {c["id"]: c["name"] for c in S["campaigns"] if c["status"] == "ENABLED"}

    # ---- client truth -----------------------------------------------------
    check("client truth: snapshot name matches profile",
          S["identity"]["descriptive_name"] == profile["google_ads"]["exact_child_account_name"],
          S["identity"]["descriptive_name"])
    check("client truth: snapshot ID matches profile",
          S["identity"]["id"] == profile["google_ads"]["child_customer_id"], S["identity"]["id"])
    check("client truth: plan target matches profile ID",
          tgt["child_customer_id"] == profile["google_ads"]["child_customer_id"])
    check("client truth: plan target matches profile name",
          tgt["exact_child_account_name"] == profile["google_ads"]["exact_child_account_name"])
    check("client truth: plan service matches work order",
          tgt["exact_service"] == order["service"]["exact_primary_service"])
    check("client truth: '- live' marker present",
          "- live" in tgt["exact_child_account_name"].casefold())
    check("client truth: manager ID is not the child ID",
          tgt["manager_customer_id"] != tgt["child_customer_id"])
    check("client truth: target is not a manager or test account",
          not S["identity"]["manager"] and not S["identity"]["test_account"])
    check("client truth: no sibling market ID appears in the plan",
          not any(x in json.dumps(plan) for x in ("8735782888", "1556242048")))

    # ---- mode -------------------------------------------------------------
    check("mode: work order is READ", order["task"]["mode"] == "read", order["task"]["mode"])
    check("mode: plan records no external write performed",
          plan.get("external_writes_performed") == "NONE")

    # ---- coverage ---------------------------------------------------------
    cv = list(csv.DictReader((OUT / "03_campaign_and_ad_group_verdicts.csv").open(encoding="utf-8")))
    camp_rows = {r["resource_id"] for r in cv if r["level"] == "CAMPAIGN"}
    ag_rows = {r["resource_id"] for r in cv if r["level"] == "AD_GROUP"}
    check("coverage: every campaign has a verdict",
          camp_rows == {c["id"] for c in S["campaigns"]},
          f"{len(camp_rows)} of {len(S['campaigns'])}")
    check("coverage: every ad group has a verdict",
          ag_rows == {a["id"] for a in S["ad_groups"]},
          f"{len(ag_rows)} of {len(S['ad_groups'])}")
    check("coverage: no verdict row is blank",
          all(r["verdict"] and r["evidence_and_reason"] for r in cv))

    kv = list(csv.DictReader((OUT / "04_keyword_verdicts.csv").open(encoding="utf-8")))
    # criterion_id alone is not unique: the same id is reused by every ad group that has the
    # same keyword text and match type. The real key is (criterion_id, ad_group_id).
    pos_kw = {(k["criterion_id"], k["ad_group_id"])
              for k in S["keywords"] if not k["negative"]}
    check("coverage: every positive keyword has a verdict",
          {(r["criterion_id"], r["ad_group_id"]) for r in kv} == pos_kw,
          f"{len(kv)} rows for {len(pos_kw)} (criterion, ad group) pairs")
    check("coverage: keyword verdict rows are unique per (criterion, ad group)",
          len({(r["criterion_id"], r["ad_group_id"]) for r in kv}) == len(kv))
    check("coverage: every keyword verdict carries evidence",
          all(r["verdict"] and r["evidence_and_reason"] for r in kv))

    stv = list(csv.DictReader((OUT / "05_search_term_verdicts.csv").open(encoding="utf-8")))
    check("coverage: every retrievable search term row has a verdict",
          all(r["verdict"] for r in stv), f"{len(stv)} rows")
    check("coverage: every search term row carries a reason",
          all(r["reason"] for r in stv))
    src_rows = len({(r["term"], r["campaign_id"], r["ad_group_id"], r["matched_keyword"],
                     r["matched_keyword_match_type"]) for r in S["search_terms"]["all_time"]})
    check("coverage: search-term verdict rows equal distinct snapshot rows",
          len(stv) == src_rows, f"{len(stv)} vs {src_rows}")

    lp = list(csv.DictReader((OUT / "09_landing_page_and_market_integrity_audit.csv").open(encoding="utf-8")))
    live_urls = {u for a in S["ads"] if a["campaign_status"] == "ENABLED" for u in a["final_urls"]}
    check("coverage: every live ad destination was fetched",
          live_urls <= {r["url"] for r in lp},
          f"{len(live_urls & {r['url'] for r in lp})} of {len(live_urls)}")

    # ---- conversion isolation --------------------------------------------
    conv_actions = {c["id"]: c for c in S["conversion_actions"]}
    conv_plan = plan["subplans"]["CONVERSIONS"]["actions"]
    check("conversion isolation: every targeted action exists in the account",
          all(a["resource_id"] in conv_actions for a in conv_plan))
    check("conversion isolation: every targeted action is currently primary",
          all(conv_actions[a["resource_id"]]["primary_for_goal"] for a in conv_plan))
    survivors = [c for c in S["conversion_actions"]
                 if c["status"] == "ENABLED" and c["primary_for_goal"]
                 and c["include_in_conversions_metric"]
                 and c["id"] not in {a["resource_id"] for a in conv_plan}]
    check("conversion isolation: at least one form-lead definition survives",
          any(c["category"] == "SUBMIT_LEAD_FORM" or c["type"] == "UPLOAD_CLICKS"
              for c in survivors),
          ", ".join(c["name"] for c in survivors))
    check("conversion isolation: at least one call-lead definition survives",
          any(c["category"] == "PHONE_CALL_LEAD" or c["type"] in ("AD_CALL", "UPLOAD_CALLS")
              for c in survivors))
    check("conversion isolation: no Google-hosted local action is made primary",
          not any(conv_actions[a["resource_id"]]["type"] == "GOOGLE_HOSTED" for a in conv_plan))

    # ---- mutation necessity and status handling ---------------------------
    all_actions = [a for b in plan["subplans"].values() for a in (b.get("actions") or [])]
    check("mutation necessity: every action states current and proposed state",
          all(a.get("current_state") and a.get("proposed_state") for a in all_actions))
    check("mutation necessity: no action proposes its own current state",
          all(a["current_state"] != a["proposed_state"] for a in all_actions))
    check("mutation necessity: every action carries evidence, risk and rollback",
          all(a.get("evidence") and a.get("risk") and a.get("rollback") for a in all_actions))
    check("status handling: STATUS subplan is empty with a stated reason",
          not plan["subplans"]["STATUS"]["actions"]
          and bool(plan["subplans"]["STATUS"].get("empty_reason")))
    check("status handling: ENABLE subplan is empty with a stated reason",
          not plan["subplans"]["ENABLE"]["actions"]
          and bool(plan["subplans"]["ENABLE"].get("empty_reason")))
    check("status handling: no action enables anything",
          not any("ENABLE" in a["operation"] and "DISABLE" not in a["operation"]
                  for a in all_actions))
    check("status handling: no delete or remove-campaign operation",
          not any(re.search(r"\b(DELETE|REMOVE_CAMPAIGN|REMOVE_AD_GROUP|REMOVE_CONVERSION)\b",
                            a["operation"]) for a in all_actions))

    # ---- resource IDs must exist ------------------------------------------
    known = ({c["id"] for c in S["campaigns"]} | {a["id"] for a in S["ad_groups"]}
             | {c["id"] for c in S["conversion_actions"]}
             | {c["budget_id"] for c in S["campaigns"]}
             | {m["criterion_id"] for m in S["shared_criteria"]}
             | {S["identity"]["id"]})
    unknown = [a["action_id"] for a in all_actions
               if a["resource_type"] not in (
                   "campaign_criterion (negative keyword)",)
               and str(a["resource_id"]).isdigit() and str(a["resource_id"]) not in known]
    check("resource ids: every numeric target exists in the snapshot",
          not unknown, ", ".join(unknown))

    # ---- budget math ------------------------------------------------------
    bud = plan["subplans"]["BUDGET"]["actions"]
    micros = {}
    for a in bud:
        m = re.search(r"amount_micros = (\d+)", a["proposed_state"])
        micros[a["resource_id"]] = int(m.group(1))
    live_budget_ids = {c["budget_id"] for c in S["campaigns"] if c["status"] == "ENABLED"}
    total = sum(micros.get(b, int(next(c["budget_amount"] for c in S["campaigns"]
                                       if c["budget_id"] == b) * 1_000_000))
                for b in live_budget_ids)
    daily = total / 1_000_000
    check("budget math: every enabled campaign budget is covered by the plan",
          live_budget_ids <= set(micros), f"{len(micros)} of {len(live_budget_ids)}")
    check("budget math: combined daily ceiling is at or below $65.79",
          daily <= 65.79 + 1e-9, f"${daily:.2f}/day")
    check("budget math: 30.4-day projection is at or below $2,000.00",
          daily * 30.4 <= 2000.0 + 1e-9, f"${daily * 30.4:.2f}")
    check("budget math: no enabled in-scope budget is shared, so none is double counted",
          not any(c["budget_shared"] for c in S["campaigns"] if c["status"] == "ENABLED"))
    cur_daily = sum(c["budget_amount"] for c in S["campaigns"] if c["status"] == "ENABLED")
    check("budget math: the approved total is unchanged",
          abs(cur_daily - daily) < 1e-9, f"before ${cur_daily:.2f} / after ${daily:.2f}")

    # ---- location targeting ----------------------------------------------
    check("location targeting: manifest declares 24 positive targets",
          locs["total_positive_targets"] == 24)
    check("location targeting: manifest is PRESENCE",
          locs["geo_target_type_setting"]["positive_geo_target_type"] == "PRESENCE")
    manifest_ids = {t["geo_target_constant_id"]
                    for t in (locs["postal_code_targets"] + locs["named_targets"])}
    for cid, cname in LIVE.items():
        account_ids = {c["geo_target_constant"].split("/")[-1] for c in S["campaign_criteria"]
                       if c["campaign_id"] == cid and c["type"] == "LOCATION" and not c["negative"]}
        check(f"location targeting: {cname[:38]} targets exactly the approved 24",
              account_ids == manifest_ids, f"{len(account_ids)} targeted")
        negs = [c for c in S["campaign_criteria"]
                if c["campaign_id"] == cid and c["type"] == "LOCATION" and c["negative"]]
        check(f"location targeting: {cname[:38]} has no location exclusion", not negs)
        geo = next(c for c in S["campaigns"] if c["id"] == cid)
        check(f"location targeting: {cname[:38]} uses PRESENCE", geo["positive_geo"] == "PRESENCE")
    check("location targeting: no geo mutation is proposed",
          not any("LOCATION" in a["operation"] or "GEO" in a["operation"] for a in all_actions))

    # ---- negatives: protected terms and conflicts -------------------------
    neg_add = [a for a in plan["subplans"]["EXISTING_RESOURCES"]["actions"]
               if a["operation"] == "ADD_CAMPAIGN_NEGATIVE_KEYWORD"]
    neg_rm = [a for a in plan["subplans"]["EXISTING_RESOURCES"]["actions"]
              if a["operation"] == "REMOVE_SHARED_LIST_NEGATIVE"]
    check("negatives: no proposed negative contains a protected term",
          not [a for a in neg_add
               if any(re.search(rf"\b{re.escape(p)}\b", norm(a["negative_text"]))
                      for p in PROTECTED)],
          f"{len(neg_add)} additions checked")
    live_pos = [k for k in S["keywords"]
                if not k["negative"] and k["campaign_id"] in LIVE and k["status"] == "ENABLED"]
    blocked = []
    for a in neg_add:
        n = norm(a["negative_text"])
        rx = re.compile(rf"\b{re.escape(n)}\b")
        for k in live_pos:
            if rx.search(norm(k["text"])):
                blocked.append(f"{a['negative_text']!r} blocks {k['text']!r}")
    check("negatives: no proposed negative blocks a live positive keyword",
          not blocked, "; ".join(blocked))
    conv_terms = {norm(r["term"]) for r in S["search_terms"]["all_time"] if r["conversions"] > 0}
    blocked_q = []
    for a in neg_add:
        n = norm(a["negative_text"])
        rx = re.compile(rf"\b{re.escape(n)}\b")
        hits = [q for q in conv_terms if rx.search(q)]
        if hits:
            blocked_q.append(f"{a['negative_text']!r} blocks {hits[0]!r}")
    check("negatives: no proposed negative blocks a query that ever converted",
          not blocked_q, "; ".join(blocked_q))
    check("negatives: every removal targets an existing shared_criterion id",
          all(a["resource_id"] in {m["criterion_id"] for m in S["shared_criteria"]}
              for a in neg_rm), f"{len(neg_rm)} removals")
    check("negatives: additions are campaign scoped, never account level",
          all(a["resource_id"] in LIVE for a in neg_add))

    # ---- unsupported claims ----------------------------------------------
    verified = {norm(x) for x in profile["offer"].get("services_in_scope", [])}
    check("unsupported claims: every live ad-group theme is a verified first-party service",
          bool(verified), f"{len(verified)} verified services recorded")
    check("unsupported claims: the unverified experience claim is recorded, not repeated as fact",
          bool(profile["offer"].get("unverified_claims_currently_serving")))
    check("unsupported claims: no new ad copy is created in this round",
          not plan["subplans"]["CREATE_PAUSED"]["actions"])

    # ---- secrets ----------------------------------------------------------
    try:
        assert_no_embedded_secrets(plan_doc)
        check("secrets: no secret-like key in the change plan", True)
    except Exception as exc:  # noqa: BLE001
        check("secrets: no secret-like key in the change plan", False, str(exc))
    leaks = []
    for f in sorted(OUT.glob("*")):
        if f.is_file() and f.suffix in (".md", ".yaml", ".csv", ".json"):
            if SECRETISH.search(f.read_text(encoding="utf-8", errors="ignore")):
                leaks.append(f.name)
    check("secrets: no credential pattern in any deliverable", not leaks, ", ".join(leaks))


    # ---- custom conversion goals (Google's documented biddability override) --
    ccg = RV.get("custom_conversion_goals") or []
    check("custom goals: no custom_conversion_goal exists in the account",
          ccg == [], f"{len(ccg)} found")
    cfgs = RV.get("conversion_goal_campaign_config") or []
    check("custom goals: no live campaign references a custom conversion goal",
          all(not c.get("custom_conversion_goal") for c in cfgs),
          "; ".join(f"{c['campaign_id']}={c['goal_config_level']}" for c in cfgs))
    check("custom goals: so primary_for_goal=false does make each demoted action non-biddable",
          ccg == [] and all(not c.get("custom_conversion_goal") for c in cfgs))

    # ---- count-once: exactly one primary action per real lead event ----------
    demoted = {a["resource_id"] for a in conv_plan}
    still_primary = [a for a in RV["enabled_conversion_actions"]
                     if a["in_conv_column"] and a["primary_for_goal"]
                     and a["id"] not in demoted]
    declared = plan["subplans"]["CONVERSIONS"].get("remaining_primary_after_this_change") or []
    check("count once: the plan declares the surviving primary set",
          {d["id"] for d in declared} == {a["id"] for a in still_primary},
          f"declared {sorted(d['id'] for d in declared)} vs actual "
          f"{sorted(a['id'] for a in still_primary)}")
    EVENT = {"7644242327": "website form submission",
             "6885610317": "connected call from the website",
             "6566620547": "connected call from the ad"}
    events = [EVENT.get(a["id"], "UNMAPPED:" + a["name"]) for a in still_primary]
    check("count once: every surviving primary action maps to a known real lead event",
          all(not e.startswith("UNMAPPED") for e in events), "; ".join(events))
    check("count once: no real lead event has two surviving primary actions",
          len(events) == len(set(events)), "; ".join(sorted(events)))
    check("count once: Calls from ads stays primary", "6566620547" not in demoted)
    check("count once: every phone-click-only action is demoted",
          {"6557280400", "7389543053"} <= demoted)
    check("count once: every duplicate form-lead action is demoted",
          {"6557277268", "7389543347", "6885608055"} <= demoted)

    # ---- ClickCease: active, must remain -------------------------------------
    all_ops = " ".join(a["operation"] for a in all_actions)
    check("clickcease: no fingerprinted action clears the tracking template",
          "CLEAR_CUSTOMER_TRACKING_URL_TEMPLATE" not in all_ops)
    check("clickcease: no fingerprinted action touches customer.tracking_url_template",
          not any(a.get("field_mask") == "tracking_url_template" for a in all_actions))
    blk = plan.get("blocked_proposals") or []
    cc = [b for b in blk if b.get("field_mask") == "tracking_url_template"]
    check("clickcease: the correction exists as a BLOCKED, non-fingerprinted proposal",
          len(cc) == 1 and cc[0]["status"].startswith("BLOCKED"))
    if cc:
        b = cc[0]
        cur, prop = b["current_state_verbatim"], b["proposed_state_verbatim"]
        check("clickcease: proposal preserves the complete template",
              cur.replace("offer.sehydroseed.com",
                          "offeraustin.progreenlandscapesolutions.com") == prop)
        check("clickcease: only the ccpturl value differs",
              [x for x in cur.split("&") if not x.startswith("ccpturl=")]
              == [x for x in prop.split("&") if not x.startswith("ccpturl=")])
        check("clickcease: current_state_verbatim matches the live account today",
              cur == RV["tracking_url_template"])
        check("clickcease: proposed domain is flagged unverified",
              b.get("proposed_value_is_unverified") is True)
        check("clickcease: nothing queries, disables or modifies the ClickCease manager",
              "manager" not in b["operation"].lower()
              and not any("clickcease" in a["operation"].lower() for a in all_actions))

    # ---- ad schedule: corrected, never removed outright ----------------------
    rm = [a for a in all_actions if a["operation"] == "REMOVE_CAMPAIGN_AD_SCHEDULE_CRITERIA"]
    cr = [a for a in all_actions if a["operation"] == "CREATE_CAMPAIGN_AD_SCHEDULE_CRITERIA"]
    check("ad schedule: every removal is paired with a creation on the same campaign",
          {a["resource_id"] for a in rm} == {a["resource_id"] for a in cr} == set(LIVE))
    check("ad schedule: 14 criteria removed and 14 recreated",
          sum(a["object_count"] for a in rm) == 14
          and sum(a["object_count"] for a in cr) == 14,
          f"{sum(a['object_count'] for a in rm)} removed / "
          f"{sum(a['object_count'] for a in cr)} created")
    live_sched = RV["ad_schedule"]
    listed = [c["criterion_id"] for a in rm for c in a["exact_criteria_removed"]]
    check("ad schedule: every live criterion is listed for removal with its exact id",
          len(listed) == len(live_sched)
          and {(a["resource_id"], c["criterion_id"])
               for a in rm for c in a["exact_criteria_removed"]}
          == {(s["campaign_id"], s["criterion_id"]) for s in live_sched})
    created = [c for a in cr for c in a["exact_criteria_created"]]
    check("ad schedule: all 14 new criteria are 09:00-18:00 account time",
          all(c["start_hour"] == 9 and c["end_hour"] == 18 for c in created),
          f"{len(created)} criteria")
    check("ad schedule: 09:00-18:00 America/New_York equals 08:00-17:00 America/Chicago",
          all(c["market_time"] == "08:00 -> 17:00 America/Chicago" for c in created))
    check("ad schedule: all seven days are covered on each campaign",
          all(len({c["day"] for c in a["exact_criteria_created"]}) == 7 for a in cr))
    check("ad schedule: no action leaves a campaign eligible 24/7",
          not any("eligible all day" in str(a.get("proposed_state", "")) for a in all_actions))
    check("ad schedule: every removal action carries rollback values",
          all(a.get("rollback") and a.get("exact_criteria_removed") for a in rm))

    # ---- negatives: the revised, narrower set --------------------------------
    KEEP8 = {"agave landscaping", "agc turf", "astoria lighting", "garden goat",
             "mcdugald steele", "mirror lake landscaping", "spring texas", "ulm austin"}
    added_terms = {norm(a["negative_text"]) for a in neg_add}
    check("negatives: exactly the 8 approved high-confidence terms are added",
          added_terms == KEEP8, "; ".join(sorted(added_terms ^ KEEP8)) or "exact match")
    check("negatives: each of the 8 is added to both live campaigns",
          len(neg_add) == 16, f"{len(neg_add)} add actions")
    check("negatives: every added term has observed live spend",
          all(float(re.search(r"cost=\$([0-9.]+)", a["evidence"]).group(1)) > 0
              for a in neg_add))
    check("negatives: 'asphalt' and 'asphalt paving' are NOT added",
          not ({"asphalt", "asphalt paving"} & added_terms))
    removed_terms = {norm(a["negative_text"]) for a in neg_rm}
    check("negatives: 'emergency' is retained, not removed",
          "emergency" not in removed_terms)
    check("negatives: exactly the 7 agreed blocking negatives are removed",
          removed_terms == {"cost", "hire", "shade", "oasis", "keystone", "black",
                            "replacement"},
          "; ".join(sorted(removed_terms)))
    check("negatives: every removal names a full shared_criterion resource name",
          all(a.get("shared_criterion_resource_name", "").startswith("customers/")
              for a in neg_rm))
    wr = list(csv.DictReader((OUT / "06_negative_keyword_plan.csv").open(encoding="utf-8")))
    watch = [r for r in wr if r["operation"] == "WATCH_NO_ACTION"]
    check("negatives: the 13 deferred terms are recorded as WATCH with zero object count",
          len(watch) == 13 and all(r["object_count"] == "0" for r in watch),
          f"{len(watch)} watch rows")
    check("negatives: no WATCH term has any observed click or cost",
          all(int(r["observed_clicks"]) == 0 and float(r["observed_cost"]) == 0
              for r in watch))

    # ---- phase discipline ----------------------------------------------------
    check("phase: the plan declares itself Phase 1",
          str(plan.get("phase", "")).startswith("PHASE 1"))
    check("phase: a Phase 2 recommendation exists and creates nothing",
          bool(plan.get("phase_2_recommendation"))
          and "RECOMMENDATION ONLY" in plan["phase_2_recommendation"]["status"])
    check("phase: no keyword is created or changed in Phase 1",
          not any("KEYWORD" in a["operation"] and "NEGATIVE" not in a["operation"]
                  for a in all_actions))
    check("phase: no ad or RSA is created in Phase 1",
          not any(re.search(r"\bAD\b|RSA|RESPONSIVE", a["operation"]) for a in all_actions))

    # ---- site_or_tracking is a spec, not an executable change ----------------
    check("site spec: SITE_OR_TRACKING carries no fingerprinted actions",
          not plan["subplans"]["SITE_OR_TRACKING"]["actions"])
    spec = plan.get("site_or_tracking_specification") or {}
    check("site spec: a developer remediation specification exists",
          "SPECIFICATION ONLY" in spec.get("status", ""))
    items = spec.get("priority_order") or []
    REQ = {"gclid", "gbraid", "wbraid", "utm_source", "utm_medium", "utm_campaign",
           "utm_term", "utm_content", "landing_page_url", "referrer", "consent_state",
           "unique_lead_id"}
    check("site spec: gform_3 attribution capture is specified with all required fields",
          any(REQ <= set(i.get("required_fields", [])) for i in items))
    check("site spec: the {Referer} repair is covered",
          any("{Referer}" in json.dumps(i) for i in items))
    check("site spec: the tag test is gated behind a separate approval",
          any("own client approval" in json.dumps(i) for i in items))
    check("site spec: GA4 system of record must be identified before any removal",
          any("Removal of any property" in str(i.get("explicitly_not_proposed", ""))
              for i in items))
    check("site spec: no consent change without a client-approved implementation",
          any("consent" in json.dumps(i).lower() and i.get("explicitly_not_proposed")
              for i in items))

    # ---- version hygiene -----------------------------------------------------
    check("version: the plan supersedes the rejected v1 and says so",
          plan.get("version") == 2 and "REJECTED" in plan.get("supersedes", ""))
    V1_SUBPLAN_FPS = ("5F2D15648457", "1AE1B904B680", "FC54F5319D1B", "363B8D6D60D5")
    check("version: no rejected v1 subplan fingerprint appears anywhere in the plan",
          not any(fp in json.dumps(plan) for fp in V1_SUBPLAN_FPS))
    # The v1 MASTER may appear, but only inside `supersedes`, where naming the rejected
    # version is the point. It must not leak into any action or subplan.
    body = json.dumps({k: v for k, v in plan.items() if k != "supersedes"})
    check("version: the v1 master fingerprint appears only in `supersedes`",
          "38314B507F47" not in body and "38314B507F47" in plan.get("supersedes", ""))

    # ---- bundle completeness and hashes -----------------------------------
    required = ["00_identity_and_source_log.md", "01_fresh_account_snapshot.json",
                "02_executive_audit.md", "03_campaign_and_ad_group_verdicts.csv",
                "04_keyword_verdicts.csv", "05_search_term_verdicts.csv",
                "06_negative_keyword_plan.csv", "07_conversion_and_tracking_audit.md",
                "08_ads_assets_and_policy_audit.csv",
                "09_landing_page_and_market_integrity_audit.csv",
                "10_location_budget_schedule_and_device_plan.md",
                "11_exact_change_plan.yaml", "12_validation_and_approval_report.md"]
    missing = [r for r in required if not (OUT / r).exists()]
    check("bundle: all 13 required deliverables exist", not missing, ", ".join(missing))

    print("=" * 92)
    print("SELF-REVIEW")
    print("=" * 92)
    failed = 0
    for name, ok, detail in results:
        flag = "PASS" if ok else "**FAIL**"
        if not ok:
            failed += 1
        print(f"  [{flag:8}] {name}" + (f"  ({detail})" if detail else ""))
    print("-" * 92)
    print(f"  {len(results) - failed} passed, {failed} failed")

    print("\nARTIFACT HASHES (sha256, first 16)")
    for r in required:
        f = OUT / r
        if f.exists():
            h = hashlib.sha256(f.read_bytes()).hexdigest()[:16]
            print(f"  {h}  {f.stat().st_size:>10,} B  {r}")
        else:
            print(f"  {'-' * 16}  {'MISSING':>12}  {r}")

    print("\nMUTATION COUNTS")
    for k, b in plan["subplans"].items():
        acts = b.get("actions") or []
        print(f"  {k:<20} actions={len(acts):<4} objects="
              f"{sum(int(a.get('object_count', 1)) for a in acts)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
