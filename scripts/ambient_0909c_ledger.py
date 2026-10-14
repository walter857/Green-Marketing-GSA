#!/usr/bin/env python3
"""Third-pass package ledger + final unchanged proof."""
from __future__ import annotations
import sys, json, hashlib, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

NOW = datetime.datetime.now(TZ).isoformat()

SUPERSEDED_NOW = {
    "AMB-0909B-BUD-1": ("752BF95EBD7C", "AMB-0909C-BUD-1 (A7118436590B)",
                        "Computed the September maximum as account spend-to-date plus a "
                        "COMBINED budget formula. Each campaign carries its own monthly limit. "
                        "Rebuilt per campaign. Also lacked a compliant rollback: a blind "
                        "restore of $42.76 + $26.32 returns the account to $14,155.15 over "
                        "30.4 days, a breach."),
    "AMB-0909B-CPC-INST-1": ("DE376F91F449", "AMB-0909C-CPC-INST-2 (5D57E0EF3B70)",
                             "Quoted a $141.87 raw CPA that divided VISIBLE search-term cost "
                             "($425.60) by CAMPAIGN-level conversions (3) - two different "
                             "measurement grains. Correct campaign-level raw CPA is $161.33. "
                             "It also used a 30-click rollback trigger, which at a $65 ceiling "
                             "permits up to $1,950 of spend before intervention."),
    "AMB-0909B-COMP-1": ("05FBCBD34B4A", "AMB-0909C-COMP-1 (D434D6F41747)",
                         "Used PHRASE 'maryland mechanical heating', which can overlap generic "
                         "Maryland mechanical-heating intent. Replaced with EXACT on the "
                         "verbatim observed query 'maryland mechanical heating & cooling'."),
    "AMB-0909B-NEG-A": ("18143479027D", "split into AMB-0909C-NEG-SAVAGE (10F76004E1B6) and "
                                        "AMB-0909C-NEG-COMMERCIAL (9F88FEE76803); 'licensed' "
                                        "and 'free' both HELD",
                        "Bundled four different intents into one 16-operation package. Split "
                        "into independent packages. The 'licensed' removals failed their "
                        "required proof and the 'free' removals lack search-term evidence."),
}
EARLIER = {
    "AMB-0909-CPC-1": "46C39C6B7091", "AMB-0909-BUD-1": "D448BFDE4650",
    "AMB-0909-NEG-ADD-1": "23BE8FF0F24C", "AMB-0909-NEG-RM-1": "CE289F3508A2",
    "AMB-0909-NEG-RM-2": "A435FA09AC97",
}
NEW = {"AMB-0909C-BUD-1": "A7118436590B", "AMB-0909C-CPC-INST-2": "5D57E0EF3B70",
       "AMB-0909C-NEG-SAVAGE": "10F76004E1B6", "AMB-0909C-NEG-COMMERCIAL": "9F88FEE76803",
       "AMB-0909C-COMP-1": "D434D6F41747"}
HELD = {
    "NEG-LICENSED (5 operations, NOT drafted)":
        "The correction brief required proof that 'licensed' is supported advertising language. "
        "It could not be proved. Zero live ENABLED ad assets or callouts on the five campaigns "
        "contain 'licens/licenc'. All five paid landing pages return ZERO matches for "
        "licensed / licence / insured / bonded / certified / NATE. The main website's only "
        "match is the footer string 'CERTIFIED SERVICE TECHNICIAN', which is 'certified', not "
        "'licensed and insured'. HELD pending a claim-substantiation answer from the client.",
    "NEG-FREE (5 operations, HELD as instructed)":
        "Only ONE observed search-term row since launch contains 'free': "
        "'hvac repair free estimate near me', 6 impressions, 0 clicks, $0.00, in HVAC Repair. "
        "Zero free-repair, free-service, free-parts or free-diagnostic queries were observed. "
        "Zero 'free' queries have EVER converted account-wide. There is no campaign-specific "
        "routing evidence, so the removal is not justified.",
    "Package B - manufacturers": "NO OPERATIONS. Only YORK appears on Ambient's live website, "
                                 "and 'york' is not blocked at token level anywhere.",
    "Package C - additional services": "NO OPERATIONS. Air duct cleaning, dehumidification and "
                                       "geothermal are advertised but have no campaign, ad "
                                       "group or paid landing page.",
    "Package D - dealer and installer": "NO OPERATIONS. Brand eligibility and Spanish-language "
                                        "handling unverified.",
}

led = {"generated_local": NOW, "customer_id": CID, "exact_child_account_name": EXACT_NAME,
       "run": "2026-09-09 THIRD PASS", "mutations_executed": 0,
       "superseded_this_run": {}, "superseded_earlier": {}, "retained": {},
       "replacements": {}, "held_no_operations": HELD}

print("=== PACKAGE LEDGER, THIRD PASS ===\n")
print(f"{'package':<28}{'fingerprint':<16}{'status':<40}{'ops':>5}")
for n, (fp, repl, why) in SUPERSEDED_NOW.items():
    p = CLIENT_DIR / "plans" / f"{n}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    led["superseded_this_run"][n] = {
        "fingerprint": fp, "status": "SUPERSEDED / DO_NOT_EXECUTE", "replaced_by": repl,
        "reason": why, "object_count": d["object_count"],
        "plan_file": str(p.relative_to(ROOT)),
        "plan_file_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "plan_file_preserved_unmodified": True}
    print(f"{n:<28}{fp:<16}{'SUPERSEDED / DO_NOT_EXECUTE':<40}{d['object_count']:>5}")
for n, fp in EARLIER.items():
    p = CLIENT_DIR / "plans" / f"{n}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    led["superseded_earlier"][n] = {
        "fingerprint": fp, "status": "SUPERSEDED / DO_NOT_EXECUTE (second pass)",
        "object_count": d["object_count"], "plan_file": str(p.relative_to(ROOT)),
        "plan_file_sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    print(f"{n:<28}{fp:<16}{'SUPERSEDED (second pass)':<40}{d['object_count']:>5}")

p = CLIENT_DIR / "plans" / "AMB-0909-ADS-1.json"
d = json.loads(p.read_text(encoding="utf-8"))
led["retained"]["AMB-0909-ADS-1"] = {
    "fingerprint": "11A79347A296", "status": "RETAINED, REVALIDATED, AWAITING APPROVAL",
    "object_count": d["object_count"], "plan_file": str(p.relative_to(ROOT)),
    "plan_file_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
    "revalidation_receipt":
        "receipts/validate-only/AMB-0909-ADS-1-2026-09-09c-revalidation.json",
    "note": "Inert-status cleanup. Not a CTR or delivery improvement."}
print(f"{'AMB-0909-ADS-1':<28}{'11A79347A296':<16}"
      f"{'RETAINED + REVALIDATED':<40}{d['object_count']:>5}")
print()
for n, fp in NEW.items():
    p = CLIENT_DIR / "plans" / f"{n}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    led["replacements"][n] = {
        "fingerprint": fp, "status": "VALIDATED - AWAITING APPROVAL",
        "object_count": d["object_count"], "approval_class": d["approval_class"],
        "supersedes": d.get("supersedes"), "plan_file": str(p.relative_to(ROOT)),
        "plan_file_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "validate_only_receipt": f"receipts/validate-only/{n}-2026-09-09c.json"}
    print(f"{n:<28}{fp:<16}{'VALIDATED - AWAITING APPROVAL':<40}{d['object_count']:>5}")

newops = sum(v["object_count"] for v in led["replacements"].values())
led["operation_count"] = {"new_packages": newops, "carried_forward_ads_1": 2,
                          "approval_block_total": newops + 2,
                          "brief_expected_new": 22, "brief_expected_total": 24,
                          "delta_explanation":
                              "The brief expected 22 new + 2 = 24. The delta of 10 is exactly "
                              "the 5 'licensed' and 5 'free' removals, both HELD: 'licensed' "
                              "failed its required proof and 'free' has no search-term "
                              "evidence. 12 new + 2 = 14."}
print(f"\n  NEW PACKAGE OPERATIONS : {newops}")
print(f"  CARRIED-FORWARD ADS-1  : 2")
print(f"  APPROVAL BLOCK TOTAL   : {newops + 2}")
print(f"\n  The brief anticipated 22 new / 24 total. The 10-operation delta is exactly the")
print(f"  5 'licensed' + 5 'free' removals, both held. See the report.")

print("\n=== HELD, NO OPERATIONS ===")
for k in HELD:
    print(f"  {k}")

print("\n=== FINGERPRINT DISJOINTNESS ===")
allold = set(EARLIER.values()) | {v[0] for v in SUPERSEDED_NOW.values()} | {"11A79347A296"}
allnew = set(NEW.values())
print(f"  prior: {sorted(allold)}")
print(f"  new  : {sorted(allnew)}")
print(f"  intersection empty: {not (allold & allnew)}")
led["fingerprints_disjoint"] = not (allold & allnew)

print("\n=== FINAL UNCHANGED-RESOURCE PROOF ===")
c = client()
pr = {}
pr["campaigns_non_removed"] = len(q(c, "SELECT campaign.id FROM campaign "
                                       "WHERE campaign.status != 'REMOVED'"))
pr["campaigns_enabled"] = len(q(c, "SELECT campaign.id FROM campaign "
                                   "WHERE campaign.status = 'ENABLED'"))
pr["campaign_negatives_enabled_on_five"] = len(q(
    c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
       f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'KEYWORD' "
       f"AND campaign_criterion.negative = TRUE AND campaign_criterion.status = 'ENABLED'"))
pr["account_level_set_members"] = len(q(
    c, "SELECT shared_criterion.criterion_id FROM shared_criterion "
       "WHERE shared_set.id = 11252984411"))
pr["geo_targets_on_five"] = len(q(
    c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
       f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'LOCATION'"))
pr["ad_schedules_on_five"] = len(q(
    c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
       f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'AD_SCHEDULE'"))
pr["ip_blocks"] = len(q(c, "SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                           "WHERE campaign_criterion.type = 'IP_BLOCK'"))
pr["shared_sets"] = len(q(c, "SELECT shared_set.id FROM shared_set"))
pr["conversion_actions_non_removed"] = len(q(
    c, "SELECT conversion_action.id FROM conversion_action "
       "WHERE conversion_action.status != 'REMOVED'"))
ceil, bud = {}, {}
for r in q(c, f"SELECT campaign.id, campaign.target_spend.cpc_bid_ceiling_micros "
              f"FROM campaign WHERE campaign.id IN ({IN5})"):
    ceil[NAME[str(r.campaign.id)]] = r.campaign.target_spend.cpc_bid_ceiling_micros
for r in q(c, "SELECT campaign_budget.id, campaign_budget.amount_micros FROM campaign_budget "
              "WHERE campaign_budget.status = 'ENABLED'"):
    bud[str(r.campaign_budget.id)] = round(r.campaign_budget.amount_micros / 1e6, 2)
pr["cpc_ceilings"] = ceil
pr["five_budgets"] = {b: bud.get(b) for b in ["15787409435", "15787409438", "15787409441",
                                              "15787409444", "15787409447"]}
pr["daily_total"] = round(sum(pr["five_budgets"].values()), 2)
row = q(c, "SELECT customer.descriptive_name, customer.tracking_url_template FROM customer")[0]
pr["descriptive_name"] = row.customer.descriptive_name
pr["tracking_template_is_clickcease"] = ("clickcease" in
                                         row.customer.tracking_url_template.lower())
pr["manager_links"] = {x.customer_manager_link.manager_customer.split("/")[-1]:
                       E(x.customer_manager_link.status) for x in
                       q(c, "SELECT customer_manager_link.manager_customer, "
                            "customer_manager_link.status FROM customer_manager_link")}
pr["checked_local"] = datetime.datetime.now(TZ).isoformat()
pr["mutations_executed_this_run"] = 0
for k, v in pr.items():
    print(f"  {k}: {v}")
led["unchanged_proof"] = pr
write(EVID / "2026-09-09c-package-ledger.json", led)
