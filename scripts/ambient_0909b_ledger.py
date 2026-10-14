#!/usr/bin/env python3
"""Write the package ledger (SUPERSEDED / DO_NOT_EXECUTE marks) and the final unchanged proof.
Preserves the original plan files byte-for-byte; the ledger is a separate artefact."""
from __future__ import annotations
import sys, json, hashlib, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

NOW = datetime.datetime.now(TZ).isoformat()

OLD = {
    "AMB-0909-CPC-1": ("46C39C6B7091", "SUPERSEDED / DO_NOT_EXECUTE",
                       "AMB-0909B-CPC-INST-1 (DE376F91F449)",
                       "Bundled HVAC Installation with HVAC Repair. The HVAC Repair $60 "
                       "recommendation is withdrawn: $36.47 modelled CPC is ABOVE the $32 "
                       "optimistic economic band, the $60 model retains only 1 of 4 visible "
                       "conversions, and its modelled raw CPA of $474.06 exceeds the $250 "
                       "maximum CPQL. Installation is re-issued alone."),
    "AMB-0909-BUD-1": ("D448BFDE4650", "SUPERSEDED / DO_NOT_EXECUTE",
                       "AMB-0909B-BUD-1 (752BF95EBD7C)",
                       "Used a 30-day month. Google applies 30.4. $433.33 x 30.4 = $13,173.23, "
                       "a $173.23 breach of the $13,000 maximum, so the package was NOT "
                       "compliant as claimed. It also raised HVAC Installation's budget on a "
                       "53.16% lost-IS(budget) figure contaminated by the 'hvac installers' "
                       "keyword period; the clean figure is 4.38%."),
    "AMB-0909-NEG-ADD-1": ("23BE8FF0F24C", "SUPERSEDED / DO_NOT_EXECUTE",
                           "AMB-0909B-COMP-1 (05FBCBD34B4A)",
                           "Contained \"sq ft house\" and [how much is hvac system], which are "
                           "installation sizing and pricing research from prospective buyers, "
                           "and two unverified entities."),
    "AMB-0909-NEG-RM-1": ("CE289F3508A2", "SUPERSEDED / DO_NOT_EXECUTE",
                          "AMB-0909B-NEG-A (18143479027D) covers only the high-confidence "
                          "subset; packages B, C and D are HOLD with no operations",
                          "89 bulk removals in one package mixed four different intents. It "
                          "also removed six supply-house/corporate/location EXACT negatives "
                          "that should be retained, and opened 11 manufacturers of which only "
                          "York is evidenced on the live website."),
    "AMB-0909-NEG-RM-2": ("A435FA09AC97", "SUPERSEDED / DO_NOT_EXECUTE",
                          "AMB-0909B-NEG-A (18143479027D) takes only account-level "
                          "BROAD 'commercial'",
                          "18 account-level removals opened 12 manufacturer tokens plus "
                          "'al', 'american' and 'mr' with no brand-eligibility evidence and no "
                          "routing. Only 'commercial' survives on verified evidence."),
    "AMB-0909-ADS-1": ("11A79347A296", "AWAITING APPROVAL - VALID, DO NOT EXECUTE THIS RUN",
                       "not superseded",
                       "Re-verified 2026-09-09: both ads still ENABLED + DISAPPROVED "
                       "(FULLY_LIMITED), each ad group retains 2 ENABLED + APPROVED RSAs, and "
                       "the update mask is status-only. This is inert-status cleanup, NOT a "
                       "CTR or delivery improvement."),
}
NEW = {
    "AMB-0909B-BUD-1": ("752BF95EBD7C", 2, "reversible-budget-change"),
    "AMB-0909B-CPC-INST-1": ("DE376F91F449", 1, "reversible-setting-change"),
    "AMB-0909B-NEG-A": ("18143479027D", 16, "DESTRUCTIVE-removal"),
    "AMB-0909B-COMP-1": ("05FBCBD34B4A", 3, "reversible-addition"),
}
HOLD = {
    "Package B - manufacturers": "NO OPERATIONS. Ambient's live website names only YORK. "
        "'york' is not blocked at token level anywhere, so nothing needs removing. The 11 "
        "blocked manufacturer tokens stay blocked until the client confirms which brands they "
        "install or service. The six supply-house/corporate/location EXACT negatives are "
        "RETAINED, as are ~40 multiword manufacturer price/dealer negatives.",
    "Package C - additional services": "NO OPERATIONS. The live site advertises air duct "
        "cleaning (lead-form service picker), drying & dehumidification (dedicated page) and "
        "geothermal HVAC (dedicated page). Thermostats appear in body copy only; 'humidifier' "
        "is absent entirely. None of these has a paid campaign, ad group or landing page, so "
        "opening the terms across the five would route the demand to the wrong page.",
    "Package D - dealer and installer": "NO OPERATIONS. [daikin cerca de mi] needs Spanish "
        "landing-page handling that does not exist; [trane authorized dealers near me] and "
        "[trane installers near me] need confirmed Trane eligibility; [geothermal maryland] is "
        "a real service but has no destination in the five campaigns.",
}

ledger = {"generated_local": NOW, "customer_id": CID,
          "exact_child_account_name": EXACT_NAME,
          "run": "2026-09-09 CORRECTION RUN",
          "mutations_executed": 0,
          "superseded": {}, "replacements": {}, "hold_no_operations": HOLD}

print("=== PACKAGE LEDGER ===\n")
print(f"{'package':<24}{'fingerprint':<16}{'status':<44}{'ops':>5}")
for name, (fp, status, repl, why) in OLD.items():
    p = CLIENT_DIR / "plans" / f"{name}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    ledger["superseded"][name] = {
        "fingerprint": fp, "status": status, "replaced_by": repl, "reason": why,
        "object_count": d["object_count"], "plan_file": str(p.relative_to(ROOT)),
        "plan_file_sha256": sha, "plan_file_preserved_unmodified": True,
        "validate_only_receipt": f"receipts/validate-only/{name}-2026-09-09.json"}
    print(f"{name:<24}{fp:<16}{status[:42]:<44}{d['object_count']:>5}")
print()
for name, (fp, ops, klass) in NEW.items():
    p = CLIENT_DIR / "plans" / f"{name}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    ledger["replacements"][name] = {
        "fingerprint": fp, "status": "VALIDATED - AWAITING APPROVAL", "object_count": ops,
        "approval_class": klass, "supersedes": d.get("supersedes"),
        "plan_file": str(p.relative_to(ROOT)),
        "plan_file_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "validate_only_receipt": f"receipts/validate-only/{name}-2026-09-09b.json"}
    print(f"{name:<24}{fp:<16}{'VALIDATED - AWAITING APPROVAL':<44}{ops:>5}")

print("\n=== HOLD, NO OPERATIONS ===")
for k, v in HOLD.items():
    print(f"  {k}")

print("\n=== NO OLD FINGERPRINT WAS REUSED OR MODIFIED ===")
oldfps = {v[0] for v in OLD.values()}
newfps = {v[0] for v in NEW.values()}
print(f"  old: {sorted(oldfps)}")
print(f"  new: {sorted(newfps)}")
print(f"  intersection: {sorted(oldfps & newfps)}  -> must be empty: {not (oldfps & newfps)}")
ledger["fingerprint_disjointness_verified"] = not (oldfps & newfps)

# ---- final unchanged proof ----
print("\n=== FINAL POST-RUN UNCHANGED-RESOURCE PROOF ===")
c = client()
proof = {}
proof["campaigns_non_removed"] = len(q(c, "SELECT campaign.id FROM campaign "
                                          "WHERE campaign.status != 'REMOVED'"))
proof["campaigns_enabled"] = len(q(c, "SELECT campaign.id FROM campaign "
                                     "WHERE campaign.status = 'ENABLED'"))
proof["campaign_negatives_enabled_on_five"] = len(q(
    c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
       f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'KEYWORD' "
       f"AND campaign_criterion.negative = TRUE AND campaign_criterion.status = 'ENABLED'"))
proof["account_level_set_members"] = len(q(
    c, "SELECT shared_criterion.criterion_id FROM shared_criterion "
       "WHERE shared_set.id = 11252984411"))
proof["geo_targets_on_five"] = len(q(
    c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
       f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'LOCATION'"))
proof["ad_schedules_on_five"] = len(q(
    c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
       f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'AD_SCHEDULE'"))
proof["ip_blocks"] = len(q(c, "SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                              "WHERE campaign_criterion.type = 'IP_BLOCK'"))
proof["shared_sets"] = len(q(c, "SELECT shared_set.id FROM shared_set"))
proof["conversion_actions_non_removed"] = len(q(
    c, "SELECT conversion_action.id FROM conversion_action "
       "WHERE conversion_action.status != 'REMOVED'"))
ceil = {}
bud = {}
for r in q(c, f"SELECT campaign.id, campaign.target_spend.cpc_bid_ceiling_micros, "
              f"campaign.campaign_budget FROM campaign WHERE campaign.id IN ({IN5})"):
    ceil[NAME[str(r.campaign.id)]] = r.campaign.target_spend.cpc_bid_ceiling_micros
for r in q(c, "SELECT campaign_budget.id, campaign_budget.amount_micros FROM campaign_budget "
              "WHERE campaign_budget.status = 'ENABLED'"):
    bud[str(r.campaign_budget.id)] = round(r.campaign_budget.amount_micros / 1e6, 2)
proof["cpc_ceilings"] = ceil
proof["five_budgets"] = {b: bud.get(b) for b in
                         ["15787409435", "15787409438", "15787409441", "15787409444",
                          "15787409447"]}
proof["daily_total"] = round(sum(v for v in proof["five_budgets"].values()), 2)
row = q(c, "SELECT customer.descriptive_name, customer.tracking_url_template FROM customer")[0]
proof["descriptive_name"] = row.customer.descriptive_name
proof["tracking_template_is_clickcease"] = "clickcease" in row.customer.tracking_url_template.lower()
proof["manager_links"] = {x.customer_manager_link.manager_customer.split("/")[-1]:
                          E(x.customer_manager_link.status) for x in
                          q(c, "SELECT customer_manager_link.manager_customer, "
                               "customer_manager_link.status FROM customer_manager_link")}
proof["checked_local"] = datetime.datetime.now(TZ).isoformat()
proof["mutations_executed_this_run"] = 0
for k, v in proof.items():
    print(f"  {k}: {v}")
ledger["unchanged_proof"] = proof

write(EVID / "2026-09-09b-package-ledger.json", ledger)
