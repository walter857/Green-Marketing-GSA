#!/usr/bin/env python3
"""Build the consolidated ranked payload for the portfolio MTD report.

Combines the MTD bundles with delivery-day counts and conversion-counting
diagnostics pulled fresh from the API. Read-only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client

OUT = ROOT / "reports" / "portfolio-mtd-2026-08"

load_dotenv_if_available(ROOT / ".env")
client = load_google_ads_client()
svc = client.get_service("GoogleAdsService")


def pct(v):
    return None if v is None else round(v * 100, 1)


def norm(row, label_parts, extra=None):
    cost = row.get("cost_micros", 0) / 1e6
    conv = row.get("conversions", 0.0)
    d = {
        "label": label_parts,
        "cost": round(cost, 2),
        "conv": round(conv, 1),
        "impr": row.get("impressions", 0),
        "clicks": row.get("clicks", 0),
        "ctr": pct(row.get("ctr", 0.0)),
        "cvr": pct(row.get("conversions_from_interactions_rate", 0.0)),
        "cpa": round(cost / conv, 2) if conv else None,
        "absTop": pct(row.get("absolute_top_impression_percentage", 0.0)),
        "absTopIS": pct(row.get("search_absolute_top_impression_share")),
        "lostRank": pct(row.get("search_rank_lost_absolute_top_impression_share")),
        "lostBudget": pct(row.get("search_budget_lost_absolute_top_impression_share")),
        "is": pct(row.get("search_impression_share")),
    }
    if extra:
        d.update(extra)
    return d


def tier(e):
    if e["cost"] > 0 and e["conv"] == 0:
        return 0
    if e["conv"] > 0:
        return 1
    return 2


def rank(rows):
    rows.sort(key=lambda e: (tier(e), -e["cost"] if tier(e) == 0 else -(e["cpa"] or 0)))
    for i, e in enumerate(rows, 1):
        e["rank"] = i
        e["tier"] = tier(e)
    return rows


payload = {"accounts": [], "campaigns": [], "adGroups": [], "ads": [], "keywords": []}

for path in sorted(OUT.glob("*.json")):
    b = json.loads(path.read_text())
    name = b["account"]["name"]
    cid = b["account"]["customer_id"]
    short = name.replace(" - Live", "")

    # delivery days + counted conversion actions, fresh from API
    days = [r.segments.date for r in svc.search(
        customer_id=cid,
        query="SELECT segments.date, metrics.impressions FROM customer "
              "WHERE segments.date DURING THIS_MONTH ORDER BY segments.date")]
    ca = list(svc.search(
        customer_id=cid,
        query="SELECT conversion_action.name, conversion_action.include_in_conversions_metric "
              "FROM conversion_action WHERE conversion_action.status = 'ENABLED'"))
    counted = [r.conversion_action.name for r in ca
               if r.conversion_action.include_in_conversions_metric]

    acct = norm(b.get("account_total") or {}, [name], {
        "cid": cid, "short": short,
        "days": len(days),
        "firstDay": days[0] if days else None,
        "lastDay": days[-1] if days else None,
        "enabledActions": len(ca),
        "countedActions": len(counted),
        "countedNames": counted,
        "campaignsTotal": len(b["campaigns"]),
        "campaignsSpending": len([c for c in b["campaigns"] if c["cost_micros"] > 0]),
        "keywordsTotal": len(b["keywords"]),
    })
    payload["accounts"].append(acct)

    for c in b["campaigns"]:
        payload["campaigns"].append(norm(c, [short, c["campaign"]], {
            "acct": short, "status": c["status"], "channel": c["channel"],
            "budget": round(c["daily_budget"], 2)}))
    for g in b["ad_groups"]:
        if g["impressions"] > 0:
            payload["adGroups"].append(norm(g, [short, g["campaign"], g["ad_group"]],
                                            {"acct": short, "status": g["status"]}))
    for a in b["ads"]:
        if a["impressions"] > 0:
            hl = " / ".join(a["headlines"]) if a["headlines"] else a["ad_type"]
            payload["ads"].append(norm(a, [short, a["ad_group"], hl], {
                "acct": short, "status": a["status"], "type": a["ad_type"],
                "strength": a["ad_strength"]}))
    for k in b["keywords"]:
        if k["impressions"] > 0:
            payload["keywords"].append(norm(k, [short, k["keyword"]], {
                "acct": short, "match": k["match_type"], "status": k["status"],
                "qs": k["qs"], "qsAd": k["qs_ad_relevance"],
                "qsLp": k["qs_lp_exp"], "qsCtr": k["qs_exp_ctr"],
                "campaign": k["campaign"], "adGroup": k["ad_group"]}))

for key in payload:
    rank(payload[key])

t_cost = sum(a["cost"] for a in payload["accounts"])
t_conv = sum(a["conv"] for a in payload["accounts"])
payload["totals"] = {
    "cost": round(t_cost, 2), "conv": round(t_conv, 1),
    "cpa": round(t_cost / t_conv, 2) if t_conv else None,
    "impr": sum(a["impr"] for a in payload["accounts"]),
    "clicks": sum(a["clicks"] for a in payload["accounts"]),
    "accounts": len(payload["accounts"]),
    "period": "2026-08-01 .. 2026-08-27 (THIS_MONTH, account time zone)",
}

(OUT / "payload.json").write_text(json.dumps(payload, indent=1))

print("PAYLOAD SUMMARY")
print(f"  totals: {payload['totals']}")
for key in ["accounts", "campaigns", "adGroups", "ads", "keywords"]:
    rows = payload[key]
    t0 = [r for r in rows if r["tier"] == 0]
    t1 = [r for r in rows if r["tier"] == 1]
    t2 = [r for r in rows if r["tier"] == 2]
    print(f"  {key:10s} n={len(rows):5d}  zero-conv-spend={len(t0):4d} "
          f"(${sum(r['cost'] for r in t0):9,.2f})  converting={len(t1):3d}  no-spend={len(t2):4d}")

print("\nACCOUNT PACING + MEASUREMENT")
for a in payload["accounts"]:
    print(f"  {a['short']:32s} days={a['days']:2d} ({a['firstDay']}..{a['lastDay']}) "
          f"cost=${a['cost']:9,.2f} conv={a['conv']:5.1f} "
          f"counted_actions={a['countedActions']}/{a['enabledActions']} "
          f"camps={a['campaignsSpending']}/{a['campaignsTotal']}")
