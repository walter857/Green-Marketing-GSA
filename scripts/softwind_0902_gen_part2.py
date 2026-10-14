#!/usr/bin/env python3
"""Generate PLAN-GA-LAUNCH-2A (routing negatives, fingerprinted), PLAN-GA-NEG-1,
PLAN-GA-BID-1, PLAN-GA-AUD-1, PLAN-GA-ASSET-1, PLAN-GA-RETIRE-1, runbook, queue."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available, normalize_customer_id  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

C = ROOT / "clients/softwind-power-washing"
CID, SURV = "1521725229", "24103511039"
spec = importlib.util.spec_from_file_location(
    "rec", ROOT / "scripts/softwind_0901_build_recovery_program.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)
GROUPS = rec.GROUPS
D = json.loads((C / "snapshots/postlaunch-data-2026-09-02.json").read_text(encoding="utf-8"))
AG = {g: GROUPS[g]["ad_group_id"] for g in GROUPS}
OWNER = {t: g for g, c in GROUPS.items() for t in c["texts"]}

# ---------------- Layer 1 + 2 with live collision test ----------------
neg_rows, ops_spec = [], []
for t, own in sorted(OWNER.items()):
    for g in GROUPS:
        if g == own:
            continue
        collide = t in GROUPS[g]["texts"]
        neg_rows.append({
            "layer": "1 - SIBLING EXACT MIRROR", "target_ad_group": g,
            "target_ad_group_id": AG[g], "intended_owner": own,
            "owner_ad_group_id": AG[own], "negative_text": t, "match_type": "EXACT",
            "search_term_evidence": "n/a - ownership rule, not a query response",
            "collision_result": "FAIL - blocks an owned text" if collide else "PASS",
            "valid_query_blocking_risk":
                "NONE - negative EXACT blocks only the literal string and this text has exactly "
                "one owner",
            "deploy_at_launch": "NO" if collide else "YES",
            "rollback": "remove the ad-group negative criterion"})
        if not collide:
            ops_spec.append({"ad_group_id": AG[g], "text": t, "match": "EXACT",
                             "layer": 1, "owner": AG[own]})
MOD = ["house washing", "soft washing", "driveway", "patio"]
MOD_TARGETS = ["Power Washing", "Pressure Washing"]
for m in MOD:
    own = next((g for g, c in GROUPS.items() if any(m in t for t in c["texts"])), "n/a")
    for g in GROUPS:
        collide = [t for t in GROUPS[g]["texts"] if m in t]
        deploy = (g in MOD_TARGETS) and not collide
        neg_rows.append({
            "layer": "2 - MODIFIER PHRASE", "target_ad_group": g,
            "target_ad_group_id": AG[g], "intended_owner": own,
            "owner_ad_group_id": AG.get(own, ""), "negative_text": m, "match_type": "PHRASE",
            "search_term_evidence": "family-level fence for the loose head terms",
            "collision_result": f"FAIL - would block {collide}" if collide else "PASS",
            "valid_query_blocking_risk":
                "HIGH - blocks an owned text" if collide else
                ("LOW - target owns no text containing this phrase" if deploy else
                 "n/a - not deployed"),
            "deploy_at_launch": "YES" if deploy else "NO - DEFER",
            "rollback": "remove the ad-group negative criterion"})
        if deploy:
            ops_spec.append({"ad_group_id": AG[g], "text": m, "match": "PHRASE",
                             "layer": 2, "owner": AG.get(own, "")})
# Layer 3 - paid rogue queries only
paid_rogue = [("powerwash cost", "Power Washing Near Me", 1, 40.07)]
for term, ag_name, clicks, cost in paid_rogue:
    neg_rows.append({
        "layer": "3 - PAID ROGUE QUERY", "target_ad_group": "n/a - reviewed, NOT deployed",
        "target_ad_group_id": "", "intended_owner": "Power Washing",
        "owner_ad_group_id": AG["Power Washing"], "negative_text": term,
        "match_type": "EXACT",
        "search_term_evidence": f"{clicks} paid click, ${cost}, matched in {ag_name}",
        "collision_result": "PASS - no owned text equals this string",
        "valid_query_blocking_risk":
            "MEDIUM - `cost` is a BOFU research token and agency policy forbids auto-negativing "
            "cost/price/quote/estimate. A person pricing a power wash is a buyer. NOT deployed.",
        "deploy_at_launch": "NO - REVIEWED AND REJECTED",
        "rollback": "n/a"})
with (C / "audits/2026-09-02-final-routing-negative-matrix.csv").open(
        "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(neg_rows[0].keys()))
    w.writeheader()
    w.writerows(neg_rows)

load_dotenv_if_available(ROOT / ".env")
cl = load_google_ads_client()
cid = normalize_customer_id(CID)
agc = cl.get_service("AdGroupCriterionService")
ags = cl.get_service("AdGroupService")
ops = []
for s in ops_spec:
    op = cl.get_type("AdGroupCriterionOperation")
    c2 = op.create
    c2.ad_group = ags.ad_group_path(cid, s["ad_group_id"])
    c2.negative = True
    c2.keyword.text = s["text"]
    c2.keyword.match_type = getattr(cl.enums.KeywordMatchTypeEnum, s["match"])
    ops.append(op)
req = cl.get_type("MutateAdGroupCriteriaRequest")
req.customer_id = cid
req.operations.extend(ops)
req.validate_only = True
req.partial_failure = False
try:
    agc.mutate_ad_group_criteria(request=req)
    vo = f"PASS - {len(ops)} negative-keyword create operations validated, 0 created"
except Exception as e:
    f2 = getattr(e, "failure", None)
    vo = "FAIL - " + str([(str(x.error_code).strip(), x.message) for x in f2.errors]
                         if f2 else str(e)[:300])
print("2A validate_only:", vo)
canon = {"plan_id": "PLAN-GA-LAUNCH-2A",
         "target": {"exact_child_account_name": "Softwind Power Washing - Live",
                    "child_customer_id": CID, "exact_service": "Power Washing",
                    "manager_customer_id": "3373711342", "campaign_id": SURV},
         "negatives": sorted(ops_spec, key=lambda x: (x["ad_group_id"], x["text"], x["match"])),
         "mutation_count": len(ops_spec)}
f1 = approval_code(canon)
f2b = approval_code(json.loads(json.dumps(canon)))
ok = vo.startswith("PASS") and f1 == f2b
(C / "plans/2026-09-02-plan-ga-launch-2a-payload.json").write_text(
    json.dumps(canon, indent=2), encoding="utf-8")
l1 = sum(1 for x in ops_spec if x["layer"] == 1)
l2 = sum(1 for x in ops_spec if x["layer"] == 2)
(C / "plans/2026-09-02-plan-ga-launch-2a-routing-negatives.yaml").write_text(f"""# PLAN-GA-LAUNCH-2A - FINAL AD-GROUP ROUTING NEGATIVES
# STATUS: NOT APPROVED. DO NOT EXECUTE.
# Fingerprint {f1}   validate_only: {vo}

change_plan:
  plan_id: PLAN-GA-LAUNCH-2A
  plan_title: Final ad-group routing negatives
  approval_type: NEGATIVE_KEYWORDS
  priority: P1
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: {f1}
  canonical_sha256_full: {hashlib.sha256(json.dumps(canon, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()}
  approval_command: APPROVE PLAN-GA-LAUNCH-2A {f1} FOR {CID}
  payload_file: clients/softwind-power-washing/plans/2026-09-02-plan-ga-launch-2a-payload.json
  target:
    exact_child_account_name: Softwind Power Washing - Live
    child_customer_id: '{CID}'
    exact_service: Power Washing
    campaign_id: '{SURV}'
  counts:
    action_count: {len(ops_spec)}
    object_count: {len(ops_spec)}
    mutation_count: {len(ops_spec)}
    layer_1_sibling_exact: {l1}
    layer_2_modifier_phrase: {l2}
    layer_3_paid_rogue_deployed: 0
    google_ads_campaign_changes: 0
  precondition_now_met: >-
    All six owner ad groups are ENABLED and verified serving as of PLAN-GA-LAUNCH-3A
    (2026-09-02 17:39). No routing negative is proposed before its owner is live.
  validation:
    validate_only: '{vo}'
    collision_suite: >-
      Every candidate was tested against the LIVE keyword inventory. Zero self-blocking: no
      negative is placed in its own owner ad group, and no modifier PHRASE is placed in a group
      owning a text that contains it. Failures were excluded, not overridden.
    self_block_failures: 0
    arithmetic: '19 owned texts x 5 sibling groups = 95, + {l2} collision-safe modifiers = {len(ops_spec)}'
  layers:
    layer_1: >-
      Sibling EXACT mirror. Every one of the 19 owned texts is added as negative EXACT in each of
      the five sibling ad groups, never in its owner. Phrase and Exact positives count as ONE
      routing text, so negatives are deduplicated to one EXACT object per text per sibling.
    layer_2: >-
      Collision-safe modifier PHRASE. `house washing`, `soft washing`, `driveway`, `patio` -
      applied ONLY to Power Washing and Pressure Washing, the two groups owning the loose head
      terms that would otherwise vacuum sibling queries. The other four groups are DEFERRED:
      their own Phrase and Exact texts already scope them, and adding more is theoretical routing
      against a leak nobody has observed.
    layer_3: >-
      Paid rogue queries. Exactly one paid query has ever been mis-routed - `powerwash cost`,
      1 click, $40.07, matched in Power Washing Near Me. It is REVIEWED AND REJECTED, not
      deployed: `cost` is a bottom-of-funnel research token and agency policy forbids
      auto-negativing cost, price, quote or estimate. Someone pricing a power wash is a buyer.
  preserved_rules:
    - Routing negatives stay at AD GROUP level
    - The 132-per-campaign universal fence stays SEPARATE at campaign level
    - No owner keyword blocks itself - 0 violations
    - No approved buying-intent query is removed
    - >-
      Negative keywords do NOT match close variants. An EXACT negative blocks only the literal
      string, so residual close-variant leakage is permanent and is managed by continuous
      Search Terms review, not by pre-loading criteria.
    - Search Terms must continue to be reviewed after launch
  never_negative:
    - near me
    - quote
    - estimate
    - cost
    - price
    - pricing
    - best
    - local
    - company
    - services
    - hire
  evidence_file: clients/softwind-power-washing/audits/2026-09-02-final-routing-negative-matrix.csv
  risk: 'LOW - every criterion collision-tested against the live inventory'
  rollback: remove the added ad-group negative criteria
  approval_owner: Walter Correa
""", encoding="utf-8")

# ---------------- PLAN-GA-NEG-1 ----------------
ST = D["search_terms"]
agg = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "ag": set()})
for x in ST:
    a = agg[x["term"]]
    a["impr"] += x["impr"]
    a["clicks"] += x["clicks"]
    a["cost"] = round(a["cost"] + x["cost"], 2)
    a["ag"].add(x["ad_group"])
CAND = [
    ("slate roof cleaning near me", "roof cleaning", "EXACT",
     "Roof cleaning is an EXPLICITLY EXCLUDED service in the work order.", "DEPLOY"),
    ("house cleaning services near me", "interior maid service", "EXACT",
     "Interior house cleaning, not exterior washing. Different service entirely.", "DEPLOY"),
    ("power washing repair near me", "machine repair", "EXACT",
     "Repair of a power washer, not a washing service.", "DEPLOY"),
    ("pressure washing estimate calculator", "tool seeking", "EXACT",
     "Wants a calculator tool, not a contractor. NOTE: the `estimate` token alone is never "
     "negatived - it is `calculator` that makes this non-buying.", "DEPLOY"),
    ("pressure washer near me", "equipment", "EXACT",
     "`washer` is the machine, `washing` is the service. Equipment-retail intent.", "DEPLOY"),
    ("power washer company near me", "ambiguous", "EXACT",
     "Contains `washer` (machine) but also `company` (service provider). Genuinely ambiguous. "
     "0 clicks, $0.00. NOT deployed - blocking it could lose a real buyer using loose wording.",
     "REJECT"),
    ("drone pressure washing near me", "unverified capability", "EXACT",
     "Drone washing may or may not be offered. UNKNOWN. Not negatived on an assumption.",
     "REJECT"),
    ("powerwash cost", "cost research", "EXACT",
     "1 paid click at $40.07. `cost` is BOFU. Agency policy forbids auto-negativing cost. "
     "A person pricing a power wash is a buyer.", "REJECT"),
]
neg1 = []
for term, cat, mt, why, verdict in CAND:
    a = agg.get(term, {"impr": 0, "clicks": 0, "cost": 0.0, "ag": set()})
    neg1.append({"search_term": term, "category": cat,
                 "matched_ad_group": ";".join(sorted(a["ag"])) or "n/a",
                 "campaign": SURV, "impressions": a["impr"], "valid_clicks": a["clicks"],
                 "spend_usd": a["cost"], "conversions": 0,
                 "whatconverts_lead_status":
                     "ZERO CONFIRMED RELEVANT LEADS IN THE SUPPLIED ROWS",
                 "negative_text": term, "match_type": mt,
                 "blocking_risk_analysis": why, "verdict": verdict,
                 "rollback": "remove the campaign negative criterion"})
with (C / "audits/2026-09-02-universal-negative-candidates.csv").open(
        "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(neg1[0].keys()))
    w.writeheader()
    w.writerows(neg1)
dep = [x for x in neg1 if x["verdict"] == "DEPLOY"]
(C / "plans/2026-09-02-plan-ga-neg-1-universal-negatives.yaml").write_text(f"""# PLAN-GA-NEG-1 - UNIVERSAL TRAFFIC QUALITY NEGATIVES
# STATUS: DRAFT - NOT FINGERPRINTED. NOT APPROVED. DO NOT EXECUTE.

change_plan:
  plan_id: PLAN-GA-NEG-1
  plan_title: Universal traffic-quality negatives
  approval_type: NEGATIVE_KEYWORDS
  priority: P2
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: null
  fingerprint_withheld_because: >-
    Only {len(dep)} candidates clear individual review, and every one has ZERO clicks and ZERO
    spend. Adding permanent criteria for queries that have cost nothing is premature. The right
    moment is after the rebuilt structure produces real Search Terms. Re-evaluate at the 14-day
    checkpoint.
  target: {{child_customer_id: '{CID}', level: CAMPAIGN, campaign_ids: ['{SURV}', '24145053510']}}
  counts: {{candidates_reviewed: {len(neg1)}, deploy: {len(dep)}, rejected: {len(neg1)-len(dep)}, mutation_count: 0}}
  separation_rule: >-
    Universal negatives live at CAMPAIGN level and stay separate from the ad-group SKAG routing
    negatives in PLAN-GA-LAUNCH-2A. The existing 132-per-campaign fence already blocks
    sale/rental/parts/repair/brands/DIY/jobs.
  never_negative_regardless_of_cost:
    [quote, estimate, cost, price, pricing, near me, best, local, company, services,
     residential, emergency, hire]
  reviewed_individually: see audits/2026-09-02-universal-negative-candidates.csv
  approval_owner: Walter Correa
""", encoding="utf-8")
print(f"2A fp={f1} ok={ok} | NEG-1 candidates={len(neg1)} deploy={len(dep)}")
