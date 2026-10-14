#!/usr/bin/env python3
"""Readback for AMB-0910-CPC-CAP-1 + the exact six-ad policy inventory.
Read-only after the executor's write. No mutation here."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
identity_gate(c, verbose=True)
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
FAIL = []


def chk(label, got, want):
    ok = got == want
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}: {got!r}" + ("" if ok else f" != {want!r}"))
    if not ok:
        FAIL.append(f"{label}: {got!r} != {want!r}")
    return ok


print("\n=== READBACK: AMB-0910-CPC-CAP-1 7EA6922309EB ===")
state = {}
for r in q(c, f"SELECT campaign.id, campaign.name, campaign.status, "
              f"campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros, "
              f"campaign_budget.id, campaign_budget.amount_micros, "
              f"campaign.geo_target_type_setting.positive_geo_target_type "
              f"FROM campaign WHERE campaign.id IN ({IN5})"):
    state[str(r.campaign.id)] = {
        "name": r.campaign.name, "status": E(r.campaign.status),
        "strategy": E(r.campaign.bidding_strategy_type),
        "ceiling": r.campaign.target_spend.cpc_bid_ceiling_micros,
        "budget_id": str(r.campaign_budget.id),
        "budget": r.campaign_budget.amount_micros,
        "geo": E(r.campaign.geo_target_type_setting.positive_geo_target_type)}

print("\n  intended changes:")
chk("Gas Boiler ceiling_micros", state["24132507744"]["ceiling"], 25000000)
chk("HVAC Replacement ceiling_micros", state["24132507753"]["ceiling"], 30000000)

print("\n  unrelated-resource assertions:")
chk("AC Repair ceiling unchanged", state["24132507741"]["ceiling"], 25000000)
chk("HVAC Repair ceiling unchanged", state["24132507750"]["ceiling"], 25000000)
chk("HVAC Installation ceiling unchanged", state["24132507747"]["ceiling"], 30000000)
chk("Gas Boiler budget unchanged", state["24132507744"]["budget"], 5000000)
chk("HVAC Replacement budget unchanged", state["24132507753"]["budget"], 20000000)
for cid, v in state.items():
    chk(f"{NAME[cid]} strategy", v["strategy"], "TARGET_SPEND")
    chk(f"{NAME[cid]} status", v["status"], "ENABLED")
    chk(f"{NAME[cid]} geo target type", v["geo"], "PRESENCE")

tot = sum(v["budget"] for v in state.values()) / 1e6
print(f"\n  combined daily ${tot:.2f}  x 30.4 = ${tot*30.4:,.2f}  "
      f"headroom ${13000 - tot*30.4:,.2f}")
chk("combined daily budget", round(tot, 2), 421.55)
if tot * 30.4 > 13000:
    FAIL.append("CHARGING LIMIT BREACH")

print("\n  every campaign now carries a ceiling:")
for cid, v in state.items():
    print(f"    {NAME[cid]:<20}${v['ceiling']/1e6:>6.2f}")
    if v["ceiling"] == 0:
        FAIL.append(f"{NAME[cid]} still uncapped")

print("\n  wider blast radius:")
# Scope these the way before-state-2026-09-10.json scoped them: REMOVED rows excluded,
# and geo counted on the five campaigns only. Counting every row inflates all three and
# produces false failures (33 / 83 / 1467).
n_camp = len(q(c, "SELECT campaign.id FROM campaign WHERE campaign.status != 'REMOVED'"))
n_ag = len(q(c, "SELECT ad_group.id FROM ad_group WHERE ad_group.status != 'REMOVED'"))
n_geo = len(q(c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                 f"WHERE campaign_criterion.type = 'LOCATION' AND campaign.id IN ({IN5})"))
n_ip = len(q(c, "SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                "WHERE campaign_criterion.type = 'IP_BLOCK'"))
n_ss = len(q(c, "SELECT shared_set.id FROM shared_set"))
n_ca = len(q(c, "SELECT conversion_action.id FROM conversion_action "
                "WHERE conversion_action.status != 'REMOVED'"))
n_neg = len(q(c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                 f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type='KEYWORD' "
                 f"AND campaign_criterion.negative=TRUE"))
for lbl, got, want in [("campaigns", n_camp, 23), ("ad groups", n_ag, 68),
                       ("geo criteria", n_geo, 375), ("IP blocks", n_ip, 2796),
                       ("shared sets", n_ss, 17), ("conversion actions", n_ca, 16),
                       ("campaign negatives on the five", n_neg, 6158)]:
    chk(lbl, got, want)

print(f"\n=== READBACK RESULT: {len(FAIL)} FAIL ===")
for f in FAIL:
    print(f"  {f}")
out["readback_failures"] = FAIL
out["state"] = {NAME[k]: {"ceiling_micros": v["ceiling"], "budget_micros": v["budget"],
                          "strategy": v["strategy"], "status": v["status"]}
                for k, v in state.items()}

# ---------------------------------------------------------------- SIX-AD POLICY
SIX = {"820900825434": ("HVAC Installation", "202339087634"),
       "820944944368": ("HVAC Replacement", "200159223798"),
       "820900825428": ("Gas Boiler Repair", None),
       "820900825431": ("Gas Boiler Repair", None),
       "820900825437": ("HVAC Installation", None),
       "820944944371": ("HVAC Replacement", None)}
print("\n\n=== EXACT SIX-AD POLICY INVENTORY ===")
inv = []
ids = ",".join(SIX)
for r in q(c, f"SELECT campaign.id, campaign.name, ad_group.id, ad_group.name, "
              f"ad_group.status, ad_group_ad.ad.id, ad_group_ad.status, "
              f"ad_group_ad.ad.type, ad_group_ad.ad.final_urls, "
              f"ad_group_ad.policy_summary.approval_status, "
              f"ad_group_ad.policy_summary.review_status, "
              f"ad_group_ad.policy_summary.policy_topic_entries "
              f"FROM ad_group_ad WHERE ad_group_ad.ad.id IN ({ids})"):
    x = r.ad_group_ad
    topics = []
    for t in x.policy_summary.policy_topic_entries:
        ev = []
        for e in t.evidences:
            d = {}
            for f in ("text_list", "website_list", "destination_not_working",
                      "destination_mismatch", "destination_text_list"):
                v = getattr(e, f, None)
                if v is not None and str(v).strip():
                    d[f] = str(v)[:400]
            if d:
                ev.append(d)
        cons = []
        for k in t.constraints:
            cons.append(str(k)[:400])
        topics.append({"topic": t.topic, "type": E(t.type_),
                       "evidences": ev, "constraints": cons})
    rec = {"ad_id": str(x.ad.id), "campaign": NAME.get(str(r.campaign.id), r.campaign.name),
           "campaign_id": str(r.campaign.id), "ad_group_id": str(r.ad_group.id),
           "ad_group": r.ad_group.name, "ad_group_status": E(r.ad_group.status),
           "ad_status": E(x.status), "ad_type": E(x.ad.type_),
           "final_urls": list(x.ad.final_urls),
           "approval_status": E(x.policy_summary.approval_status),
           "review_status": E(x.policy_summary.review_status),
           "policy_topics": topics}
    inv.append(rec)

for a in sorted(inv, key=lambda z: z["ad_id"]):
    print(f"\n  ad {a['ad_id']}  {a['campaign']}  ad group {a['ad_group_id']} "
          f"({a['ad_group_status']})")
    print(f"    ad status {a['ad_status']}  approval {a['approval_status']}  "
          f"review {a['review_status']}  type {a['ad_type']}")
    print(f"    final_urls {a['final_urls']}")
    for t in a["policy_topics"]:
        print(f"    TOPIC {t['topic']}  type={t['type']}")
        for e in t["evidences"]:
            print(f"      evidence {e}")
        for k in t["constraints"]:
            print(f"      constraint {k[:300]}")
    if not a["policy_topics"]:
        print("    (no policy topic entries returned)")
print(f"\n  ads returned: {len(inv)} / 6")
missing = set(SIX) - {a["ad_id"] for a in inv}
if missing:
    print(f"  NOT RETURNED: {sorted(missing)}")
out["six_ad_policy_inventory"] = inv
out["six_ad_missing"] = sorted(missing)

print("\n=== DELIVERY COVER: enabled+approved RSAs in each affected ad group ===")
affected = sorted({a["ad_group_id"] for a in inv})
for ag in affected:
    rows = q(c, f"SELECT campaign.id, ad_group.id, ad_group.status, ad_group_ad.ad.id, "
                f"ad_group_ad.status, ad_group_ad.policy_summary.approval_status "
                f"FROM ad_group_ad WHERE ad_group.id = {ag}")
    live = [r for r in rows if E(r.ad_group_ad.status) == "ENABLED"
            and E(r.ad_group_ad.policy_summary.approval_status) == "APPROVED"]
    cname = NAME.get(str(rows[0].campaign.id), "?") if rows else "?"
    agst = E(rows[0].ad_group.status) if rows else "?"
    print(f"  ad group {ag} ({cname}, {agst}): {len(rows)} ads, "
          f"{len(live)} ENABLED+APPROVED  -> {[str(r.ad_group_ad.ad.id) for r in live]}")
    out.setdefault("delivery_cover", {})[ag] = {
        "campaign": cname, "ad_group_status": agst, "total_ads": len(rows),
        "enabled_approved": [str(r.ad_group_ad.ad.id) for r in live]}

write(EVID / "2026-09-10c-readback-and-six-ad-policy.json", out)
