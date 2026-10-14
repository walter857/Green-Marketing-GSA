#!/usr/bin/env python3
"""Fresh read for PLAN-GA-LAUNCH-3A enablement. READ-ONLY.

Reads every resource created by PLAN-GA-LAUNCH-1 with fresh policy status, every
child resource inside the six final ad groups (to catch accidental legacy
activation), and the six Final URLs.
"""
from __future__ import annotations

import glob
import importlib.util
import json
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available, normalize_customer_id  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name  # noqa: E402

CID, SURVIVOR, RETIRING = "1521725229", "24103511039", "24145053510"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"

spec = importlib.util.spec_from_file_location(
    "rec", ROOT / "scripts/softwind_0901_build_recovery_program.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)
GROUPS, RSA = rec.GROUPS, rec.RSA

CREATED = json.loads((SNAP / "launch1-created-ids.json").read_text(encoding="utf-8"))
CREATED_KW = {(ag, c) for ag, lst in CREATED["keywords_by_ad_group"].items() for c in lst}
CREATED_ADS = {a for lst in CREATED["ads_by_ad_group"].values() for a in lst}

# The authoritative final inventory: ad_group_id -> {(text, match)}
FINAL = {}
for g, cfg in GROUPS.items():
    FINAL[cfg["ad_group_id"]] = {(t, m) for t in cfg["texts"] for m in ("PHRASE", "EXACT")}
AG2NAME = {cfg["ad_group_id"]: g for g, cfg in GROUPS.items()}


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    ga = load_google_ads_client().get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)

    def q(s):
        return list(ga.search(customer_id=cid, query=s))

    out = {}
    c = q("""SELECT customer.id, customer.descriptive_name, customer.manager,
                    customer.test_account, customer.status, customer.currency_code,
                    customer.time_zone FROM customer LIMIT 1""")[0].customer
    tz = c.time_zone or "America/New_York"
    now = datetime.now(ZoneInfo(tz))
    out["identity"] = {"name": c.descriptive_name, "id": str(c.id), "manager": bool(c.manager),
                       "test": bool(c.test_account), "status": enum_name(c.status),
                       "currency": c.currency_code, "tz": tz, "read_at": now.isoformat()}
    gate = (c.descriptive_name == "Softwind Power Washing - Live" and str(c.id) == CID
            and not c.manager and not c.test_account and enum_name(c.status) == "ENABLED"
            and c.currency_code == "USD" and tz == "America/New_York")
    out["identity_gate_pass"] = gate
    if not gate:
        print("IDENTITY GATE FAILED"); return 2

    # ---------- campaigns ----------
    out["campaigns"] = {}
    for r in q("""SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
                         campaign.target_spend.cpc_bid_ceiling_micros,
                         campaign.bidding_strategy_type
                  FROM campaign WHERE campaign.status != 'REMOVED'"""):
        k = r.campaign
        out["campaigns"][str(k.id)] = {
            "name": k.name, "status": enum_name(k.status),
            "serving": enum_name(k.serving_status),
            "ceiling_usd": round(k.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
            "bidding": enum_name(k.bidding_strategy_type)}

    # ---------- ad groups ----------
    ags = {}
    for r in q("""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status
                  FROM ad_group WHERE ad_group.status != 'REMOVED'"""):
        ags[str(r.ad_group.id)] = {"campaign": str(r.campaign.id), "name": r.ad_group.name,
                                   "status": enum_name(r.ad_group.status)}
    out["target_ad_groups"] = {a: {**ags[a], "final_group": AG2NAME[a]} for a in FINAL}

    # ---------- every keyword child of the six groups ----------
    kids = defaultdict(list)
    for r in q(f"""SELECT ad_group.id, ad_group_criterion.criterion_id,
                          ad_group_criterion.keyword.text,
                          ad_group_criterion.keyword.match_type,
                          ad_group_criterion.status,
                          ad_group_criterion.approval_status,
                          ad_group_criterion.system_serving_status,
                          ad_group_criterion.negative
                   FROM ad_group_criterion
                   WHERE ad_group_criterion.status != 'REMOVED'
                     AND ad_group.id IN ({','.join(FINAL)})"""):
        k = r.ad_group_criterion
        agid = str(r.ad_group.id)
        mt = enum_name(k.keyword.match_type)
        cidn = str(k.criterion_id)
        is_new = (agid, cidn) in CREATED_KW
        in_final = (k.keyword.text, mt) in FINAL[agid]
        st = enum_name(k.status)
        if k.negative:
            cls = "AD GROUP NEGATIVE - not in scope"
        elif is_new:
            cls = "FINAL - ENABLE"
        elif in_final and st == "ENABLED":
            cls = "FINAL - ALREADY ENABLED"
        elif in_final and st == "PAUSED":
            cls = "FINAL - ENABLE"
        elif st == "ENABLED":
            cls = "NON-FINAL AND CURRENTLY ENABLED - WOULD SERVE ON PARENT ENABLE"
        else:
            cls = "LEGACY - KEEP PAUSED"
        kids[agid].append({
            "criterion_id": cidn, "text": k.keyword.text, "match_type": mt,
            "status": st, "approval": enum_name(k.approval_status),
            "serving": enum_name(k.system_serving_status),
            "negative": bool(k.negative), "created_by_launch1": is_new,
            "in_final_inventory": in_final, "classification": cls,
            "broad_match": mt == "BROAD"})
    out["keyword_children"] = {a: sorted(kids[a], key=lambda x: (x["text"], x["match_type"]))
                               for a in FINAL}

    # ---------- every ad child of the six groups ----------
    adkids = defaultdict(list)
    for r in q(f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
                          ad_group_ad.ad.type, ad_group_ad.ad.final_urls,
                          ad_group_ad.policy_summary.approval_status,
                          ad_group_ad.policy_summary.review_status,
                          ad_group_ad.policy_summary.policy_topic_entries,
                          ad_group_ad.primary_status, ad_group_ad.primary_status_reasons,
                          ad_group_ad.ad.responsive_search_ad.path1,
                          ad_group_ad.ad.responsive_search_ad.path2,
                          ad_group_ad.ad.responsive_search_ad.headlines,
                          ad_group_ad.ad.responsive_search_ad.descriptions
                   FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'
                     AND ad_group.id IN ({','.join(FINAL)})"""):
        a = r.ad_group_ad
        agid = str(r.ad_group.id)
        adid = str(a.ad.id)
        is_new = adid in CREATED_ADS
        topics = [enum_name(t.topic_entry_type) + ":" + (t.topic or "")
                  for t in a.policy_summary.policy_topic_entries]
        appr = enum_name(a.policy_summary.approval_status)
        rev = enum_name(a.policy_summary.review_status)
        if appr == "DISAPPROVED":
            pol = "DISAPPROVED"
        elif appr == "APPROVED_LIMITED":
            pol = "APPROVED BUT LIMITED"
        elif appr == "APPROVED":
            pol = "APPROVED AND ELIGIBLE"
        elif rev in ("UNDER_REVIEW", "REVIEW_IN_PROGRESS"):
            pol = "UNDER REVIEW"
        elif appr in ("UNKNOWN", "UNSPECIFIED") and not topics:
            pol = "UNKNOWN WITH NO POLICY TOPIC"
        else:
            pol = "INELIGIBLE"
        st = enum_name(a.status)
        if is_new:
            cls = "FINAL - ENABLE"
        elif st == "ENABLED":
            cls = "LEGACY BUT SAFE DURING TRANSITION - already serving, retire later"
        else:
            cls = "LEGACY - KEEP PAUSED"
        adkids[agid].append({
            "ad_id": adid, "status": st, "type": enum_name(a.ad.type_),
            "created_by_launch1": is_new, "approval_status": appr,
            "review_status": rev, "policy_topics": topics,
            "policy_class": pol, "primary_status": enum_name(a.primary_status),
            "primary_status_reasons": [enum_name(x) for x in a.primary_status_reasons],
            "final_urls": list(a.ad.final_urls),
            "path1": a.ad.responsive_search_ad.path1,
            "path2": a.ad.responsive_search_ad.path2,
            "headline_count": len(a.ad.responsive_search_ad.headlines),
            "description_count": len(a.ad.responsive_search_ad.descriptions),
            "pinned": [enum_name(h.pinned_field)
                       for h in a.ad.responsive_search_ad.headlines
                       if enum_name(h.pinned_field) not in ("UNSPECIFIED", "UNKNOWN", "")],
            "classification": cls})
    out["ad_children"] = {a: adkids[a] for a in FINAL}

    # ---------- conflicts ----------
    conflicts = []
    for agid, rows in kids.items():
        if ags[agid]["status"] != "PAUSED":
            continue
        for k in rows:
            if k["classification"].startswith("NON-FINAL AND CURRENTLY ENABLED"):
                conflicts.append({
                    "type": "LEGACY KEYWORD WOULD ACTIVATE", "ad_group_id": agid,
                    "ad_group_name": ags[agid]["name"], "criterion_id": k["criterion_id"],
                    "text": k["text"], "match_type": k["match_type"],
                    "detail": "ENABLED inside a PAUSED ad group and NOT in the final "
                              "inventory. It would begin serving the moment the parent "
                              "ad group is enabled."})
    for agid, rows in adkids.items():
        if ags[agid]["status"] != "PAUSED":
            continue
        for a in rows:
            if not a["created_by_launch1"] and a["status"] == "ENABLED":
                conflicts.append({
                    "type": "LEGACY AD WOULD ACTIVATE", "ad_group_id": agid,
                    "ad_group_name": ags[agid]["name"], "ad_id": a["ad_id"],
                    "detail": "ENABLED inside a PAUSED ad group and not created by "
                              "PLAN-GA-LAUNCH-1. It would begin serving on parent enable."})
    out["legacy_activation_conflicts"] = conflicts
    out["broad_match_present"] = [k for rows in kids.values() for k in rows if k["broad_match"]]

    # ---------- final URLs ----------
    urls = {}
    for g, cfg in GROUPS.items():
        u = cfg["page"]
        try:
            rq = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 GM-readonly"})
            with urllib.request.urlopen(rq, timeout=45) as resp:
                body = resp.read().decode("utf-8", "ignore")
                urls[u] = {"status": resp.status, "final_url": resp.url,
                           "https": resp.url.startswith("https://"),
                           "redirected": resp.url.split("?")[0].rstrip("/") != u.rstrip("/"),
                           "has_form": 'id="gform_1"' in body or "gform_1" in body,
                           "has_phone_cta": "6315027946" in body.replace("-", "").replace(
                               " ", "").replace("(", "").replace(")", "") or
                               "502-7946" in body,
                           "ad_group": g}
        except Exception as exc:
            urls[u] = {"status": None, "error": str(exc)[:160], "ad_group": g}
    out["final_urls"] = urls

    # ---------- enable set ----------
    enable = {"ad_groups": [], "keywords": [], "ads": []}
    already = {"ad_groups": [], "keywords": [], "ads": []}
    for agid in FINAL:
        (enable if ags[agid]["status"] == "PAUSED" else already)["ad_groups"].append(
            {"ad_group_id": agid, "name": ags[agid]["name"],
             "final_group": AG2NAME[agid], "current": ags[agid]["status"]})
        for k in kids[agid]:
            if k["negative"]:
                continue
            if k["classification"] == "FINAL - ENABLE" and k["status"] == "PAUSED":
                enable["keywords"].append({"ad_group_id": agid, **k})
            elif k["classification"] == "FINAL - ALREADY ENABLED":
                already["keywords"].append({"ad_group_id": agid, **k})
        for a in adkids[agid]:
            if a["created_by_launch1"] and a["status"] == "PAUSED":
                enable["ads"].append({"ad_group_id": agid, **a})
            elif a["status"] == "ENABLED":
                already["ads"].append({"ad_group_id": agid, **a})
    out["enable_set"] = enable
    out["already_enabled"] = already
    out["counts"] = {
        "ad_groups_to_enable": len(enable["ad_groups"]),
        "keywords_to_enable": len(enable["keywords"]),
        "ads_to_enable": len(enable["ads"]),
        "total_mutations": len(enable["ad_groups"]) + len(enable["keywords"]) + len(enable["ads"]),
        "already_enabled_ad_groups": len(already["ad_groups"]),
        "already_enabled_keywords": len(already["keywords"]),
        "already_enabled_ads": len(already["ads"]),
        "legacy_activation_conflicts": len(conflicts),
        "broad_match_keywords": len(out["broad_match_present"]),
    }
    p = SNAP / f"launch3a-read-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

    print(json.dumps({k: out[k] for k in ("identity", "identity_gate_pass", "campaigns",
                                          "target_ad_groups", "counts")},
                     indent=2, default=str))
    print("\n=== NEW RSA POLICY STATUS ===")
    for agid in FINAL:
        for a in adkids[agid]:
            if a["created_by_launch1"]:
                print(f"  {a['ad_id']} ag={agid} {AG2NAME[agid][:24]:24} "
                      f"{a['policy_class']:28} appr={a['approval_status']:16} "
                      f"rev={a['review_status']:16} primary={a['primary_status']} "
                      f"topics={a['policy_topics']}")
    print("\n=== LEGACY ACTIVATION CONFLICTS ===")
    if not conflicts:
        print("  NONE")
    for x in conflicts:
        print("  !!", json.dumps(x))
    print("\n=== FINAL URLS ===")
    for u, v in urls.items():
        print(f"  {v.get('status')} https={v.get('https')} redirect={v.get('redirected')} "
              f"form={v.get('has_form')} phone={v.get('has_phone_cta')}  {u}")
    print("\nWROTE", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
