#!/usr/bin/env python3
"""Ambient Cooling - Live | FINAL READBACK after the three approved executions.

Read-only. Diffs live state against the preflight structural baseline and proves
that exactly the nine approved operations landed and nothing else moved.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    CID, FIVE, IN5, NAME, RECEIPTS, TZ, client, q, identity_gate, E, write,
)

STAMP = "2026-08-28"
HVAC_INSTALL, AC_REPAIR = "24132507747", "24132507741"
ACCOUNT_SET, HANOVER_CRIT = "11252984411", "11143481"
A1 = ["armbridge", "blauch", "bluedot", "croppmetcalfe", "hugee",
      "michael & sons", "michael and sons"]
FAILS = []


def check(label, ok, detail=""):
    if not ok:
        FAILS.append(label)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" :: {detail}" if detail else ""))


def main():
    c = client()
    pre = json.loads((RECEIPTS / f"preflight-approved-{STAMP}.json").read_text(encoding="utf-8"))
    base = pre["structural_baseline"]
    ex = json.loads((RECEIPTS / f"execution-receipt-{STAMP}.json").read_text(encoding="utf-8"))
    out = {"stage": "FINAL READBACK", "customer_id": CID,
           "run_local": datetime.datetime.now(TZ).isoformat(),
           "baseline_source": f"receipts/preflight-approved-{STAMP}.json", "checks": {}}

    print("== IDENTITY ==")
    ident = identity_gate(c)
    out["identity"] = ident

    # ---------- 1-3 the nine operations ----------
    print("\n== 1. SEVEN COMPETITOR PHRASE NEGATIVES ON 24132507747 ==")
    hi = []
    for r in q(c, f"""SELECT campaign_criterion.resource_name, campaign_criterion.criterion_id,
                      campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
                      campaign_criterion.negative, campaign_criterion.status
                      FROM campaign_criterion WHERE campaign.id = {HVAC_INSTALL}
                        AND campaign_criterion.type='KEYWORD'
                        AND campaign_criterion.status!='REMOVED'"""):
        x = r.campaign_criterion
        hi.append({"criterion_id": str(x.criterion_id), "text": x.keyword.text,
                   "match": E(x.keyword.match_type), "negative": x.negative,
                   "status": E(x.status), "resource_name": x.resource_name})
    out["hvac_installation_negatives"] = hi
    for b in sorted(hi, key=lambda z: z["text"]):
        print(f"     [{b['match']:6s}] {b['text']:20s} id={b['criterion_id']:>13s} "
              f"neg={b['negative']} {b['status']}")
    check("exactly 7 negatives on HVAC Installation", len(hi) == 7, str(len(hi)))
    check("texts match the approved seven", sorted(b["text"] for b in hi) == A1)
    check("all PHRASE, negative, ENABLED",
          all(b["match"] == "PHRASE" and b["negative"] and b["status"] == "ENABLED" for b in hi))

    print("\n== 2. ONE 'automotive' BROAD NEGATIVE ON 24132507741 ==")
    ac = []
    for r in q(c, f"""SELECT campaign_criterion.resource_name, campaign_criterion.criterion_id,
                      campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
                      campaign_criterion.negative, campaign_criterion.status
                      FROM campaign_criterion WHERE campaign.id = {AC_REPAIR}
                        AND campaign_criterion.type='KEYWORD'
                        AND campaign_criterion.status!='REMOVED'"""):
        x = r.campaign_criterion
        ac.append({"criterion_id": str(x.criterion_id), "text": x.keyword.text,
                   "match": E(x.keyword.match_type), "negative": x.negative,
                   "status": E(x.status)})
    out["ac_repair_negatives"] = ac
    for b in sorted(ac, key=lambda z: z["text"]):
        print(f"     [{b['match']:6s}] {b['text']:20s} id={b['criterion_id']:>13s} "
              f"neg={b['negative']} {b['status']}")
    check("exactly 4 negatives on AC Repair", len(ac) == 4, str(len(ac)))
    check("texts are auto, automotive, boat, car",
          sorted(b["text"] for b in ac) == ["auto", "automotive", "boat", "car"])
    check("the three pre-existing criterion ids are untouched",
          {"10000390", "10008241", "10019071"} <= {b["criterion_id"] for b in ac})
    check("all BROAD, negative, ENABLED",
          all(b["match"] == "BROAD" and b["negative"] and b["status"] == "ENABLED" for b in ac))

    print("\n== 3. ONE HANOVER ACCOUNT-LEVEL REMOVAL ==")
    mem = {}
    for r in q(c, f"""SELECT shared_criterion.criterion_id, shared_criterion.keyword.text,
                      shared_criterion.keyword.match_type FROM shared_criterion
                      WHERE shared_set.id = {ACCOUNT_SET}"""):
        mem[str(r.shared_criterion.criterion_id)] = {
            "text": r.shared_criterion.keyword.text,
            "match": E(r.shared_criterion.keyword.match_type)}
    out["account_list_members_after"] = len(mem)
    before_members = {m["criterion_id"]: {"text": m["text"], "match": m["match"]}
                      for m in pre["account_list_members_before"]}
    removed = sorted(set(before_members) - set(mem))
    added = sorted(set(mem) - set(before_members))
    changed = [k for k in set(before_members) & set(mem) if before_members[k] != mem[k]]
    check("account-level list now has 58 members", len(mem) == 58, str(len(mem)))
    check("criterion 11143481 no longer exists", HANOVER_CRIT not in mem)
    check("exactly one member removed, and it is 11143481", removed == [HANOVER_CRIT], str(removed))
    check("zero members added", not added, str(added))
    check("zero members changed", not changed, str(changed))
    held = ["ducane", "ecobee", "frigidaire", "rudd", "ruud", "thermostat", "thermostats"]
    check("all 7 HELD negatives still present",
          sorted(v["text"] for v in mem.values() if v["text"].lower() in held) == held)

    print("\n== 4. OPERATION COUNT ==")
    created = len(ex["created_resource_names"])
    removed_n = len(ex["removed_resource_names"])
    check("exactly 8 resources created", created == 8, str(created))
    check("exactly 1 resource removed", removed_n == 1, str(removed_n))
    check("exactly 9 approved operations completed", created + removed_n == 9)

    # ---------- 5-6 nothing unapproved ----------
    print("\n== 5-6. NOTHING UNAPPROVED ADDED OR REMOVED ==")
    allneg = []
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id,
                      campaign_criterion.keyword.text FROM campaign_criterion
                      WHERE campaign.id IN ({IN5}) AND campaign_criterion.type='KEYWORD'
                        AND campaign_criterion.status!='REMOVED'"""):
        allneg.append((str(r.campaign.id), r.campaign_criterion.keyword.text))
    out["all_campaign_negatives_after"] = sorted(allneg)
    check("campaign negatives went 3 -> 11 exactly",
          len(allneg) == base["campaign_negatives"] + 8, str(len(allneg)))
    check("the other three campaigns still hold zero campaign negatives",
          not [x for x in allneg if x[0] not in (HVAC_INSTALL, AC_REPAIR)])

    # ---------- 7 keywords eligible ----------
    print("\n== 7. ALL ACTIVE KEYWORDS REMAIN ELIGIBLE ==")
    kw = []
    for r in q(c, f"""SELECT campaign.id, ad_group_criterion.keyword.text,
                      ad_group_criterion.keyword.match_type, ad_group_criterion.status,
                      ad_group_criterion.system_serving_status
                      FROM ad_group_criterion WHERE campaign.id IN ({IN5})
                        AND ad_group_criterion.type='KEYWORD'
                        AND ad_group_criterion.status!='REMOVED'
                        AND ad_group_criterion.negative=FALSE
                        AND ad_group.status!='REMOVED'"""):
        kw.append({"campaign": NAME[str(r.campaign.id)],
                   "text": r.ad_group_criterion.keyword.text,
                   "match": E(r.ad_group_criterion.keyword.match_type),
                   "status": E(r.ad_group_criterion.status),
                   "serving": E(r.ad_group_criterion.system_serving_status)})
    out["keywords_after"] = kw
    for k in sorted(kw, key=lambda z: (z["campaign"], z["match"], z["text"])):
        print(f"     {k['campaign']:20s} [{k['match'][:6]:6s}] {k['text']:26s} "
              f"{k['status']:8s} {k['serving']}")
    check("10 live positive keywords", len(kw) == 10, str(len(kw)))
    check("all ENABLED and ELIGIBLE",
          all(k["status"] == "ENABLED" and k["serving"] == "ELIGIBLE" for k in kw))

    # ---------- 8 everything else unchanged ----------
    print("\n== 8. EVERYTHING ELSE UNCHANGED vs THE PREFLIGHT BASELINE ==")
    now = {}
    now["campaigns"] = len(q(c, "SELECT campaign.id FROM campaign WHERE campaign.status!='REMOVED'"))
    now["ad_groups_on_five"] = len(q(c, f"SELECT ad_group.id FROM ad_group WHERE campaign.id IN ({IN5}) AND ad_group.status!='REMOVED'"))
    now["ads_on_five"] = len(q(c, f"SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE campaign.id IN ({IN5}) AND ad_group_ad.status!='REMOVED'"))
    now["positive_keywords"] = len(kw)
    now["budgets"] = {str(r.campaign_budget.id): r.campaign_budget.amount_micros for r in q(c,
        """SELECT campaign_budget.id, campaign_budget.amount_micros FROM campaign_budget
        WHERE campaign_budget.id IN (15787409435,15787409438,15787409441,15787409444,15787409447)""")}
    now["cpc_ceilings"] = sorted({r.campaign.target_spend.cpc_bid_ceiling_micros for r in q(c,
        f"SELECT campaign.id, campaign.target_spend.cpc_bid_ceiling_micros FROM campaign WHERE campaign.id IN ({IN5})")})
    # JSON round-trips a tuple to a list, so normalise both sides before comparing.
    now["excluded_asset_set_types"] = sorted(
        [list(t) for t in {tuple(E(z) for z in r.campaign.excluded_parent_asset_set_types)
         for r in q(c, f"SELECT campaign.id, campaign.excluded_parent_asset_set_types FROM campaign WHERE campaign.id IN ({IN5})")}])
    now["ip_exclusions"] = len(q(c, "SELECT campaign_criterion.criterion_id FROM campaign_criterion WHERE campaign_criterion.type='IP_BLOCK' AND campaign_criterion.status!='REMOVED'"))
    now["ad_schedule_rows"] = len(q(c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion WHERE campaign.id IN ({IN5}) AND campaign_criterion.type='AD_SCHEDULE' AND campaign_criterion.status!='REMOVED'"))
    now["location_criteria"] = len(q(c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion WHERE campaign.id IN ({IN5}) AND campaign_criterion.type='LOCATION' AND campaign_criterion.status!='REMOVED'"))
    now["conversion_actions"] = len(q(c, "SELECT conversion_action.id FROM conversion_action WHERE conversion_action.status!='REMOVED'"))
    now["wc_lead_include_in_conversions"] = [r.conversion_action.include_in_conversions_metric for r in q(c,
        "SELECT conversion_action.id, conversion_action.include_in_conversions_metric FROM conversion_action WHERE conversion_action.id = 7643656486")]
    now["sitelink_associations"] = len([r for r in q(c,
        f"SELECT campaign.id, campaign_asset.status FROM campaign_asset WHERE campaign.id IN ({IN5}) AND campaign_asset.field_type='SITELINK'")
        if E(r.campaign_asset.status) != "REMOVED"])
    now["campaign_shared_sets_on_five"] = len(q(c, f"SELECT campaign.id FROM campaign_shared_set WHERE campaign.id IN ({IN5})"))
    now["location_asset_set_status"] = [E(r.customer_asset_set.status) for r in q(c,
        "SELECT customer_asset_set.asset_set, customer_asset_set.status FROM customer_asset_set")
        if r.customer_asset_set.asset_set.endswith("8620443109")]
    now["manager_links"] = ident["manager_links"]
    out["structural_after"] = now
    for k in ("campaigns", "ad_groups_on_five", "ads_on_five", "positive_keywords",
              "budgets", "cpc_ceilings", "excluded_asset_set_types", "ip_exclusions",
              "ad_schedule_rows", "location_criteria", "conversion_actions",
              "wc_lead_include_in_conversions", "sitelink_associations",
              "campaign_shared_sets_on_five", "location_asset_set_status",
              "manager_links"):
        check(f"{k} unchanged", now[k] == base[k], f"before={base[k]} after={now[k]}")

    # ---------- 9-10 void / hold plans untouched ----------
    print("\n== 9-10. VOID AND HELD PLANS NOT EXECUTED ==")
    check("no CPC ceiling was created (VOID package B)", now["cpc_ceilings"] == [0])
    check("location asset untouched (VOID package C)",
          now["excluded_asset_set_types"] == [[]] and now["location_asset_set_status"] == ["ENABLED"])
    check("no conversion action changed (VOID EE6CFAD6667A95A1)",
          now["conversion_actions"] == base["conversion_actions"]
          and now["wc_lead_include_in_conversions"] == [False])
    check("the 7 HELD removals were not executed (D-2 4D7AF1C9CFCA27F9)", len(mem) == 58)

    plans = Path("clients/ambient-cooling-heating/plans")
    voids = {}
    for f, fp_ in (("AMBIENT-CONSOLIDATED-2026-08-27.json", "ACE80A09AC134C85"),
                   ("AMBIENT-CONV-1-2026-08-27.json", "EE6CFAD6667A95A1"),
                   ("AMBIENT-DEL-1-2026-08-27.json", "C3038EDD9E621944")):
        d = json.loads((plans / f).read_text(encoding="utf-8"))
        voids[fp_] = {"void": d.get("void"), "do_not_execute": d.get("do_not_execute")}
    out["void_markers"] = voids
    check("all three superseded fingerprints still marked VOID",
          all(v["void"] and v["do_not_execute"] for v in voids.values()), str(voids))

    # ---------- change history corroboration ----------
    print("\n== CHANGE HISTORY ==")
    ch = []
    for r in q(c, """SELECT change_event.change_date_time, change_event.change_resource_type,
                     change_event.resource_change_operation, change_event.user_email,
                     change_event.campaign FROM change_event
                     WHERE change_event.change_date_time >= '2026-08-28'
                       AND change_event.change_date_time <= '2026-08-29'
                     ORDER BY change_event.change_date_time DESC LIMIT 50"""):
        x = r.change_event
        ch.append({"when": x.change_date_time, "type": E(x.change_resource_type),
                   "op": E(x.resource_change_operation), "user": x.user_email,
                   "campaign": NAME.get(x.campaign.split("/")[-1], "")})
    out["change_events_today"] = ch
    print(f"  rows for 2026-08-28: {len(ch)}")
    for x in ch[:12]:
        print(f"     {x['when']} {x['op']:8s} {x['type']:22s} {x['campaign']} {x['user']}")
    if not ch:
        print("     none yet - change_event lags by hours and is not used as proof here;")
        print("     the resource readbacks above are the authoritative evidence.")

    out["failed_checks"] = FAILS
    out["result"] = "PASS" if not FAILS else "FAIL"
    write(RECEIPTS / f"final-readback-{STAMP}.json", out)
    print(f"\n== FINAL READBACK: {out['result']} ==")
    if FAILS:
        for f in FAILS:
            print(f"    - {f}")
        sys.exit(1)
    print("  Exactly 9 approved operations landed. Nothing else moved.")
    return out


if __name__ == "__main__":
    main()
