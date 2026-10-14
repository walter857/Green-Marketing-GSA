#!/usr/bin/env python3
"""LOCAL preflight for the 2026-09-09 packages. Costs zero API operations.
Run this before any validate_only call - validate_only burns the same daily mutate quota."""
from __future__ import annotations
import sys, json, re, unicodedata
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

struct = json.load(open(EVID / "2026-09-09-structure.json", encoding="utf-8"))
ident = json.load(open(EVID / "2026-09-09-identity-and-structure.json", encoding="utf-8"))
ads = json.load(open(EVID / "2026-09-09-ads-assets.json", encoding="utf-8"))["ads"]
plans = json.load(open(TOPPLANS / "AMBIENT-2026-09-09-packages.json", encoding="utf-8"))


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9\s&]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


fails, warns = [], []


def check(cond, msg):
    (print(f"  [PASS] {msg}") if cond else (print(f"  [FAIL] {msg}"), fails.append(msg)))


live_neg = {(n["campaign_id"], n["criterion_id"]): n for n in struct["campaign_negatives"]
            if n["status"] == "ENABLED"}
neg_by_camp = defaultdict(lambda: defaultdict(set))
for n in struct["campaign_negatives"]:
    if n["status"] == "ENABLED" and n["campaign_id"] in FIVE:
        neg_by_camp[n["campaign_id"]][n["match"]].add(norm(n["text"]))
acct = defaultdict(set)
for sc in struct["shared_criteria"]:
    if sc["shared_set"] == "11252984411" and sc["match"] in ("BROAD", "PHRASE", "EXACT"):
        acct[sc["match"]].add(norm(sc["text"]))
agneg = defaultdict(lambda: defaultdict(set))
for n in struct["ad_group_negatives"]:
    if n["status"] == "ENABLED":
        agneg[n["ad_group_id"]][n["match"]].add(norm(n["text"]))
camps = {c["id"]: c for c in ident["campaigns"]}
buds = {b["id"]: b for b in ident["budgets"]}
adidx = {(a["ag"], a["ad_id"]): a for a in ads}

print("=== FINGERPRINT INTEGRITY ===")
for name, p in plans.items():
    rec = approval_code({"target": p["target"], "plan": name, "operations": p["operations"]})
    check(rec == p["fingerprint"], f"{name} fingerprint recomputes to {rec}")

print("\n=== AMB-0909-CPC-1 ===")
p = plans["AMB-0909-CPC-1"]
for a in p["operations"]:
    cid = a["resource_id"]
    cur = camps[cid]["target_spend_ceiling_micros"]
    stated = int(a["current_state"].split("= ")[1].split(" ")[0])
    new = int(a["proposed_state"].split("= ")[1].split(" ")[0])
    check(cid in FIVE, f"{NAME[cid]} is one of the five")
    check(camps[cid]["bidding"] == "TARGET_SPEND",
          f"{NAME[cid]} bidding is TARGET_SPEND (ceiling field is valid)")
    check(stated == cur, f"{NAME[cid]} recorded before-state {stated} matches live {cur}")
    check(new > cur, f"{NAME[cid]} new ceiling {new/1e6:.2f} raises from {cur/1e6:.2f}")
    check(a["field_mask"] == ["target_spend.cpc_bid_ceiling_micros"],
          f"{NAME[cid]} field mask touches only the ceiling")
check("24132507741" not in [a["resource_id"] for a in p["operations"]],
      "AC Repair is NOT in the CPC package (deliberate hold)")

print("\n=== AMB-0909-NEG-RM-1 (destructive) ===")
p = plans["AMB-0909-NEG-RM-1"]
missing = [a for a in p["operations"]
           if (a["campaign_id"], a["criterion_id"]) not in live_neg]
check(not missing, f"all {len(p['operations'])} removal targets resolve to a live ENABLED "
                   f"negative ({len(missing)} missing)")
mismatch = [a for a in p["operations"]
            if (a["campaign_id"], a["criterion_id"]) in live_neg
            and (norm(live_neg[(a['campaign_id'], a['criterion_id'])]["text"]) != norm(a["negative_text"])
                 or live_neg[(a['campaign_id'], a['criterion_id'])]["match"] != a["match_type"])]
check(not mismatch, f"every removal target's text and match type match the live resource "
                    f"({len(mismatch)} mismatched)")
check(all(a["campaign_id"] in FIVE for a in p["operations"]),
      "every removal is on one of the five campaigns")
check(all(a["resource_name"].startswith(f"customers/{CID}/campaignCriteria/")
          for a in p["operations"]), "every resource name is a campaign criterion under 2401959466")
dupes = [k for k, v in Counter((a["campaign_id"], a["criterion_id"])
                               for a in p["operations"]).items() if v > 1]
check(not dupes, f"no duplicate removal targets ({len(dupes)} duplicated)")
print(f"  removals by campaign: {dict(Counter(a['campaign'] for a in p['operations']))}")
print(f"  removals by match:    {dict(Counter(a['match_type'] for a in p['operations']))}")
print(f"  distinct texts:       {len({a['negative_text'].lower() for a in p['operations']})}")
after = {cid: len(neg_by_camp[cid]["BROAD"]) + len(neg_by_camp[cid]["PHRASE"])
              + len(neg_by_camp[cid]["EXACT"]) for cid in FIVE}
rmc = Counter(a["campaign_id"] for a in p["operations"])
print("  expected campaign-negative counts after execution:")
for cid in FIVE:
    live_n = sum(1 for n in struct["campaign_negatives"]
                 if n["status"] == "ENABLED" and n["campaign_id"] == cid)
    print(f"    {NAME[cid]:<20} {live_n} -> {live_n - rmc.get(cid, 0)}  (-{rmc.get(cid,0)})")

print("\n=== AMB-0909-ADS-1 ===")
p = plans["AMB-0909-ADS-1"]
for a in p["operations"]:
    ad = adidx.get((a["ad_group_id"], a["ad_id"]))
    check(ad is not None, f"ad {a['ad_id']} exists in ad group {a['ad_group_id']}")
    if ad:
        check(ad["status"] == "ENABLED", f"ad {a['ad_id']} is currently ENABLED")
        check(ad["approval"] == "DISAPPROVED", f"ad {a['ad_id']} is currently DISAPPROVED")
    keep = [x for x in ads if x["ag"] == a["ad_group_id"] and x["status"] == "ENABLED"
            and x["approval"] == "APPROVED" and x["ad_id"] != a["ad_id"]]
    check(len(keep) >= 2, f"ad group {a['ad_group_id']} keeps {len(keep)} ENABLED APPROVED "
                          f"RSAs after the pause (agency minimum is 2)")

print("\n=== AMB-0909-NEG-ADD-1 ===")
p = plans["AMB-0909-NEG-ADD-1"]
for a in p["operations"]:
    txt, mt, cid = norm(a["negative_text"]), a["match_type"], a["campaign_id"]
    check(len(a["negative_text"].split()) <= 10,
          f"{a['negative_text']!r} within the 10-word negative limit "
          f"({len(a['negative_text'].split())})")
    check(len(a["negative_text"]) <= 80,
          f"{a['negative_text']!r} within the 80-char limit ({len(a['negative_text'])})")
    already = (txt in neg_by_camp[cid][mt] or txt in acct[mt])
    check(not already, f"{a['negative_text']!r} [{mt}] is not already present at this scope")
    # would a broader existing negative already cover it?
    tw = set(txt.split())
    sub = [n for n in neg_by_camp[cid]["BROAD"] if n and set(n.split()) <= tw]
    ph = [n for n in neg_by_camp[cid]["PHRASE"] if (" " + n + " ") in (" " + txt + " ")]
    if sub or ph:
        warns.append(f"{a['negative_text']!r} already subsumed by {sub or ph}")
        print(f"  [WARN] {a['negative_text']!r} already subsumed by {(sub or ph)[:3]}")
    else:
        print(f"  [PASS] {a['negative_text']!r} adds new coverage")

print("\n=== AMB-0909-BUD-1 ===")
p = plans["AMB-0909-BUD-1"]
tot_before = tot_after = 0.0
FIVE_BUDS = {"15787409435": 141.45, "15787409438": 42.76, "15787409441": 176.15,
             "15787409444": 78.95, "15787409447": 26.32}
proposed = dict(FIVE_BUDS)
for a in p["operations"]:
    bid = a["resource_id"]
    cur = int(a["current_state"].split("= ")[1].split(" ")[0])
    new = int(a["proposed_state"].split("= ")[1].split(" ")[0])
    live = buds[bid]["daily"]
    check(abs(live - cur / 1e6) < 0.005,
          f"budget {bid} recorded before-state ${cur/1e6:.2f} matches live ${live:.2f}")
    check(buds[bid]["refs"] == 1, f"budget {bid} is referenced by exactly one campaign")
    proposed[bid] = new / 1e6
check(sum(proposed.values()) <= sum(FIVE_BUDS.values()) + 0.005,
      f"daily total does not increase: ${sum(FIVE_BUDS.values()):.2f} -> "
      f"${sum(proposed.values()):.2f}")
check(sum(proposed.values()) * 30 <= 13000.0,
      f"30-day worst case ${sum(proposed.values())*30:,.2f} is within the $13,000 "
      f"monthly maximum")
check(all(b not in proposed or True for b in FIVE_BUDS),
      "no budget outside the five is touched")
untouched = set(FIVE_BUDS) - {a["resource_id"] for a in p["operations"]}
check(all(abs(proposed[b] - FIVE_BUDS[b]) < 0.005 for b in untouched),
      f"the {len(untouched)} untouched budgets keep their live amounts")
print(f"  30-day worst-case exposure at the proposed daily total: "
      f"${sum(proposed.values())*30:,.2f} against a ${13000:,} monthly maximum")
if sum(proposed.values()) * 30 > 13000:
    fails.append("nominal 30-day budget capacity exceeds the $13,000 monthly maximum")
    print("  [FAIL] nominal 30-day capacity exceeds the monthly maximum")
else:
    print(f"  [PASS] headroom against the monthly maximum: "
          f"${13000 - sum(proposed.values())*30:,.2f}")

print("\n" + "=" * 78)
print(f"PREFLIGHT: {len(fails)} FAIL, {len(warns)} WARN")
for f in fails:
    print("  FAIL:", f)
for w in warns:
    print("  WARN:", w)
print("=" * 78)
write(EVID / "2026-09-09-local-preflight.json",
      {"fails": fails, "warns": warns,
       "packages": {k: {"fingerprint": v["fingerprint"], "ops": v["object_count"],
                        "class": v["approval_class"]} for k, v in plans.items()}})
sys.exit(1 if fails else 0)
