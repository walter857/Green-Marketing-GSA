#!/usr/bin/env python3
"""Permanent validator for a Green Marketing campaign-negative package.

Checks the plan against its own reconciliation report, the verdict CSV, the plan CSV and
the fresh read-only snapshot it was built from. Read-only; touches nothing external.

Exit code 0 only when every check passes.
"""
from __future__ import annotations

import argparse
import csv
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

VOID_FINGERPRINTS = {"2D87A5249784", "4EEF81C7F2F5"}

PROTECTED_TERMS = ["near me", "quote", "quotes", "price", "prices", "pricing", "cost",
                   "costs", "best", "hire", "local", "emergency"]

PHASE1_NEGATIVES = ["agc turf", "ulm austin", "garden goat", "agave landscaping",
                    "astoria lighting", "mcdugald steele", "mirror lake landscaping",
                    "spring texas"]

ALLOWED_CAMPAIGNS = {"24053505504", "24053505501"}
ALLOWED_OPERATIONS = {"ADD_CAMPAIGN_NEGATIVE_KEYWORD"}


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


def makes_redundant(existing_text, existing_mt, proposed):
    e, p = toks(existing_text), toks(proposed)
    if not e:
        return False
    if existing_mt == "PHRASE":
        return contiguous(e, p)
    if existing_mt == "BROAD":
        return set(e).issubset(set(p))
    return e == p


class Checks:
    def __init__(self):
        self.rows = []

    def add(self, name, ok, detail=""):
        self.rows.append((name, bool(ok), detail))
        return ok

    def report(self):
        width = max(len(n) for n, _, _ in self.rows)
        failed = 0
        for name, ok, detail in self.rows:
            flag = "PASS" if ok else "FAIL"
            if not ok:
                failed += 1
            print(f"  [{flag}] {name:<{width}}  {detail}")
        print(f"\n  {len(self.rows) - failed}/{len(self.rows)} checks passed")
        return failed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--verdict-csv", required=True)
    ap.add_argument("--plan-csv", required=True)
    ap.add_argument("--reconciliation", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--expect-master")
    ap.add_argument("--expect-subplan")
    args = ap.parse_args()

    doc = yaml.safe_load(Path(args.plan).read_text(encoding="utf-8"))
    plan = doc["change_plan"]
    actions = plan["subplans"]["EXISTING_RESOURCES"]["actions"]
    rec = json.loads(Path(args.reconciliation).read_text(encoding="utf-8"))
    D = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    with open(args.verdict_csv, encoding="utf-8") as fh:
        vrows = list(csv.DictReader(fh))
    with open(args.plan_csv, encoding="utf-8") as fh:
        prows = list(csv.DictReader(fh))

    c = Checks()

    # ---------------- identity ----------------
    t = plan["target"]
    ident = D["identity"]
    c.add("identity.account_name", t["exact_child_account_name"] == "Pro Green - Austin - Live"
          == ident["descriptive_name"], ident["descriptive_name"])
    c.add("identity.customer_id", t["child_customer_id"] == "7380491929" == ident["id"],
          ident["id"])
    c.add("identity.not_manager", ident["manager"] is False, f"manager={ident['manager']}")
    c.add("identity.not_test_account", ident["test_account"] is False,
          f"test={ident['test_account']}")
    c.add("identity.currency_usd", ident["currency_code"] == "USD", ident["currency_code"])
    c.add("identity.service", t["exact_service"] == "outdoor design & build",
          t["exact_service"])
    c.add("identity.vertical_in_scope",
          t["vertical"] in {"landscaping", "hardscaping", "heating-cooling",
                            "similar-local-service"}, t["vertical"])
    c.add("snapshot.no_read_errors", len(D["read_errors"]) == 0,
          f"{len(D['read_errors'])} read errors")

    live = {x["id"]: x for x in D["campaigns"] if x["status"] == "ENABLED"}
    c.add("campaigns.both_enabled", set(live) == ALLOWED_CAMPAIGNS,
          f"enabled={sorted(live)}")

    # GAQL returns REMOVED rows unless filtered. A REMOVED negative counted as live would
    # wrongly mark a proposal redundant, so the inventory must contain no REMOVED row.
    inscope_kw = [k for k in D["ad_group_keywords"] if k["campaign_id"] in ALLOWED_CAMPAIGNS]
    inscope_cn = [x for x in D["campaign_negative_keywords"]
                  if x["campaign_id"] in ALLOWED_CAMPAIGNS]
    inscope_ag = [a for a in D["ad_groups"] if a["campaign_id"] in ALLOWED_CAMPAIGNS]
    c.add("inventory.no_removed_ad_group_criteria",
          all(k["status"] != "REMOVED" for k in inscope_kw),
          str(dict(Counter(k["status"] for k in inscope_kw))))
    c.add("inventory.no_removed_campaign_negatives",
          all(x["status"] != "REMOVED" for x in inscope_cn),
          str(dict(Counter(x["status"] for x in inscope_cn))))
    c.add("inventory.no_removed_ad_groups",
          all(a["status"] != "REMOVED" for a in inscope_ag),
          str(dict(Counter(a["status"] for a in inscope_ag))))
    used_sets = ({s["id"] for s in D["shared_sets"]
                  if s["type"] == "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS"}
                 | {l["shared_set_id"] for l in D["campaign_shared_sets"]
                    if l["campaign_id"] in ALLOWED_CAMPAIGNS
                    and l["link_status"] == "ENABLED"})
    c.add("inventory.every_consulted_shared_set_is_enabled",
          all(s["status"] == "ENABLED" for s in D["shared_sets"] if s["id"] in used_sets),
          f"{len(used_sets)} sets consulted")

    # ---------------- source vs verdict reconciliation ----------------
    src = rec["source"]
    src_rows = [r for r in D["search_terms_window"] if r["campaign_id"] in ALLOWED_CAMPAIGNS]
    c.add("recon.source_row_total_equals_verdict_row_total",
          len(src_rows) == len(vrows) == src["rows"],
          f"snapshot={len(src_rows)} csv={len(vrows)}")
    c.add("recon.source_distinct_terms_equals_verdict_distinct_terms",
          len({norm(r['term']) for r in src_rows})
          == len({r['normalized_search_term'] for r in vrows}),
          f"{len({norm(r['term']) for r in src_rows})}")
    c.add("recon.verdict_cost_equals_source_visible_cost",
          round(sum(r["cost"] for r in src_rows), 2)
          == round(sum(float(r["cost"]) for r in vrows), 2),
          f"${round(sum(float(r['cost']) for r in vrows), 2)}")
    c.add("recon.verdict_clicks_equal_source_visible_clicks",
          sum(r["clicks"] for r in src_rows) == sum(int(r["clicks"]) for r in vrows),
          str(sum(int(r["clicks"]) for r in vrows)))
    c.add("recon.verdict_conversions_equal_source_visible_conversions",
          round(sum(r["conversions"] for r in src_rows), 4)
          == round(sum(float(r["conversions"]) for r in vrows), 4),
          str(round(sum(float(r["conversions"]) for r in vrows), 2)))
    c.add("recon.every_row_has_a_verdict", all(r["verdict"] for r in vrows))
    c.add("recon.no_row_silently_dropped",
          Counter((r["term"], r["campaign_id"], r["ad_group_id"], r["matched_keyword"])
                  for r in src_rows)
          == Counter((r["raw_search_term"], r["campaign_id"], r["ad_group_id"],
                      r["matching_keyword_text"]) for r in vrows))
    c.add("recon.zero_impression_rows_retained",
          sum(1 for r in src_rows if r["impressions"] == 0)
          == sum(1 for r in vrows if int(r["impressions"]) == 0),
          f"{sum(1 for r in vrows if int(r['impressions']) == 0)} zero-impression rows")
    c.add("recon.raw_term_preserved_alongside_normalized",
          all(r["raw_search_term"] and r["normalized_search_term"] for r in vrows))

    # ---------------- object counts ----------------
    objects = sum(int(a["object_count"]) for a in actions)
    c.add("counts.yaml_object_count_equals_csv_object_count",
          objects == sum(int(r["object_count"]) for r in prows) == len(prows),
          f"yaml={objects} csv={len(prows)}")
    c.add("counts.plan_actions_equal_objects", len(actions) == objects,
          f"actions={len(actions)} objects={objects}")
    phrases = {a["negative_text"] for a in actions}
    c.add("counts.unique_phrases_times_campaigns_minus_skips",
          len(phrases) * len(ALLOWED_CAMPAIGNS)
          - len(rec["targets_skipped"]) == len(actions),
          f"{len(phrases)} x 2 - {len(rec['targets_skipped'])} = {len(actions)}")
    c.add("counts.every_phrase_on_both_campaigns_unless_skipped",
          all(len({a["resource_id"] for a in actions if a["negative_text"] == p})
              == 2 for p in phrases))
    c.add("counts.reconciliation_agrees",
          rec["plan_actions"] == len(actions) and rec["plan_objects"] == objects
          and rec["csv_rows"] == len(prows))

    # ---------------- scope ----------------
    c.add("scope.only_the_two_approved_campaigns",
          {a["resource_id"] for a in actions} == ALLOWED_CAMPAIGNS,
          str(sorted({a["resource_id"] for a in actions})))
    c.add("scope.only_campaign_negative_operations",
          {a["operation"] for a in actions} == ALLOWED_OPERATIONS,
          str(sorted({a["operation"] for a in actions})))
    c.add("scope.no_account_shared_or_ad_group_mutation",
          not any(k in json.dumps(a) for a in actions
                  for k in ("shared_criterion_operation", "customer_negative",
                            "ad_group_criterion_operation", "ADD_AD_GROUP_NEGATIVE_KEYWORD",
                            "REMOVE_SHARED_LIST_NEGATIVE")))
    c.add("scope.other_subplans_empty",
          all(not (plan["subplans"].get(n) or {}).get("actions")
              for n in SUBPLANS if n != "EXISTING_RESOURCES"))
    c.add("scope.all_match_types_are_phrase",
          {a["match_type"] for a in actions} == {"PHRASE"},
          str(sorted({a["match_type"] for a in actions})))
    c.add("scope.every_object_has_a_rollback",
          all(a.get("rollback") and "criterion_id" in a["rollback"] for a in actions))
    c.add("scope.every_object_names_its_campaign_resource",
          all(a["campaign_resource_name"] == f"customers/7380491929/campaigns/{a['resource_id']}"
              for a in actions))
    c.add("scope.mode_is_draft", plan["mode"] == "draft", plan["mode"])
    c.add("scope.no_external_write_recorded",
          plan["external_writes_performed"] == "NONE")

    # ---------------- effective-negative duplication ----------------
    acct_sets = {s["id"] for s in D["shared_sets"]
                 if s["type"] == "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS"}
    linked = defaultdict(set)
    for l in D["campaign_shared_sets"]:
        if l["campaign_id"] in ALLOWED_CAMPAIGNS and l["link_status"] == "ENABLED":
            linked[l["campaign_id"]].add(l["shared_set_id"])
    members = defaultdict(list)
    for m in D["shared_criteria"]:
        members[m["shared_set_id"]].append((m["keyword_text"], m["match_type"]))
    camp_neg = defaultdict(list)
    for x in D["campaign_negative_keywords"]:
        if x["campaign_id"] in ALLOWED_CAMPAIGNS:
            camp_neg[x["campaign_id"]].append((x["text"], x["match_type"]))
    ag_campaign = {a["id"]: a["campaign_id"] for a in D["ad_groups"]}
    ag_count = Counter(ag_campaign.values())
    ag_hits = defaultdict(Counter)
    for k in D["ad_group_keywords"]:
        if k["negative"] and k["campaign_id"] in ALLOWED_CAMPAIGNS:
            ag_hits[k["campaign_id"]][(norm(k["text"]), k["match_type"])] += 1

    def eff(cid):
        out = []
        for s in acct_sets:
            out += members[s]
        for s in linked[cid]:
            out += members[s]
        out += camp_neg[cid]
        out += [(t_, m) for (t_, m), n in ag_hits[cid].items() if n == ag_count[cid]]
        return out

    dups = [(a["negative_text"], a["resource_id"], t_, m)
            for a in actions
            for t_, m in eff(a["resource_id"])
            if makes_redundant(t_, m, a["negative_text"])]
    c.add("negatives.no_proposal_is_already_effectively_blocked", not dups, str(dups[:3]))
    c.add("negatives.no_phase_1_negative_is_duplicated",
          not (phrases & {norm(p) for p in PHASE1_NEGATIVES}),
          str(sorted(phrases & {norm(p) for p in PHASE1_NEGATIVES})))
    c.add("negatives.phase_1_still_effective_on_both_campaigns",
          all(any(makes_redundant(t_, m, p) for t_, m in eff(cid))
              for p in PHASE1_NEGATIVES for cid in ALLOWED_CAMPAIGNS))
    c.add("negatives.no_duplicate_phrase_within_a_campaign",
          all(n == 1 for n in Counter((a["negative_text"], a["resource_id"])
                                      for a in actions).values()))

    # ---------------- conflicts ----------------
    pos = [k for k in D["ad_group_keywords"]
           if not k["negative"] and k["campaign_id"] in ALLOWED_CAMPAIGNS
           and k["status"] == "ENABLED"]
    kw_conf = [(a["negative_text"], k["text"]) for a in actions for k in pos
               if k["campaign_id"] == a["resource_id"]
               and blocks(a["negative_text"], "PHRASE", k["text"])]
    c.add("conflicts.no_positive_keyword_blocked", not kw_conf, str(kw_conf[:3]))

    converting = {norm(r["term"]) for r in D["search_terms_all_time_converting"]}
    conv_conf = [(p, q) for p in phrases for q in converting if blocks(p, "PHRASE", q)]
    c.add("conflicts.no_converted_query_family_blocked", not conv_conf, str(conv_conf[:3]))

    allconv = {norm(r["term"]) for r in D["search_terms_all_time_all_conv"]}
    ac_conf = [(p, q) for p in phrases for q in allconv if blocks(p, "PHRASE", q)]
    c.add("conflicts.no_all_conversions_query_blocked", not ac_conf, str(ac_conf[:3]))

    prot = [(p, t_) for p in phrases for t_ in PROTECTED_TERMS
            if contiguous(toks(p), toks(t_))]
    c.add("conflicts.no_protected_buyer_intent_term_proposed", not prot, str(prot[:3]))

    kept = {r["normalized_search_term"] for r in vrows
            if r["verdict"] in ("KEEP", "WATCH", "INSUFFICIENT_DATA")}
    kept_conf = [(p, q) for p in phrases for q in kept if blocks(p, "PHRASE", q)]
    c.add("conflicts.no_retained_query_blocked", not kept_conf, str(kept_conf[:3]))

    generic = {r["normalized_search_term"] for r in vrows
               if r["intent_family"] == "GENERIC_LANDSCAPING"}
    gen_conf = [(p, q) for p in phrases for q in generic if blocks(p, "PHRASE", q)]
    c.add("conflicts.no_generic_landscaping_family_proposed", not gen_conf, str(gen_conf[:3]))
    c.add("conflicts.generic_landscaping_family_present_and_retained",
          bool(generic) and all(
              r["verdict"] in ("KEEP", "WATCH") for r in vrows
              if r["intent_family"] == "GENERIC_LANDSCAPING"),
          f"{len(generic)} generic-landscaping terms retained")
    brand = [r for r in vrows if r["intent_family"] == "CLIENT_BRAND"]
    c.add("conflicts.client_brand_never_blocked",
          all(r["verdict"] == "KEEP" for r in brand), f"{len(brand)} client-brand rows")

    # ---------------- fingerprints ----------------
    master = approval_code({"target": plan["target"],
                            "subplans": {n: plan["subplans"].get(n) for n in SUBPLANS}})
    sub = approval_code({"target": plan["target"], "subplan": "EXISTING_RESOURCES",
                         "actions": actions})
    master2 = approval_code({"target": plan["target"],
                             "subplans": {n: plan["subplans"].get(n) for n in SUBPLANS}})
    c.add("fingerprint.reproducible", master == master2, master)
    c.add("fingerprint.master_not_void", master not in VOID_FINGERPRINTS, master)
    c.add("fingerprint.subplan_not_void", sub not in VOID_FINGERPRINTS, sub)
    c.add("fingerprint.no_void_code_anywhere_in_the_plan",
          not (VOID_FINGERPRINTS & set(re.findall(r"[0-9A-F]{12}",
               yaml.safe_dump(plan["subplans"], sort_keys=False)))))
    c.add("fingerprint.void_codes_recorded_as_superseded",
          VOID_FINGERPRINTS <= set(json.dumps(plan["supersedes"]).replace('"', " ").split()),
          str(plan["supersedes"]["MASTER"]) + "/" + str(
              plan["supersedes"]["EXISTING_RESOURCES"]))
    if args.expect_master:
        c.add("fingerprint.master_matches_expected",
              master == args.expect_master.strip().upper(), master)
    if args.expect_subplan:
        c.add("fingerprint.subplan_matches_expected",
              sub == args.expect_subplan.strip().upper(), sub)

    print(f"PLAN      {args.plan}")
    print(f"MASTER    {master}")
    print(f"SUBPLAN   EXISTING_RESOURCES {sub}   "
          f"actions={len(actions)} objects={objects}\n")
    failed = c.report()
    if failed:
        print(f"\nVALIDATION FAILED: {failed} check(s)")
        return 1
    print("\nVALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
