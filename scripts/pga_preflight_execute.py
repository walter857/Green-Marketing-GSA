#!/usr/bin/env python3
"""Execution preflight for the frozen Pro Green Austin campaign-negative plan.

Checks the approved plan against a FRESH read-only snapshot taken immediately before the
live mutation. Target-state drift stops the run. Read-only; writes nothing external.

Exit code 0 only when every check passes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402

from gm_gsa.safety import approval_code  # noqa: E402

SUBPLANS = ["STATUS", "BUDGET", "EXISTING_RESOURCES", "CONVERSIONS",
            "CREATE_PAUSED", "SITE_OR_TRACKING", "ENABLE"]
CAMPAIGNS = {"24053505504": "Progreen Austin | Search | Outdoor Living & Design",
             "24053505501": "Progreen Austin | Search | Hardscape Construction"}
EXPECTED_BASELINE = 44
PHASE1 = ["agc turf", "ulm austin", "garden goat", "agave landscaping", "astoria lighting"]
PROTECTED = ["near me", "quote", "quotes", "price", "prices", "pricing", "cost", "costs",
             "best", "hire", "local", "emergency"]
CLIENT_BRAND = ["progreen", "pro green"]
VERIFIED_SERVICES = [
    "hardscaping", "patios", "pavers", "paver driveways", "walkways", "retaining walls",
    "outdoor living spaces", "fire pits", "pergolas", "landscape design",
    "landscape lighting", "artificial turf", "outdoor kitchens", "concrete", "masonry",
    "deck construction", "landscaping", "driveways", "sod installation", "irrigation",
]


def norm(t):
    t = (t or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s&'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def toks(t):
    return norm(t).split()


def contiguous(sub, seq):
    if not sub or len(sub) > len(seq):
        return False
    return any(seq[i:i + len(sub)] == sub for i in range(len(seq) - len(sub) + 1))


def blocks(neg, mt, query):
    n, q = toks(neg), toks(query)
    if not n:
        return False
    if mt == "EXACT":
        return n == q
    if mt == "BROAD":
        return set(n).issubset(set(q))
    return contiguous(n, q)


def makes_redundant(text, mt, proposed):
    e, p = toks(text), toks(proposed)
    if not e:
        return False
    if mt == "PHRASE":
        return contiguous(e, p)
    if mt == "BROAD":
        return set(e).issubset(set(p))
    return e == p


class Checks:
    def __init__(self):
        self.rows = []

    def add(self, name, ok, detail=""):
        self.rows.append((name, bool(ok), detail))
        return ok

    def report(self):
        w = max(len(n) for n, _, _ in self.rows)
        failed = sum(1 for _, ok, _ in self.rows if not ok)
        for name, ok, detail in self.rows:
            print(f"  [{'PASS' if ok else 'FAIL'}] {name:<{w}}  {detail}")
        print(f"\n  {len(self.rows) - failed}/{len(self.rows)} checks passed")
        return failed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--snapshot", required=True, help="FRESH pre-execution snapshot")
    ap.add_argument("--approved-list", required=True)
    ap.add_argument("--expect-master", required=True)
    ap.add_argument("--expect-subplan", required=True)
    args = ap.parse_args()

    plan = yaml.safe_load(Path(args.plan).read_text(encoding="utf-8"))["change_plan"]
    actions = plan["subplans"]["EXISTING_RESOURCES"]["actions"]
    D = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    approved = {}
    for line in Path(args.approved_list).read_text(encoding="utf-8").splitlines():
        if line.strip():
            fam, ph = line.split("|", 1)
            approved[ph.strip()] = fam.strip()

    c = Checks()
    ident = D["identity"]

    # ---------------- identity ----------------
    c.add("identity.account_name_exact",
          ident["descriptive_name"] == "Pro Green - Austin - Live",
          ident["descriptive_name"])
    c.add("identity.customer_id_exact", ident["id"] == "7380491929", ident["id"])
    c.add("identity.manager_false", ident["manager"] is False, str(ident["manager"]))
    c.add("identity.test_account_false", ident["test_account"] is False,
          str(ident["test_account"]))
    c.add("identity.service_exact", plan["target"]["exact_service"] == "outdoor design & build",
          plan["target"]["exact_service"])
    c.add("identity.currency_usd", ident["currency_code"] == "USD", ident["currency_code"])
    c.add("identity.timezone", ident["time_zone"] == "America/New_York", ident["time_zone"])
    c.add("snapshot.zero_read_errors", not D["read_errors"], f"{len(D['read_errors'])}")

    enabled = {x["id"] for x in D["campaigns"] if x["status"] == "ENABLED"}
    c.add("campaigns.exactly_the_two_in_scope_enabled", enabled == set(CAMPAIGNS),
          str(sorted(enabled)))

    # ---------------- fingerprints ----------------
    master = approval_code({"target": plan["target"],
                            "subplans": {n: plan["subplans"].get(n) for n in SUBPLANS}})
    sub = approval_code({"target": plan["target"], "subplan": "EXISTING_RESOURCES",
                         "actions": actions})
    c.add("fingerprint.master_reproduces", master == args.expect_master.upper(), master)
    c.add("fingerprint.subplan_reproduces", sub == args.expect_subplan.upper(), sub)
    c.add("fingerprint.neither_is_void",
          not ({master, sub} & {"2D87A5249784", "4EEF81C7F2F5"}))

    # ---------------- plan shape vs the approval text ----------------
    phrases = {a["negative_text"] for a in actions}
    c.add("plan.action_count_68", len(actions) == 68, str(len(actions)))
    c.add("plan.object_count_68", sum(int(a["object_count"]) for a in actions) == 68,
          str(sum(int(a["object_count"]) for a in actions)))
    c.add("plan.unique_phrases_34", len(phrases) == 34, str(len(phrases)))
    c.add("plan.matches_approved_list_exactly", phrases == set(approved),
          f"missing={sorted(set(approved) - phrases)} extra={sorted(phrases - set(approved))}")
    c.add("plan.families_match_approval",
          all(a["family"] == approved[a["negative_text"]] for a in actions))
    per = Counter(a["resource_id"] for a in actions)
    c.add("plan.34_targets_per_campaign",
          per == Counter({"24053505501": 34, "24053505504": 34}), str(dict(per)))
    c.add("plan.every_target_is_phrase", {a["match_type"] for a in actions} == {"PHRASE"},
          str(sorted({a["match_type"] for a in actions})))
    c.add("plan.only_campaign_negative_operation",
          {a["operation"] for a in actions} == {"ADD_CAMPAIGN_NEGATIVE_KEYWORD"},
          str(sorted({a["operation"] for a in actions})))
    c.add("plan.only_the_two_approved_campaigns",
          {a["resource_id"] for a in actions} == set(CAMPAIGNS))
    c.add("plan.no_other_subplan_has_actions",
          all(not (plan["subplans"].get(n) or {}).get("actions")
              for n in SUBPLANS if n != "EXISTING_RESOURCES"))
    # Structural, not textual: an operation is defined by the `operation` value and the
    # field names present, never by a word appearing inside human-readable evidence prose.
    ALLOWED_FIELDS = {
        "action_id", "priority", "operation", "resource_type", "resource_id",
        "resource_name", "campaign_resource_name", "negative_text", "match_type", "family",
        "current_state", "proposed_state", "field_mask", "supporting_raw_search_terms",
        "august_impressions", "august_clicks", "august_cost", "august_conversions",
        "first_party_service_verification", "competitor_verification", "evidence",
        "positive_keyword_conflict_result", "converted_query_conflict_result",
        "existing_negative_check", "protected_term_result", "expected_effect", "risk",
        "rollback", "object_count",
    }
    stray = sorted({k for a in actions for k in a} - ALLOWED_FIELDS)
    c.add("plan.no_field_outside_the_negative_creation_schema", not stray, str(stray))
    c.add("plan.every_action_declares_the_negative_operation",
          all(a["operation"] == "ADD_CAMPAIGN_NEGATIVE_KEYWORD" for a in actions))
    c.add("plan.no_field_mask_touches_an_existing_resource",
          all(a["field_mask"] == "n/a (criterion creation)" for a in actions),
          str(sorted({a["field_mask"] for a in actions})))
    c.add("plan.every_action_is_a_creation_not_a_removal",
          all(a["current_state"].startswith("not present") for a in actions))
    c.add("plan.every_object_has_rollback",
          all("criterion_id" in a.get("rollback", "") for a in actions))

    # ---------------- live effective-negative inventory ----------------
    acct_sets = {s["id"] for s in D["shared_sets"]
                 if s["type"] == "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS"}
    linked = defaultdict(set)
    for l in D["campaign_shared_sets"]:
        if l["campaign_id"] in CAMPAIGNS and l["link_status"] == "ENABLED":
            linked[l["campaign_id"]].add(l["shared_set_id"])
    members = defaultdict(list)
    for m in D["shared_criteria"]:
        members[m["shared_set_id"]].append((m["keyword_text"], m["match_type"]))
    camp_neg = defaultdict(list)
    for x in D["campaign_negative_keywords"]:
        if x["campaign_id"] in CAMPAIGNS:
            camp_neg[x["campaign_id"]].append((x["text"], x["match_type"]))
    ag_campaign = {a["id"]: a["campaign_id"] for a in D["ad_groups"]}
    ag_count = Counter(ag_campaign.values())
    ag_hits = defaultdict(Counter)
    for k in D["ad_group_keywords"]:
        if k["negative"] and k["campaign_id"] in CAMPAIGNS:
            ag_hits[k["campaign_id"]][(norm(k["text"]), k["match_type"])] += 1

    def eff(cid):
        out = []
        for s in acct_sets:
            out += [(t, m, "ACCOUNT_LEVEL") for t, m in members[s]]
        for s in linked[cid]:
            out += [(t, m, "SHARED_LIST") for t, m in members[s]]
        out += [(t, m, "CAMPAIGN") for t, m in camp_neg[cid]]
        out += [(t, m, "AD_GROUP_ALL") for (t, m), n in ag_hits[cid].items()
                if n == ag_count[cid]]
        return out

    baseline = {cid: len(camp_neg[cid]) for cid in CAMPAIGNS}
    c.add("live.campaign_negative_baseline_is_44_each",
          all(v == EXPECTED_BASELINE for v in baseline.values()), str(baseline))

    present = [(a["negative_text"], a["resource_id"]) for a in actions
               if (norm(a["negative_text"]), "PHRASE")
               in {(norm(t), m) for t, m in camp_neg[a["resource_id"]]}]
    c.add("live.no_proposed_phrase_already_a_campaign_negative", not present,
          str(present[:3]))
    redundant = [(a["negative_text"], a["resource_id"], t, m)
                 for a in actions for t, m, _ in eff(a["resource_id"])
                 if makes_redundant(t, m, a["negative_text"])]
    c.add("live.no_proposed_phrase_already_effectively_blocked", not redundant,
          str(redundant[:3]))
    c.add("live.all_68_operations_absent_from_the_account",
          len(present) == 0 and len(redundant) == 0, "0 of 68 present")

    # ---------------- structural baselines ----------------
    pos = [k for k in D["ad_group_keywords"] if not k["negative"]
           and k["campaign_id"] in CAMPAIGNS and k["status"] == "ENABLED"]
    agneg = [k for k in D["ad_group_keywords"] if k["negative"]
             and k["campaign_id"] in CAMPAIGNS]
    ads = [a for a in D["ad_final_urls"] if a["campaign_id"] in CAMPAIGNS
           and a["status"] == "ENABLED"]
    c.add("live.48_enabled_positive_keywords", len(pos) == 48, str(len(pos)))
    c.add("live.246_ad_group_negatives", len(agneg) == 246, str(len(agneg)))
    c.add("live.48_enabled_ads", len(ads) == 48, str(len(ads)))
    c.add("live.24_enabled_ad_groups",
          len([a for a in D["ad_groups"] if a["status"] == "ENABLED"]) == 24)
    c.add("live.8689_shared_criteria", len(D["shared_criteria"]) == 8689,
          str(len(D["shared_criteria"])))
    c.add("live.no_removed_rows_in_inventory",
          all(k["status"] != "REMOVED" for k in D["ad_group_keywords"]
              if k["campaign_id"] in CAMPAIGNS)
          and all(x["status"] != "REMOVED" for x in D["campaign_negative_keywords"]
                  if x["campaign_id"] in CAMPAIGNS))

    # ---------------- conflict checks against CURRENT data ----------------
    kwc = [(a["negative_text"], k["text"]) for a in actions for k in pos
           if k["campaign_id"] == a["resource_id"]
           and blocks(a["negative_text"], "PHRASE", k["text"])]
    c.add("conflict.no_enabled_positive_keyword_blocked", not kwc, str(kwc[:3]))

    converting = {norm(r["term"]) for r in D["search_terms_all_time_converting"]}
    cq = [(p, q) for p in phrases for q in converting if blocks(p, "PHRASE", q)]
    c.add("conflict.no_historical_converting_query_blocked", not cq, str(cq[:3]))
    c.add("conflict.no_primary_conversion_family_blocked", not cq,
          f"{len(converting)} converting queries checked")

    allconv = {norm(r["term"]) for r in D["search_terms_all_time_all_conv"]}
    ac = [(p, q) for p in phrases for q in allconv if blocks(p, "PHRASE", q)]
    c.add("conflict.no_all_conversions_query_blocked", not ac, str(ac[:3]))

    pr = [(p, t) for p in phrases for t in PROTECTED if contiguous(toks(p), toks(t))]
    c.add("conflict.no_protected_buyer_intent_term_proposed", not pr, str(pr[:3]))

    cb = [p for p in phrases if any(b in norm(p) for b in CLIENT_BRAND)]
    c.add("conflict.no_client_brand_term_proposed", not cb, str(cb))

    vs = [(p, s) for p in phrases for s in VERIFIED_SERVICES
          if blocks(p, "PHRASE", s) or norm(p) == norm(s)]
    c.add("conflict.no_verified_austin_service_blocked", not vs, str(vs[:3]))

    # generic landscaping: nothing in the plan may block a bare landscaping query
    generic = ["landscaper near me", "landscapers near me", "landscape companies near me",
               "landscaping companies near me", "landscaping services near me",
               "landscaping near me", "landscape near me", "landscaping company near me"]
    g = [(p, q) for p in phrases for q in generic if blocks(p, "PHRASE", q)]
    c.add("conflict.generic_landscaping_family_excluded", not g, str(g[:3]))

    # collateral against the CURRENT corpus, including any newly released day
    supporting = {norm(t) for a in actions for t in a["supporting_raw_search_terms"]}
    corpus = {norm(r["term"]) for r in D["search_terms_window"]
              if r["campaign_id"] in CAMPAIGNS}
    collateral = sorted({q for p in phrases for q in corpus
                         if blocks(p, "PHRASE", q) and q not in supporting})
    c.add("conflict.no_new_corpus_term_caught_as_collateral", not collateral,
          str(collateral[:5]) if collateral else f"{len(corpus)} live terms checked")

    # ---------------- Phase 1 ----------------
    p1 = {p: [cid for cid in CAMPAIGNS
              if any(makes_redundant(t, m, p) for t, m, _ in eff(cid))] for p in PHASE1}
    c.add("phase1.all_five_still_effective_on_both_campaigns",
          all(len(v) == 2 for v in p1.values()),
          str({k: len(v) for k, v in p1.items()}))
    c.add("phase1.none_duplicated_by_this_plan",
          not (phrases & {norm(p) for p in PHASE1}),
          str(sorted(phrases & {norm(p) for p in PHASE1})))

    print(f"PLAN       {args.plan}")
    print(f"SNAPSHOT   {args.snapshot}  read {D['read_started_utc']}")
    print(f"MASTER     {master}")
    print(f"SUBPLAN    {sub}   actions={len(actions)} objects="
          f"{sum(int(a['object_count']) for a in actions)}\n")
    failed = c.report()
    if failed:
        print(f"\nPREFLIGHT FAILED: {failed} check(s). DO NOT WRITE.")
        return 1
    print("\nPREFLIGHT PASSED. No target-state drift. Safe to execute the frozen plan.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
